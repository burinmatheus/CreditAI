"""
Etapa 3: Avaliação de Risco com Lógica Fuzzy usando scikit-fuzzy
"""
from typing import Dict
import uuid
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib

# Backend Agg evita necessidade de display em ambiente headless
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

from src.domain.entities.credit_request import CustomerProfile
from src.domain.entities.credit_analysis import RiskAssessment, RiskLevel


class RiskFuzzyLogic:
    """Sistema fuzzy para avaliar risco de inadimplência."""

    def __init__(self) -> None:
        self._setup_variables()
        self._setup_rules()
        self._build_system()

    def _setup_variables(self) -> None:
        # Entradas
        self.credit_score = ctrl.Antecedent(np.arange(0, 1001, 1), "credit_score")
        self.income = ctrl.Antecedent(np.arange(0, 50001, 100), "income")
        self.debt_ratio = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "debt_ratio")
        self.employment_time = ctrl.Antecedent(np.arange(0, 121, 1), "employment_time")
        self.inquiries = ctrl.Antecedent(np.arange(0, 21, 1), "inquiries")
        self.limit_ratio = ctrl.Antecedent(np.arange(0, 1.01, 0.01), "limit_ratio")

        # Saída
        self.risk = ctrl.Consequent(np.arange(0, 1.01, 0.01), "risk")

        # Funções de pertinência
        self.credit_score["low"] = fuzz.trapmf(self.credit_score.universe, [0, 0, 450, 550])
        self.credit_score["med"] = fuzz.trimf(self.credit_score.universe, [500, 650, 780])
        self.credit_score["high"] = fuzz.trapmf(self.credit_score.universe, [700, 780, 1000, 1000])

        self.income["low"] = fuzz.trapmf(self.income.universe, [0, 0, 2000, 4000])
        self.income["med"] = fuzz.trimf(self.income.universe, [3000, 7000, 12000])
        self.income["high"] = fuzz.trapmf(self.income.universe, [8000, 15000, 50000, 50000])

        self.debt_ratio["low"] = fuzz.trapmf(self.debt_ratio.universe, [0, 0, 0.2, 0.3])
        self.debt_ratio["med"] = fuzz.trimf(self.debt_ratio.universe, [0.2, 0.4, 0.6])
        self.debt_ratio["high"] = fuzz.trapmf(self.debt_ratio.universe, [0.5, 0.7, 1.0, 1.0])

        self.employment_time["short"] = fuzz.trapmf(self.employment_time.universe, [0, 0, 6, 12])
        self.employment_time["med"] = fuzz.trimf(self.employment_time.universe, [6, 24, 48])
        self.employment_time["long"] = fuzz.trapmf(self.employment_time.universe, [36, 60, 120, 120])

        self.inquiries["few"] = fuzz.trapmf(self.inquiries.universe, [0, 0, 2, 4])
        self.inquiries["many"] = fuzz.trapmf(self.inquiries.universe, [3, 6, 20, 20])

        self.limit_ratio["low"] = fuzz.trapmf(self.limit_ratio.universe, [0, 0, 0.4, 0.6])
        self.limit_ratio["med"] = fuzz.trimf(self.limit_ratio.universe, [0.5, 0.7, 0.85])
        self.limit_ratio["high"] = fuzz.trapmf(self.limit_ratio.universe, [0.8, 0.9, 1.0, 1.0])

        self.risk["low"] = fuzz.trapmf(self.risk.universe, [0.0, 0.0, 0.20, 0.40])
        self.risk["med"] = fuzz.trimf(self.risk.universe, [0.30, 0.55, 0.75])
        self.risk["high"] = fuzz.trapmf(self.risk.universe, [0.65, 0.80, 1.0, 1.0])

    def _setup_rules(self) -> None:
        self.rules = [
            # ========== REGRAS DE BAIXO RISCO ==========
            # Prioridade: credit_score alto ou income alto com condições favoráveis
            ctrl.Rule(self.credit_score["high"] & self.debt_ratio["low"], self.risk["low"]),
            ctrl.Rule(self.credit_score["high"] & self.debt_ratio["med"], self.risk["low"]),
            ctrl.Rule(self.credit_score["high"] & self.inquiries["few"], self.risk["low"]),
            ctrl.Rule(self.income["high"] & self.debt_ratio["low"], self.risk["low"]),
            ctrl.Rule(self.income["high"] & self.inquiries["few"], self.risk["low"]),
            
            # Score médio pode ser baixo risco com boas condições
            ctrl.Rule(self.credit_score["med"] & self.debt_ratio["low"] & self.inquiries["few"], self.risk["low"]),
            ctrl.Rule(self.credit_score["med"] & self.income["high"], self.risk["low"]),

            # ========== REGRAS DE RISCO MÉDIO ==========
            ctrl.Rule(self.credit_score["med"] & self.debt_ratio["med"], self.risk["med"]),
            ctrl.Rule(self.credit_score["high"] & self.debt_ratio["high"], self.risk["med"]),  # Score alto compensa dívidas
            ctrl.Rule(self.credit_score["low"] & self.debt_ratio["low"] & self.income["high"], self.risk["med"]),  # Exceção
            ctrl.Rule(self.income["med"] & self.limit_ratio["med"], self.risk["med"]),
            ctrl.Rule(self.inquiries["many"] & self.debt_ratio["low"], self.risk["med"]),  # Muitas consultas mas sem dívidas

            # ========== REGRAS DE ALTO RISCO ==========
            # Condições críticas que sempre geram alto risco
            ctrl.Rule(self.credit_score["low"] & self.debt_ratio["med"], self.risk["high"]),  # Mais específica
            ctrl.Rule(self.credit_score["low"] & self.inquiries["many"], self.risk["high"]),
            ctrl.Rule(self.debt_ratio["high"] & self.income["low"], self.risk["high"]),
            ctrl.Rule(self.debt_ratio["high"] & self.income["med"], self.risk["high"]),  # Dívidas altas são críticas
            ctrl.Rule(self.income["med"] & self.limit_ratio["high"], self.risk["high"]),  # CORRIGIDO: era med
            ctrl.Rule(self.limit_ratio["high"] & self.employment_time["short"] & self.credit_score["med"], self.risk["high"]),
            ctrl.Rule(self.inquiries["many"] & self.debt_ratio["high"], self.risk["high"]),
        ]

    def _build_system(self) -> None:
        self.control = ctrl.ControlSystem(self.rules)
        self.simulator = ctrl.ControlSystemSimulation(self.control)

    def assess_risk(self, profile: CustomerProfile, approved_limit: float, requested_amount: float) -> RiskAssessment:
        limit_ratio = min(1.0, requested_amount / approved_limit) if approved_limit > 0 else 1.0

        # Preparar entradas
        inputs = {
            "credit_score": float(profile.credit_score),
            "income": float(profile.income),
            "debt_ratio": float(profile.debt_to_income_ratio),
            "employment_time": float(profile.time_at_job_months),
            "inquiries": float(profile.num_credit_inquiries),
            "limit_ratio": float(limit_ratio)
        }
        
        # Log detalhado
        print("  Entradas:")
        for key, value in inputs.items():
            self.simulator.input[key] = value
            print(f"    {key:20s}: {value:10.2f}")
        print(f"    approved_limit     : {approved_limit:10.2f}")
        print(f"    requested_amount   : {requested_amount:10.2f}")
        print("\n")

        self.simulator.compute()
        risk_score = float(self.simulator.output["risk"])

        if risk_score < 0.40:
            risk_level = RiskLevel.LOW
        elif risk_score < 0.70:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH

        fuzzy_memberships: Dict[str, float] = {
            "low": float(fuzz.interp_membership(self.risk.universe, self.risk["low"].mf, risk_score)),
            "med": float(fuzz.interp_membership(self.risk.universe, self.risk["med"].mf, risk_score)),
            "high": float(fuzz.interp_membership(self.risk.universe, self.risk["high"].mf, risk_score)),
        }

        risk_factors = {
            "credit_score": profile.credit_score,
            "income": profile.income,
            "debt_ratio": profile.debt_to_income_ratio,
            "employment_time": profile.time_at_job_months,
            "inquiries": profile.num_credit_inquiries,
            "limit_ratio": limit_ratio,
        }

        main_factors = [k for k, v in fuzzy_memberships.items() if v >= 0.5]
        confidence = max(fuzzy_memberships.values())
        
        print(f"  Risk Score: {risk_score:.4f}")
        print(f"  Risk Level Determination: {risk_level.value.upper()}")

        # Gera gráfico da saída fuzzy com marcação do risk_score
        self._plot_risk_output(risk_score)

        return RiskAssessment(
            risk_level=risk_level,
            risk_score=risk_score,
            risk_factors=risk_factors,
            main_risk_factors=main_factors,
            confidence_score=confidence,
            fuzzy_memberships=fuzzy_memberships,
        )

    def _plot_risk_output(self, risk_score: float) -> None:
        """Plota as curvas de risco e destaca o score calculado; salva na raiz do projeto."""
        fig, ax = plt.subplots(figsize=(6, 4))
        x = self.risk.universe

        ax.plot(x, self.risk["low"].mf, label="Baixo", color="#2ca02c")
        ax.plot(x, self.risk["med"].mf, label="Médio", color="#ff7f0e")
        ax.plot(x, self.risk["high"].mf, label="Alto", color="#d62728")

        ax.axvline(risk_score, color="#1f77b4", linestyle="--", linewidth=2, label=f"Score={risk_score:.3f}")
        ax.set_title("Saída Fuzzy de Risco")
        ax.set_xlabel("Score de Risco")
        ax.set_ylabel("Pertinência")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.05)
        ax.legend(loc="upper right")
        ax.grid(True, linestyle=":", alpha=0.5)

        out_dir = Path("/workspaces/CreditAI/plots")
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = out_dir / f"risk_fuzzy_{uuid.uuid4().hex[:8]}.png"
        fig.tight_layout()
        fig.savefig(filename)
        plt.close(fig)
        print(f"  Gráfico de risco salvo em {filename}")
