"""
Etapa 4: Decisão de Aprovação usando Rede Neural (PyTorch)
"""
from typing import Tuple, List
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from src.domain.entities.credit_request import CustomerProfile
from src.domain.entities.credit_analysis import RiskAssessment, ApprovalStatus


class ApprovalMLP(nn.Module):
    """MLP simples 10→8→3 para decisão de aprovação."""

    def __init__(self):
        super().__init__()
        torch.manual_seed(42)
        self.fc1 = nn.Linear(10, 8)
        self.fc2 = nn.Linear(8, 3)
        self._init_weights()

    def _init_weights(self) -> None:
        """Inicializa pesos com heurística de negócio para estabilidade."""
        with torch.no_grad():
            # Sensibilidades: score/income positivos, dívida negativa
            w1 = torch.tensor([
                [0.8, 0.7, 0.6, -0.5, 0.4, 0.3, -0.4, -0.3, 0.5, 0.6],
                [-0.6, 0.5, 0.6, -0.8, 0.7, 0.4, -0.6, -0.5, 0.3, 0.4],
                [0.4, 0.6, 0.5, -0.3, 0.8, 0.5, -0.3, -0.2, 0.4, 0.5],
                [-0.7, 0.4, 0.5, -0.7, 0.6, 0.3, -0.8, -0.6, 0.2, 0.3],
                [0.5, 0.6, 0.4, -0.4, 0.5, 0.6, -0.5, -0.4, 0.7, 0.8],
                [0.3, 0.4, 0.5, -0.5, 0.4, 0.3, -0.6, -0.7, 0.3, 0.4],
                [0.7, 0.8, 0.6, -0.4, 0.5, 0.4, -0.3, -0.4, 0.4, 0.5],
                [-0.5, 0.5, 0.4, -0.6, 0.6, 0.5, -0.7, -0.5, 0.3, 0.4],
            ], dtype=torch.float32)
            b1 = torch.tensor([0.1, -0.1, 0.2, -0.2, 0.1, -0.1, 0.2, -0.1], dtype=torch.float32)
            self.fc1.weight.copy_(w1)
            self.fc1.bias.copy_(b1)

            w2 = torch.tensor([
                [0.9, -0.7, 0.6, -0.8, 0.7, -0.5, 0.8, -0.6],  # APPROVED
                [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],      # UNDER_REVIEW
                [-0.8, 0.9, -0.5, 0.9, -0.6, 0.7, -0.7, 0.8],   # REJECTED
            ], dtype=torch.float32)
            b2 = torch.tensor([0.2, 0.0, -0.2], dtype=torch.float32)
            self.fc2.weight.copy_(w2)
            self.fc2.bias.copy_(b2)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = torch.sigmoid(self.fc1(x))
        x = self.fc2(x)
        return F.softmax(x, dim=1)


class ApprovalNeuralNetwork:
    """Sistema de decisão de aprovação usando PyTorch."""

    def __init__(self):
        self.model = ApprovalMLP()
        self.model.eval()

    def decide_approval(
        self,
        profile: CustomerProfile,
        approved_limit: float,
        requested_amount: float,
        risk_assessment: RiskAssessment,
    ) -> Tuple[ApprovalStatus, float, List[str], dict]:
        inputs = self._prepare_inputs(profile, approved_limit, requested_amount, risk_assessment)
        with torch.no_grad():
            probs = self.model(inputs)[0]

        decision_index = int(torch.argmax(probs).item())
        confidence = float(probs[decision_index].item())

        if decision_index == 0:
            status = ApprovalStatus.APPROVED
            reasons = self._get_approval_reasons(profile, risk_assessment, confidence)
        elif decision_index == 1:
            status = ApprovalStatus.PENDING_REVIEW
            reasons = self._get_review_reasons(profile, risk_assessment)
        else:
            status = ApprovalStatus.REJECTED
            reasons = self._get_rejection_reasons(profile, risk_assessment)

        status, reasons = self._apply_business_rules(status, reasons, profile, risk_assessment, confidence)
        prob_dict = {
            "approved": float(probs[0].item()),
            "pending": float(probs[1].item()),
            "rejected": float(probs[2].item()),
        }
        return status, confidence, reasons, prob_dict

    def _prepare_inputs(
        self,
        profile: CustomerProfile,
        approved_limit: float,
        requested_amount: float,
        risk_assessment: RiskAssessment,
    ) -> torch.Tensor:
        age_norm = (profile.age - 18) / (75 - 18)
        score_norm = (profile.credit_score - 300) / (900 - 300)
        income_norm = min(1.0, np.log1p(profile.income) / np.log1p(50000))
        debt_ratio = profile.debt_to_income_ratio
        employment_binary = 1.0 if profile.employment_status in ["employed", "self_employed"] else 0.0
        bank_account_binary = 1.0 if profile.has_bank_account else 0.0
        inquiries_norm = min(1.0, profile.num_credit_inquiries / 10.0)
        loans_norm = min(1.0, profile.num_existing_loans / 5.0)
        risk_score = risk_assessment.risk_score
        limit_ratio = min(1.0, requested_amount / approved_limit) if approved_limit > 0 else 1.0

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

    def _apply_business_rules(
        self,
        status: ApprovalStatus,
        reasons: List[str],
        profile: CustomerProfile,
        risk_assessment: RiskAssessment,
        confidence: float,
    ) -> Tuple[ApprovalStatus, List[str]]:
        if profile.has_bacen_restriction:
            return ApprovalStatus.REJECTED, ["BACEN restriction detected"]

        if risk_assessment.risk_score > 0.85:
            return ApprovalStatus.REJECTED, ["Risk score too high", *reasons]

        if profile.credit_score < 400:
            return ApprovalStatus.REJECTED, ["Credit score below minimum threshold", *reasons]

        if confidence < 0.6 and status == ApprovalStatus.APPROVED:
            return ApprovalStatus.PENDING_REVIEW, ["Low confidence score", *reasons]

        return status, reasons

    def _get_approval_reasons(
        self,
        profile: CustomerProfile,
        risk_assessment: RiskAssessment,
        confidence: float,
    ) -> List[str]:
        reasons: List[str] = []
        if profile.credit_score > 700:
            reasons.append("Excellent credit score")
        if risk_assessment.risk_score < 0.3:
            reasons.append("Low risk assessment")
        if profile.debt_to_income_ratio < 0.3:
            reasons.append("Healthy debt-to-income ratio")
        if profile.time_at_job_months > 24:
            reasons.append("Stable employment history")
        if confidence > 0.8:
            reasons.append("High confidence prediction")
        return reasons if reasons else ["Approved based on overall profile"]

    def _get_review_reasons(
        self,
        profile: CustomerProfile,
        risk_assessment: RiskAssessment,
    ) -> List[str]:
        reasons: List[str] = []
        if 0.4 <= risk_assessment.risk_score <= 0.6:
            reasons.append("Moderate risk level requires review")
        if profile.num_credit_inquiries > 5:
            reasons.append("High number of recent credit inquiries")
        if profile.time_at_job_months < 12:
            reasons.append("Short employment history")
        if 0.3 <= profile.debt_to_income_ratio <= 0.4:
            reasons.append("Borderline debt-to-income ratio")
        return reasons if reasons else ["Manual review recommended"]

    def _get_rejection_reasons(
        self,
        profile: CustomerProfile,
        risk_assessment: RiskAssessment,
    ) -> List[str]:
        reasons: List[str] = []
        if risk_assessment.risk_score > 0.7:
            reasons.append("High default risk")
        if profile.credit_score < 500:
            reasons.append("Insufficient credit score")
        if profile.debt_to_income_ratio > 0.5:
            reasons.append("Excessive debt-to-income ratio")
        if profile.employment_status not in ["employed", "self_employed"]:
            reasons.append("Employment status does not meet requirements")
        if profile.num_credit_inquiries > 8:
            reasons.append("Too many recent credit inquiries")
        return reasons if reasons else ["Does not meet approval criteria"]
