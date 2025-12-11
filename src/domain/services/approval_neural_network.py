"""
Etapa 4: Decisão de Aprovação usando Rede Neural (PyTorch)
Inclui treinamento (backprop) com geração de dados sintéticos e salvamento/carregamento de pesos.
"""
import os
from pathlib import Path
from typing import Tuple, List, Dict
import json
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.domain.entities.credit_request import CustomerProfile, EmploymentStatus
from src.domain.entities.credit_analysis import RiskAssessment, ApprovalStatus


class ApprovalMLP(nn.Module):
    """MLP simples 10→16→3 para decisão de aprovação."""

    def __init__(self):
        super().__init__()
        torch.manual_seed(42)  # fixa a semente para reprodutibilidade
        self.fc1 = nn.Linear(10, 16)  # primeira camada: 10 features normalizadas → 16 neurônios
        self.fc2 = nn.Linear(16, 3)   # camada de saída: 3 logits (approved/pending/rejected)
        self._init_weights()  # aplica pesos/bias com heurísticas de negócio

    def _init_weights(self) -> None:
        """Inicializa pesos com heurística de negócio para estabilidade."""
        with torch.no_grad():
            # Heurística alinhada às regras de rotulagem:
            # - Score/income altos favorecem aprovação
            # - Risco alto e dívida alta puxam rejeição
            # - Limite muito próximo/alto ou ausência de emprego sugerem pendência
            w1 = torch.tensor([
                # h0: aprovação por score/income, penaliza dívida/risco/limite
                [0.9, 1.0, 0.8, -1.0, 0.6, 0.4, -0.2, -0.2, -0.8, -0.6],
                # h1: aprovação por emprego e score, penaliza risco
                [0.3, 0.8, 0.2, -0.4, 1.0, 0.3, -0.1, -0.1, -0.7, -0.3],
                # h2: rejeição por risco alto/dívida alta
                [-0.4, -0.6, -0.3, 1.1, -0.6, -0.3, 0.2, 0.2, 1.2, 0.4],
                # h3: rejeição por score baixo e risco
                [-1.0, -0.9, -0.4, 0.4, -0.5, -0.2, 0.1, 0.1, 0.8, 0.2],
                # h4: pendência por limite alto ou sem emprego
                [0.0, -0.2, 0.0, 0.2, -0.8, 0.0, 0.0, 0.0, 0.5, 1.0],
                # h5: pendência por risco moderado
                [0.0, -0.2, 0.0, 0.3, 0.0, 0.0, 0.0, 0.0, 0.7, 0.2],
                # h6: aprovação por banco/emprego
                [0.2, 0.4, 0.2, -0.2, 0.7, 0.5, 0.0, 0.0, -0.3, -0.2],
                # h7: leve penalização por consultas/empréstimos (ruído)
                [0.0, -0.1, 0.0, 0.1, 0.0, 0.0, 0.2, 0.2, 0.2, 0.0],
                # h8-h15: inicialização fraca (quase nula) para permitir ajuste
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ], dtype=torch.float32)
            b1 = torch.tensor([0.1, 0.1, -0.1, -0.1, 0.0, 0.0, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], dtype=torch.float32)
            self.fc1.weight.copy_(w1)
            self.fc1.bias.copy_(b1)

            # Mapear neurônios ocultos para saídas coerentes com as regras
            w2 = torch.tensor([
                # APPROVED: reforça h0, h1, h6; penaliza sinais de risco h2/h3/h4/h5
                [1.0, 0.8, -0.9, -0.8, -0.6, -0.4, 0.5, -0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                # PENDING: reforça h4/h5 (limite alto, risco moderado) e pouco dos demais
                [-0.2, 0.0, 0.2, 0.2, 1.0, 0.8, 0.0, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                # REJECTED: reforça h2/h3 (risco/score baixo) e um pouco de h7
                [-0.8, -0.6, 1.1, 1.0, 0.2, 0.3, -0.4, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            ], dtype=torch.float32)
            b2 = torch.tensor([0.1, 0.0, -0.1], dtype=torch.float32)
            self.fc2.weight.copy_(w2)
            self.fc2.bias.copy_(b2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Aplica camada oculta seguida de ReLU para introduzir não-linearidade sem saturação
        x = F.relu(self.fc1(x))
        # Devolve logits crus; softmax só é aplicado na etapa de inferência/decisão
        return self.fc2(x)


class ApprovalNeuralNetwork:
    """Sistema de decisão de aprovação usando PyTorch."""

    def __init__(self):
        self.model = ApprovalMLP()
        self.model.eval()  # modo avaliação por padrão (inference-first)
        torch.set_grad_enabled(False)  # desabilita grad para evitar custo desnecessário em produção

        self.mlflow_enabled = False  # flag de telemetria/experimentos
        self.mlflow = None
        self.mlflow_experiment = os.getenv("MLFLOW_EXPERIMENT")
        self._init_mlflow()  # tenta configurar MLflow se a URI estiver presente

        # Diretórios para dados e pesos
        self.data_dir = Path("/workspaces/CreditAI/data/training")  # onde salvar datasets sintéticos
        self.model_dir = Path("/workspaces/CreditAI/models")  # onde salvar/carregar pesos
        self.model_path = self.model_dir / "approval_mlp.pt"

        self.data_dir.mkdir(parents=True, exist_ok=True)  # garante pastas
        self.model_dir.mkdir(parents=True, exist_ok=True)

        self._load_weights_if_available()  # carrega pesos treinados, se existirem

    def _init_mlflow(self) -> None:
        """Configura MLflow se disponível; falha silenciosa caso indisponível."""
        try:
            import mlflow

            tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
            if not tracking_uri:
                print("[MLflow] Desabilitado: tracking URI não configurado")
                self.mlflow_enabled = False
                return

            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment(self.mlflow_experiment)
            self.mlflow = mlflow
            self.mlflow_enabled = True
            print(f"[MLflow] Tracking em {tracking_uri} | experimento={self.mlflow_experiment}")
        except Exception as exc:  # pragma: no cover - opcional
            print(f"[MLflow] Desabilitado: {exc}")
            self.mlflow_enabled = False

    def decide_approval(
        self,
        profile: CustomerProfile,
        approved_limit: float,
        requested_amount: float,
        risk_assessment: RiskAssessment,
    ) -> Tuple[ApprovalStatus, float, List[str], dict]:
        inputs = self._prepare_inputs(profile, approved_limit, requested_amount, risk_assessment)
        with torch.no_grad():
            logits = self.model(inputs)  # passa pelo MLP e obtém logits brutos para cada classe
            probs = torch.softmax(logits, dim=1)[0]  # converte logits em probabilidades somando 1

        decision_index = int(torch.argmax(probs).item())  # escolhe a classe com maior prob
        confidence = float(probs[decision_index].item())  # guarda a probabilidade da classe escolhida
        statuses = [
            ApprovalStatus.APPROVED,
            ApprovalStatus.PENDING_REVIEW,
            ApprovalStatus.REJECTED,
        ]
        status = statuses[decision_index]  # mapeia índice para enum de status
        reasons: List[str] = []
        prob_dict = {
            "approved": float(probs[0].item()),
            "pending": float(probs[1].item()),
            "rejected": float(probs[2].item()),
        }
        return status, confidence, reasons, prob_dict

    def generate_dataset_jsonl(self, num_samples: int = 1000, filename: str | None = None) -> Path:
        """Gera dados sintéticos e salva em JSONL para inspeção/treino offline."""
        features, labels = self._generate_synthetic_dataset(num_samples)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        fname = filename or "synthetic_training.jsonl"
        jsonl_path = self.data_dir / fname

        with jsonl_path.open("w", encoding="utf-8") as f:
            for i in range(features.shape[0]):
                row = {"features": features[i].tolist(), "label": int(labels[i].item())}
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

        return jsonl_path

    def train_from_jsonl(
        self,
        jsonl_path: Path,
        epochs: int = 30,
        lr: float = 1e-3,
        batch_size: int = 64,
    ) -> Dict[str, float]:
        """Treina lendo features/labels de um JSONL."""
        records = []  # armazena pares (features, label) lidos linha a linha
        with jsonl_path.open("r", encoding="utf-8") as f:
            for line in f:
                obj = json.loads(line)
            records.append((obj["features"], obj["label"]))  # acumula features e rótulo

        feats = torch.tensor([r[0] for r in records], dtype=torch.float32)  # tensor de entrada
        labs = torch.tensor([r[1] for r in records], dtype=torch.long)  # tensor de rótulos
        dataset = torch.utils.data.TensorDataset(feats, labs)  # dataset PyTorch
        loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=True)  # batches embaralhados

        torch.set_grad_enabled(True)  # habilita autograd (cálculo de gradientes) durante o treino
        self.model.train()  # coloca o modelo em modo treino
        
        # Otimizador e perda:
        # - Adam: descida de gradiente com momentum (1ª média dos gradientes) + escala adaptativa (2ª média das variâncias) e bias correction; 
        #           costuma convergir rápido e é menos sensível ao learning rate.
        # - CrossEntropyLoss: aplica softmax nos logits e calcula entropia cruzada negativa contra o rótulo inteiro (0/1/2), 
        #           penalizando probabilidades baixas na classe correta.
        opt = torch.optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()

        run = None
        if self.mlflow_enabled:
            run = self.mlflow.start_run(run_name=f"train_from_{jsonl_path.name}")
            self.mlflow.log_params({
                "jsonl_path": str(jsonl_path),
                "epochs": epochs,
                "lr": lr,
                "batch_size": batch_size,
                "weight_decay": 1e-4,
                "samples": len(dataset),
                "method": "jsonl",
            })

        for epoch in range(epochs):
            running = 0.0  # acumula perda ponderada pelo tamanho do batch
            for xb, yb in loader:
                opt.zero_grad()  # zera gradientes
                preds = self.model(xb)  # forward
                loss = criterion(preds, yb)  # calcula perda do batch
                loss.backward()  # backprop
                opt.step()  # atualiza pesos
                running += loss.item() * xb.size(0)  # soma perda ponderada pelo batch
            avg_loss = running / len(dataset)  # perda média por amostra
            if epoch % max(1, epochs // 5) == 0:
                print(f"[RNA] (jsonl) epoch {epoch+1}/{epochs} loss={avg_loss:.4f}")  # log parcial
            if self.mlflow_enabled:
                self.mlflow.log_metric("loss", avg_loss, step=epoch + 1)  # registra métrica no MLflow

        torch.save(self.model.state_dict(), self.model_path)  # persiste pesos treinados
        self._load_weights_if_available()  # recarrega para garantir modo eval/CPU
        torch.set_grad_enabled(False)  # desabilita autograd após treino

        if self.mlflow_enabled:
            try:
                self.mlflow.log_metric("final_loss", avg_loss)  # métrica final
                self.mlflow.log_artifact(self.model_path)  # salva pesos no MLflow
                self.mlflow.log_artifact(jsonl_path)  # salva dataset usado
            finally:
                self.mlflow.end_run()
        return {"loss": float(avg_loss), "samples": len(dataset)}

    def _load_weights_if_available(self) -> None:
        """Carrega pesos salvos caso existam."""
        if self.model_path.exists():
            state = torch.load(self.model_path, map_location=torch.device("cpu"))
            self.model.load_state_dict(state)
            self.model.eval()
            torch.set_grad_enabled(False)
            print(f"[RNA] Pesos carregados de {self.model_path}")

    def _generate_synthetic_dataset(self, n: int) -> Tuple[torch.Tensor, torch.Tensor]:
        """Gera dados sintéticos com rótulos baseados em regras de negócio simples."""
        rng = np.random.default_rng()

        ages = rng.integers(18, 101, size=n)
        scores = rng.integers(0, 1000, size=n)
        incomes = rng.uniform(800, 50000, size=n)
        debt_ratios = rng.uniform(0.0, 1.0, size=n)
        employment = rng.choice([0.0, 1.0], size=n, p=[0.2, 0.8])
        bank = rng.choice([0.0, 1.0], size=n, p=[0.1, 0.9])
        inquiries = rng.integers(0, 12, size=n)
        loans = rng.integers(0, 6, size=n)
        risk_scores = rng.uniform(0.0, 1.0, size=n)
        limit_ratios = rng.uniform(0.3, 1.2, size=n)

        age_norm = (ages - 18) / (100 - 18)
        score_norm = scores / 1000.0
        income_norm = np.minimum(1.0, np.log1p(incomes) / np.log1p(50000))
        inquiries_norm = np.minimum(1.0, inquiries / 10.0)
        loans_norm = np.minimum(1.0, loans / 5.0)
        limit_ratio_clamped = np.minimum(1.0, np.maximum(0.0, limit_ratios))

        features = np.stack([
            age_norm,
            score_norm,
            income_norm,
            debt_ratios,
            employment,
            bank,
            inquiries_norm,
            loans_norm,
            risk_scores,
            limit_ratio_clamped,
        ], axis=1).astype(np.float32)

        labels = self._label_from_rules(ages, scores, risk_scores, debt_ratios, limit_ratios, employment)

        return torch.tensor(features, dtype=torch.float32), torch.tensor(labels, dtype=torch.long)

    def _label_from_rules(
        self,
        ages: np.ndarray,
        scores: np.ndarray,
        risk_scores: np.ndarray,
        debt_ratios: np.ndarray,
        limit_ratios: np.ndarray,
        employment: np.ndarray,
    ) -> np.ndarray:
        """Rules → class: 0 approved, 1 pending, 2 rejected."""
        labels = np.zeros_like(scores, dtype=np.int64)

        # Rejection conditions
        reject_mask = (
            (risk_scores > 0.75)
            | (scores < 500)
            | (debt_ratios > 0.55)
        )
        labels[reject_mask] = 2

        # Pending conditions (only if not already rejected)
        pending_mask = (
            (labels == 0)
            & (
                (risk_scores >= 0.45)
                | (limit_ratios > 0.95)
                | (employment == 0.0)
                | (ages > 75)
            )
        )
        labels[pending_mask] = 1

        return labels

    def _prepare_inputs(
        self,
        profile: CustomerProfile,
        approved_limit: float,
        requested_amount: float,
        risk_assessment: RiskAssessment,
    ) -> torch.Tensor:
        age_clamped = min(100.0, max(18.0, float(profile.age)))
        age_norm = (age_clamped - 18.0) / (100.0 - 18.0)

        score_norm = profile.credit_score / 1000.0

        income_clamped = min(50000.0, max(800.0, float(profile.income)))
        income_norm = min(1.0, np.log1p(income_clamped) / np.log1p(50000.0))

        debt_ratio = profile.debt_to_income_ratio
        employment_binary = 1.0 if profile.employment_status in {EmploymentStatus.EMPLOYED, EmploymentStatus.SELF_EMPLOYED} else 0.0
        bank_account_binary = 1.0 if profile.has_bank_account else 0.0
        inquiries_norm = min(1.0, profile.num_credit_inquiries / 10.0)
        loans_norm = min(1.0, profile.num_existing_loans / 5.0)
        risk_score = risk_assessment.risk_score

        raw_limit_ratio = requested_amount / approved_limit if approved_limit > 0 else 1.0
        limit_ratio = min(1.0, max(0.0, raw_limit_ratio))

        arr = np.array([
            age_norm,
            score_norm,
            income_norm,
            debt_ratio,
            employment_binary,
            bank_account_binary,
            inquiries_norm,
            loans_norm,
            risk_score,
            limit_ratio,
        ], dtype=np.float32)
        return torch.tensor(arr).unsqueeze(0)
