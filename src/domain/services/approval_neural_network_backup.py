"""
Etapa 4: Decisão de Aprovação usando Rede Neural Artificial (RNA)
Biblioteca: TensorFlow/Keras
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from typing import Tuple, Optional, Dict
from dataclasses import dataclass
from src.domain.entities.credit_request import CreditRequest
from src.domain.entities.credit_analysis import (
    RiskAssessment, CreditLimit, PersonaFilterResult,
    ApprovalStatus, RejectionReason
)


@dataclass
class ApprovalDecision:
    """Decisão da rede neural"""
    status: ApprovalStatus
    confidence: float
    probabilities: Dict[str, float]
    rejection_reason: Optional[RejectionReason] = None


class CreditApprovalNeuralNetwork:
    """
    Rede Neural para Aprovação de Crédito usando TensorFlow/Keras
    
    Arquitetura MLP (Multi-Layer Perceptron):
    - Input Layer: 10 features normalizadas
    - Hidden Layer 1: 16 neurônios, ativação ReLU, Dropout 0.3
    - Hidden Layer 2: 8 neurônios, ativação ReLU, Dropout 0.2
    - Output Layer: 3 neurônios, ativação Softmax
    
    Classes de saída:
    - 0: APPROVED (Aprovado)
    - 1: REJECTED (Rejeitado)
    - 2: PENDING (Pendente - análise manual)
    
    Features de entrada:
    1. risk_score_normalized (0-1): Score de risco da lógica fuzzy normalizado
    2. credit_score_normalized (0-1): Score de crédito (300-1000) normalizado
    3. debt_ratio (0-1): Razão dívida/renda
    4. late_payments_normalized (0-1): Histórico de atrasos normalizado
    5. approved_vs_requested_ratio (0-1): Limite aprovado / valor solicitado
    6. has_bacen_restrictions (0-1): Possui restrições no BACEN
    7. has_bureau_restrictions (0-1): Possui restrições nos birôs
    8. employment_time_normalized (0-1): Tempo de emprego normalizado
    9. distance_normalized (0-1): Distância da agência normalizada
    10. persona_filter_passed (0-1): Passou no filtro de persona
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Inicializa a rede neural
        
        Args:
            model_path: Caminho para modelo salvo (opcional)
        """
        if model_path:
            self.model = keras.models.load_model(model_path)
        else:
            self.model = self._build_model()
            self._initialize_weights_with_heuristics()
    
    def _build_model(self) -> keras.Model:
        """Constrói a arquitetura da rede neural"""
        model = keras.Sequential([
            # Input layer
            keras.layers.Input(shape=(10,), name='input_features'),
            
            # Hidden layer 1
            keras.layers.Dense(
                16,
                activation='relu',
                kernel_initializer='he_normal',
                name='hidden_layer_1'
            ),
            keras.layers.Dropout(0.3, name='dropout_1'),
            
            # Hidden layer 2
            keras.layers.Dense(
                8,
                activation='relu',
                kernel_initializer='he_normal',
                name='hidden_layer_2'
            ),
            keras.layers.Dropout(0.2, name='dropout_2'),
            
            # Output layer
            keras.layers.Dense(
                3,
                activation='softmax',
                name='output_layer'
            )
        ])
        
        # Compilar modelo
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _initialize_weights_with_heuristics(self):
        """
        Inicializa pesos com valores heurísticos baseados nas regras de negócio
        Simula um treinamento prévio
        """
        # Pesos heurísticos para camada 1 (10 inputs -> 16 neurons)
        # Cada neurônio aprende um padrão específico
        weights1 = np.array([
            # Padrões de aprovação (neurônios 0-7)
            [-0.9,  0.8, -0.7, -0.8,  0.9, -1.0, -0.9,  0.7, -0.4,  0.9],  # Bom perfil geral
            [-0.7,  0.9, -0.6, -0.7,  0.8, -0.9, -0.8,  0.8, -0.3,  0.8],  # Alto score
            [-0.8,  0.7, -0.8, -0.6,  0.9, -1.0, -0.7,  0.6, -0.5,  1.0],  # Passou persona
            [-0.6,  0.6, -0.5, -0.5,  0.7, -0.8, -0.6,  0.9, -0.2,  0.7],  # Emprego estável
            [-0.5,  0.7, -0.7, -0.9,  0.6, -0.7, -0.8,  0.5, -0.6,  0.8],  # Sem atrasos
            [-0.7,  0.8, -0.4, -0.6,  0.8, -0.9, -0.7,  0.6, -0.3,  0.7],  # Baixa dívida
            [-0.6,  0.5, -0.6, -0.7,  0.9, -0.8, -0.6,  0.7, -0.4,  0.9],  # Valor adequado
            [-0.8,  0.9, -0.5, -0.8,  0.7, -1.0, -0.9,  0.8, -0.2,  0.8],  # Sem restrições
            
            # Padrões de rejeição (neurônios 8-11)
            [ 0.9, -0.8,  0.7,  0.9, -0.6,  1.0,  0.9, -0.5,  0.4, -0.9],  # Alto risco
            [ 0.8, -0.9,  0.6,  0.8, -0.7,  0.9,  1.0, -0.6,  0.3, -0.8],  # Restrições
            [ 0.7, -0.7,  0.8,  0.7, -0.8,  0.8,  0.8, -0.7,  0.5, -0.7],  # Muitos atrasos
            [ 0.6, -0.6,  0.9,  0.6, -0.5,  0.7,  0.7, -0.8,  0.6, -0.6],  # Alta dívida
            
            # Padrões de pendência (neurônios 12-15)
            [-0.3,  0.3, -0.3, -0.4,  0.4, -0.5, -0.4,  0.3, -0.2,  0.4],  # Caso limítrofe 1
            [-0.4,  0.4, -0.4, -0.3,  0.5, -0.4, -0.5,  0.4, -0.3,  0.3],  # Caso limítrofe 2
            [-0.2,  0.2, -0.5, -0.5,  0.3, -0.6, -0.3,  0.2, -0.4,  0.5],  # Score médio
            [-0.5,  0.5, -0.2, -0.2,  0.6, -0.3, -0.6,  0.5, -0.1,  0.2],  # Análise necessária
        ])
        
        bias1 = np.array([0.1] * 8 + [-0.3] * 4 + [0.0] * 4)
        
        # Pesos heurísticos para camada 2 (16 neurons -> 8 neurons)
        weights2 = np.random.randn(8, 16) * 0.1
        bias2 = np.zeros(8)
        
        # Pesos heurísticos para camada de saída (8 neurons -> 3 outputs)
        weights3 = np.array([
            # APPROVED, REJECTED, PENDING
            [ 0.9, -0.7,  0.3],  # Neurônio 0 favorece aprovação
            [ 0.8, -0.6,  0.2],  # Neurônio 1 favorece aprovação
            [ 0.7, -0.8,  0.4],  # Neurônio 2 favorece aprovação
            [ 0.6, -0.5,  0.5],  # Neurônio 3 moderado
            [-0.7,  0.9, -0.3],  # Neurônio 4 favorece rejeição
            [-0.6,  0.8, -0.2],  # Neurônio 5 favorece rejeição
            [ 0.2, -0.2,  0.8],  # Neurônio 6 favorece pendência
            [ 0.3, -0.3,  0.7],  # Neurônio 7 favorece pendência
        ]).T
        
        bias3 = np.array([0.3, -0.3, 0.0])
        
        # Aplicar pesos ao modelo
        self.model.layers[1].set_weights([weights1.T, bias1])
        self.model.layers[3].set_weights([weights2.T, bias2])
        self.model.layers[5].set_weights([weights3, bias3])
    
    def predict(self, features: np.ndarray) -> Tuple[int, float, Dict[str, float]]:
        """
        Faz predição usando a rede neural
        
        Args:
            features: Array numpy com 10 features normalizadas
            
        Returns:
            tuple[predicted_class, confidence, probabilities]:
                - predicted_class: 0=APPROVED, 1=REJECTED, 2=PENDING
                - confidence: Probabilidade da classe predita
                - probabilities: Dict com probabilidades de cada classe
        """
        # Reshape para batch
        features_batch = features.reshape(1, -1)
        
        # Predição (modo de inferência, sem dropout)
        predictions = self.model.predict(features_batch, verbose=0)[0]
        
        # Classe predita
        predicted_class = int(np.argmax(predictions))
        confidence = float(predictions[predicted_class])
        
        probabilities = {
            'approved': float(predictions[0]),
            'rejected': float(predictions[1]),
            'pending': float(predictions[2])
        }
        
        return predicted_class, confidence, probabilities
    
    def train_on_synthetic_data(self, num_samples: int = 1000):
        """
        Treina a rede com dados sintéticos gerados a partir de regras de negócio
        
        Args:
            num_samples: Número de amostras sintéticas
        """
        X_train = []
        y_train = []
        
        for _ in range(num_samples):
            # Gera features aleatórias
            features = np.random.rand(10)
            
            # Aplica regras de negócio para gerar label
            label = self._generate_label_from_rules(features)
            
            X_train.append(features)
            y_train.append(label)
        
        X_train = np.array(X_train)
        y_train = keras.utils.to_categorical(y_train, 3)
        
        # Treina
        self.model.fit(
            X_train,
            y_train,
            epochs=50,
            batch_size=32,
            validation_split=0.2,
            verbose=0
        )
    
    def _generate_label_from_rules(self, features: np.ndarray) -> int:
        """Gera label baseado em regras de negócio"""
        risk = features[0]
        credit_score = features[1]
        bacen = features[5]
        bureau = features[6]
        persona = features[9]
        
        # Regras de rejeição
        if bacen > 0.5 or bureau > 0.5:
            return 1  # REJECTED
        if persona < 0.5:
            return 1  # REJECTED
        if risk > 0.7 and credit_score < 0.5:
            return 1  # REJECTED
        
        # Regras de aprovação
        if risk < 0.3 and credit_score > 0.7:
            return 0  # APPROVED
        if risk < 0.5 and credit_score > 0.6 and bacen == 0 and bureau == 0:
            return 0  # APPROVED
        
        # Casos limítrofes
        return 2  # PENDING
    
    def save_model(self, path: str):
        """Salva o modelo treinado"""
        self.model.save(path)


class ApprovalNeuralNetwork:
    """
    Sistema de aprovação usando Rede Neural
    Orquestra a preparação de features e decisão final
    """
    
    def __init__(self, model_path: Optional[str] = None):
        self.neural_network = CreditApprovalNeuralNetwork(model_path)
    
    def _prepare_features(self,
                         credit_request: CreditRequest,
                         persona_result: PersonaFilterResult,
                         credit_limit: Optional[CreditLimit],
                         risk_assessment: Optional[RiskAssessment]) -> np.ndarray:
        """
        Prepara features normalizadas para a rede neural
        
        Returns:
            Array numpy com 10 features (0-1)
        """
        profile = credit_request.customer_profile
        
        # Feature 1: Risk score normalizado (0-10 -> 0-1)
        if risk_assessment and hasattr(risk_assessment, 'risk_score'):
            risk_score = min(1.0, risk_assessment.risk_score / 10.0)
        else:
            risk_score = 0.5
        
        # Feature 2: Credit score normalizado (300-1000 -> 0-1)
        credit_score_norm = (profile.credit_score - 300) / 700
        credit_score_norm = max(0.0, min(1.0, credit_score_norm))
        
        # Feature 3: Debt ratio (0-1)
        debt_ratio = min(1.0, profile.debt_to_income_ratio())
        
        # Feature 4: Late payments normalizado (0-10 -> 0-1)
        late_payments_norm = min(1.0, profile.late_payments_count / 10)
        
        # Feature 5: Razão valor aprovado / solicitado
        if credit_limit and credit_limit.approved_amount > 0:
            amount_ratio = min(1.0, credit_limit.approved_amount / credit_request.requested_amount)
        else:
            amount_ratio = 0.0
        
        # Feature 6: Restrições BACEN
        bacen = 1.0 if profile.has_bacen_restrictions else 0.0
        
        # Feature 7: Restrições Bureau
        bureau = 1.0 if profile.has_bureau_restrictions else 0.0
        
        # Feature 8: Tempo de emprego normalizado (0-60 meses -> 0-1)
        employment_norm = min(1.0, (profile.employment_time_months or 0) / 60)
        
        # Feature 9: Distância normalizada (0-100km -> 0-1)
        distance_norm = min(1.0, (profile.distance_from_rs_km or 0) / 100)
        
        # Feature 10: Passou no filtro de persona
        persona_passed = 0.0 if persona_result.should_reject else 1.0
        
        return np.array([
            risk_score,
            credit_score_norm,
            debt_ratio,
            late_payments_norm,
            amount_ratio,
            bacen,
            bureau,
            employment_norm,
            distance_norm,
            persona_passed
        ])
    
    def _apply_business_rules(self,
                             credit_request: CreditRequest,
                             persona_result: PersonaFilterResult,
                             credit_limit: Optional[CreditLimit]) -> Optional[ApprovalDecision]:
        """
        Aplica regras de negócio duras que bypassam a rede neural
        
        Returns:
            ApprovalDecision se deve ser decidido por regra, None caso contrário
        """
        profile = credit_request.customer_profile
        
        # Regra 1: Reprovado no filtro de persona
        if persona_result.should_reject:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                probabilities={'approved': 0.0, 'rejected': 1.0, 'pending': 0.0},
                rejection_reason=RejectionReason.PERSONA_FILTER
            )
        
        # Regra 2: Restrições BACEN
        if profile.has_bacen_restrictions:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                probabilities={'approved': 0.0, 'rejected': 1.0, 'pending': 0.0},
                rejection_reason=RejectionReason.BACEN_RESTRICTIONS
            )
        
        # Regra 3: Limite insuficiente
        if not credit_limit or credit_limit.approved_amount == 0:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                probabilities={'approved': 0.0, 'rejected': 1.0, 'pending': 0.0},
                rejection_reason=RejectionReason.INSUFFICIENT_INCOME
            )
        
        # Regra 4: Score muito baixo
        if profile.credit_score < 300:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                probabilities={'approved': 0.0, 'rejected': 1.0, 'pending': 0.0},
                rejection_reason=RejectionReason.LOW_CREDIT_SCORE
            )
        
        return None  # Deixa rede neural decidir
    
    def evaluate(self,
                credit_request: CreditRequest,
                persona_result: PersonaFilterResult,
                credit_limit: Optional[CreditLimit],
                risk_assessment: Optional[RiskAssessment]) -> ApprovalDecision:
        """
        Avalia solicitação e retorna decisão final
        
        Args:
            credit_request: Solicitação de crédito
            persona_result: Resultado do filtro de persona (Etapa 1)
            credit_limit: Limite calculado (Etapa 2)
            risk_assessment: Avaliação de risco (Etapa 3)
            
        Returns:
            ApprovalDecision com status, confiança e probabilidades
        """
        # Aplica regras de negócio primeiro
        business_decision = self._apply_business_rules(
            credit_request, persona_result, credit_limit
        )
        
        if business_decision:
            return business_decision
        
        # Prepara features
        features = self._prepare_features(
            credit_request, persona_result, credit_limit, risk_assessment
        )
        
        # Predição da rede neural
        predicted_class, confidence, probabilities = self.neural_network.predict(features)
        
        # Mapeia classe para status
        status_map = {
            0: ApprovalStatus.APPROVED,
            1: ApprovalStatus.REJECTED,
            2: ApprovalStatus.PENDING
        }
        
        status = status_map[predicted_class]
        
        # Se confiança muito baixa (<60%), marca como pendente
        if confidence < 0.60 and status != ApprovalStatus.PENDING:
            status = ApprovalStatus.PENDING
        
        # Define rejection_reason se rejeitado
        rejection_reason = None
        if status == ApprovalStatus.REJECTED:
            rejection_reason = RejectionReason.NEURAL_NETWORK_DECISION
        
        return ApprovalDecision(
            status=status,
            confidence=confidence,
            probabilities=probabilities,
            rejection_reason=rejection_reason
        )

    """
    Rede Neural Simples (MLP - Multilayer Perceptron)
    Arquitetura: 10 entradas -> 8 neurônios camada oculta -> 3 saídas
    
    Entradas (10 features):
    1. risk_score (0-1)
    2. credit_score_normalized (0-1)
    3. debt_ratio (0-1)
    4. late_payments_normalized (0-1)
    5. approved_amount_ratio (valor_aprovado / valor_solicitado)
    6. has_bacen_restrictions (0 ou 1)
    7. has_bureau_restrictions (0 ou 1)
    8. employment_time_normalized (0-1)
    9. distance_normalized (0-1)
    10. persona_filter_passed (0 ou 1)
    
    Saídas (3 neurônios):
    - Índice 0: APPROVED
    - Índice 1: REJECTED
    - Índice 2: PENDING
    """
    
    def __init__(self):
        # Inicializa pesos com valores heurísticos baseados em regras de negócio
        # Isso simula um treinamento prévio
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Inicializa pesos da rede com valores heurísticos"""
        np.random.seed(42)  # Para reprodutibilidade
        
        # Camada 1: 10 entradas -> 8 neurônios ocultos
        # Pesos favoráveis para aprovação
        self.weights1 = np.array([
            # risk, score, debt, late, amount, bacen, bureau, emp, dist, persona
            [-0.8,  0.7, -0.6, -0.5,  0.8, -0.9, -0.7,  0.6, -0.3,  0.9],  # Neurônio 1
            [-0.7,  0.8, -0.7, -0.6,  0.7, -0.8, -0.8,  0.5, -0.4,  0.8],  # Neurônio 2
            [-0.9,  0.6, -0.5, -0.7,  0.9, -1.0, -0.6,  0.7, -0.2,  1.0],  # Neurônio 3
            [ 0.5, -0.5,  0.6,  0.7, -0.4,  0.8,  0.7, -0.5,  0.3, -0.6],  # Neurônio 4 (para rejeição)
            [ 0.6, -0.6,  0.7,  0.8, -0.5,  0.9,  0.8, -0.6,  0.4, -0.7],  # Neurônio 5 (para rejeição)
            [-0.4,  0.4, -0.3, -0.4,  0.5, -0.5, -0.5,  0.3, -0.2,  0.5],  # Neurônio 6 (para pending)
            [-0.3,  0.3, -0.4, -0.3,  0.4, -0.4, -0.4,  0.4, -0.3,  0.4],  # Neurônio 7 (para pending)
            [-0.5,  0.5, -0.5, -0.5,  0.6, -0.6, -0.6,  0.5, -0.3,  0.6],  # Neurônio 8
        ])
        
        self.bias1 = np.array([0.1, 0.2, 0.15, -0.3, -0.4, 0.0, 0.05, 0.1])
        
        # Camada 2: 8 neurônios ocultos -> 3 saídas
        self.weights2 = np.array([
            [ 0.8,  0.9,  0.7, -0.6, -0.7,  0.3,  0.2,  0.5],  # APPROVED
            [-0.7, -0.8, -0.6,  0.8,  0.9, -0.2, -0.3, -0.4],  # REJECTED
            [ 0.2,  0.1,  0.3, -0.1, -0.2,  0.6,  0.7,  0.4],  # PENDING
        ])
        
        self.bias2 = np.array([0.5, -0.5, 0.0])
    
    def _sigmoid(self, x: np.ndarray) -> np.ndarray:
        """Função de ativação sigmoid"""
        return 1 / (1 + np.exp(-np.clip(x, -500, 500)))
    
    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Função softmax para saída multiclasse"""
        exp_x = np.exp(x - np.max(x))  # Previne overflow
        return exp_x / exp_x.sum()
    
    def _forward(self, inputs: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Forward propagation"""
        # Camada oculta
        hidden = self._sigmoid(np.dot(inputs, self.weights1.T) + self.bias1)
        
        # Camada de saída
        output = np.dot(hidden, self.weights2.T) + self.bias2
        output_probs = self._softmax(output)
        
        return hidden, output_probs
    
    def predict(self, inputs: np.ndarray) -> Tuple[int, float]:
        """
        Faz predição
        
        Returns:
            (classe_predita, confiança)
            classe: 0=APPROVED, 1=REJECTED, 2=PENDING
        """
        _, output_probs = self._forward(inputs)
        predicted_class = np.argmax(output_probs)
        confidence = output_probs[predicted_class]
        return int(predicted_class), float(confidence)


class ApprovalNeuralNetwork:
    """
    Sistema de aprovação usando Rede Neural
    Combina resultados das etapas anteriores para decisão final
    """
    
    def __init__(self):
        self.neural_network = SimpleNeuralNetwork()
    
    def _prepare_features(self, 
                         credit_request: CreditRequest,
                         persona_result: PersonaFilterResult,
                         credit_limit: Optional[CreditLimit],
                         risk_assessment: Optional[RiskAssessment]) -> np.ndarray:
        """
        Prepara features para entrada da rede neural
        
        Returns:
            Array numpy com 10 features normalizadas
        """
        profile = credit_request.customer_profile
        
        # Feature 1: Risk score (0-1)
        risk_score = risk_assessment.risk_score if risk_assessment else 0.5
        
        # Feature 2: Credit score normalizado (300-1000 -> 0-1)
        credit_score_norm = (profile.credit_score - 300) / 700
        
        # Feature 3: Debt ratio (0-1)
        debt_ratio = min(1.0, profile.debt_to_income_ratio())
        
        # Feature 4: Late payments normalizado (0-10 -> 0-1)
        late_payments_norm = min(1.0, profile.late_payments_count / 10)
        
        # Feature 5: Razão valor aprovado / solicitado
        if credit_limit and credit_limit.approved_amount > 0:
            amount_ratio = min(1.0, credit_limit.approved_amount / credit_request.requested_amount)
        else:
            amount_ratio = 0.0
        
        # Feature 6: Restrições BACEN (0 ou 1)
        bacen = 1.0 if profile.has_bacen_restrictions else 0.0
        
        # Feature 7: Restrições Bureau (0 ou 1)
        bureau = 1.0 if profile.has_bureau_restrictions else 0.0
        
        # Feature 8: Tempo de emprego normalizado (0-60 meses -> 0-1)
        employment_norm = min(1.0, profile.employment_time_months / 60)
        
        # Feature 9: Distância normalizada (0-50km -> 0-1)
        distance_norm = min(1.0, profile.distance_from_branch_km / 50)
        
        # Feature 10: Passou no filtro de persona (0 ou 1)
        persona_passed = 0.0 if persona_result.should_reject else 1.0
        
        return np.array([
            risk_score,
            credit_score_norm,
            debt_ratio,
            late_payments_norm,
            amount_ratio,
            bacen,
            bureau,
            employment_norm,
            distance_norm,
            persona_passed
        ])
    
    def _apply_business_rules(self, 
                             credit_request: CreditRequest,
                             persona_result: PersonaFilterResult,
                             credit_limit: Optional[CreditLimit],
                             risk_assessment: Optional[RiskAssessment]) -> Optional[ApprovalDecision]:
        """
        Aplica regras de negócio duras (bypassa rede neural se necessário)
        
        Returns:
            ApprovalDecision se deve ser decidido por regra, None caso contrário
        """
        profile = credit_request.customer_profile
        
        # Regra 1: Se reprovado no filtro de persona, rejeita imediatamente
        if persona_result.should_reject:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                rejection_reason=RejectionReason.PERSONA_FILTER
            )
        
        # Regra 2: Se tem restrições BACEN, rejeita
        if profile.has_bacen_restrictions:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                rejection_reason=RejectionReason.BACEN_RESTRICTIONS
            )
        
        # Regra 3: Se não tem limite de crédito aprovado, rejeita
        if not credit_limit or credit_limit.approved_amount == 0:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                rejection_reason=RejectionReason.INSUFFICIENT_INCOME
            )
        
        # Regra 4: Se limite é insuficiente para valor solicitado
        if not credit_limit.is_sufficient_for_request(credit_request.requested_amount):
            # Pode ser aprovado com valor menor ou pendente
            return None  # Deixa rede neural decidir
        
        # Regra 5: Score muito baixo (<300) - já deveria ser pego pelo filtro, mas garante
        if profile.credit_score < 300:
            return ApprovalDecision(
                status=ApprovalStatus.REJECTED,
                confidence=1.0,
                rejection_reason=RejectionReason.LOW_CREDIT_SCORE
            )
        
        return None  # Deixa rede neural decidir
    
    def evaluate(self,
                credit_request: CreditRequest,
                persona_result: PersonaFilterResult,
                credit_limit: Optional[CreditLimit],
                risk_assessment: Optional[RiskAssessment]) -> ApprovalDecision:
        """
        Avalia solicitação de crédito e retorna decisão final
        
        Args:
            credit_request: Solicitação de crédito
            persona_result: Resultado do filtro de persona
            credit_limit: Limite de crédito calculado
            risk_assessment: Avaliação de risco
            
        Returns:
            ApprovalDecision com status e confiança
        """
        # Aplica regras de negócio primeiro
        business_decision = self._apply_business_rules(
            credit_request, persona_result, credit_limit, risk_assessment
        )
        
        if business_decision:
            return business_decision
        
        # Prepara features para rede neural
        features = self._prepare_features(
            credit_request, persona_result, credit_limit, risk_assessment
        )
        
        # Predição da rede neural
        predicted_class, confidence = self.neural_network.predict(features)
        
        # Mapeia classe para status
        if predicted_class == 0:
            status = ApprovalStatus.APPROVED
            rejection_reason = None
        elif predicted_class == 1:
            status = ApprovalStatus.REJECTED
            rejection_reason = RejectionReason.NEURAL_NETWORK_DECISION
        else:  # predicted_class == 2
            status = ApprovalStatus.PENDING
            rejection_reason = None
        
        # Ajusta decisão baseada em confiança
        # Se confiança baixa, marca como pendente para análise manual
        if confidence < 0.60 and status != ApprovalStatus.PENDING:
            status = ApprovalStatus.PENDING
            rejection_reason = None
        
        return ApprovalDecision(
            status=status,
            confidence=confidence,
            rejection_reason=rejection_reason
        )
