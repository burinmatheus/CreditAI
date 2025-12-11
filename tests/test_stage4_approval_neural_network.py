import numpy as np
import torch

from src.domain.services.approval_neural_network import ApprovalNeuralNetwork
from src.domain.entities.credit_request import CustomerProfile, Gender, MaritalStatus, EmploymentStatus
from src.domain.entities.credit_analysis import RiskAssessment, RiskLevel


def test_label_from_rules_marks_age_over_75_as_pending():
    ann = ApprovalNeuralNetwork()

    ages = np.array([76, 74])
    scores = np.array([700, 700])
    risk_scores = np.array([0.2, 0.2])
    debt_ratios = np.array([0.2, 0.2])
    limit_ratios = np.array([0.5, 0.5])
    employment = np.array([1.0, 1.0])

    labels = ann._label_from_rules(ages, scores, risk_scores, debt_ratios, limit_ratios, employment)

    assert labels[0] == 1  # age > 75 => pending
    assert labels[1] == 0  # age <= 75 and no other pending/reject triggers => approved


def test_prepare_inputs_clamps_and_normalizes_extremes():
    ann = ApprovalNeuralNetwork()

    profile = CustomerProfile(
        customer_id="CUST-1",
        name="Test User",
        age=120,  # will clamp to 100
        gender=Gender.MALE,
        marital_status=MaritalStatus.SINGLE,
        income=100_000.0,  # will clamp to 50k
        credit_score=900,
        debt_to_income_ratio=0.4,
        employment_status=EmploymentStatus.UNEMPLOYED,
        time_at_job_months=0,
        has_bank_account=False,
        has_bacen_restriction=False,
        num_credit_inquiries=20,  # will cap to 1.0
        num_existing_loans=10,    # will cap to 1.0
    )

    risk_assessment = RiskAssessment(
        risk_level=RiskLevel.LOW,
        risk_score=0.3,
        risk_factors={},
        main_risk_factors=[],
        confidence_score=0.9,
    )

    inputs = ann._prepare_inputs(
        profile=profile,
        approved_limit=5_000.0,
        requested_amount=100_000.0,
        risk_assessment=risk_assessment,
    )

    arr = inputs.numpy()[0]

    expected_age_norm = (100.0 - 18.0) / (100.0 - 18.0)
    expected_income_norm = 1.0
    expected_limit_ratio = 1.0

    assert torch.isclose(torch.tensor(arr[0]), torch.tensor(expected_age_norm))
    assert torch.isclose(torch.tensor(arr[2]), torch.tensor(expected_income_norm))
    assert torch.isclose(torch.tensor(arr[-1]), torch.tensor(expected_limit_ratio))

    assert arr[4] == 0.0
    assert arr[5] == 0.0
    assert arr[6] == 1.0
    assert arr[7] == 1.0
    assert arr[1] == 0.9
    assert arr[3] == 0.4
    assert arr[8] == 0.3


def test_label_from_rules_rejects_high_risk_and_low_score():
    ann = ApprovalNeuralNetwork()

    ages = np.array([40, 50])
    scores = np.array([700, 400])
    risk_scores = np.array([0.8, 0.2])
    debt_ratios = np.array([0.2, 0.6])
    limit_ratios = np.array([0.5, 0.5])
    employment = np.array([1.0, 1.0])

    labels = ann._label_from_rules(ages, scores, risk_scores, debt_ratios, limit_ratios, employment)

    assert labels[0] == 2
    assert labels[1] == 2


def test_label_from_rules_pending_by_limit_ratio_and_employment():
    ann = ApprovalNeuralNetwork()

    ages = np.array([60, 60])
    scores = np.array([700, 700])
    risk_scores = np.array([0.2, 0.2])
    debt_ratios = np.array([0.2, 0.2])
    limit_ratios = np.array([1.1, 0.5])
    employment = np.array([1.0, 0.0])

    labels = ann._label_from_rules(ages, scores, risk_scores, debt_ratios, limit_ratios, employment)

    assert labels[0] == 1
    assert labels[1] == 1


def test_label_from_rules_pending_by_risk_threshold_only():
    ann = ApprovalNeuralNetwork()

    ages = np.array([50])
    scores = np.array([700])
    risk_scores = np.array([0.5])
    debt_ratios = np.array([0.2])
    limit_ratios = np.array([0.5])
    employment = np.array([1.0])

    labels = ann._label_from_rules(ages, scores, risk_scores, debt_ratios, limit_ratios, employment)

    assert labels[0] == 1


def test_prepare_inputs_handles_nonpositive_approved_limit():
    ann = ApprovalNeuralNetwork()

    profile = CustomerProfile(
        customer_id="CUST-2",
        name="Test User",
        age=30,
        gender=Gender.MALE,
        marital_status=MaritalStatus.SINGLE,
        income=2_000.0,
        credit_score=800,
        debt_to_income_ratio=0.1,
        employment_status=EmploymentStatus.EMPLOYED,
        time_at_job_months=12,
        has_bank_account=True,
        has_bacen_restriction=False,
        num_credit_inquiries=1,
        num_existing_loans=0,
    )

    risk_assessment = RiskAssessment(
        risk_level=RiskLevel.LOW,
        risk_score=0.1,
        risk_factors={},
        main_risk_factors=[],
        confidence_score=0.8,
    )

    inputs = ann._prepare_inputs(
        profile=profile,
        approved_limit=0.0,
        requested_amount=10_000.0,
        risk_assessment=risk_assessment,
    )

    arr = inputs.numpy()[0]
    assert arr[-1] == 1.0


def test_prepare_inputs_clamps_negative_limit_ratio_to_zero():
    ann = ApprovalNeuralNetwork()

    profile = CustomerProfile(
        customer_id="CUST-3",
        name="Test User",
        age=30,
        gender=Gender.MALE,
        marital_status=MaritalStatus.SINGLE,
        income=5_000.0,
        credit_score=750,
        debt_to_income_ratio=0.2,
        employment_status=EmploymentStatus.EMPLOYED,
        time_at_job_months=12,
        has_bank_account=True,
        has_bacen_restriction=False,
        num_credit_inquiries=0,
        num_existing_loans=0,
    )

    risk_assessment = RiskAssessment(
        risk_level=RiskLevel.LOW,
        risk_score=0.1,
        risk_factors={},
        main_risk_factors=[],
        confidence_score=0.8,
    )

    inputs = ann._prepare_inputs(
        profile=profile,
        approved_limit=10_000.0,
        requested_amount=-1_000.0,
        risk_assessment=risk_assessment,
    )

    arr = inputs.numpy()[0]
    assert arr[-1] == 0.0


def test_label_from_rules_clean_approval_path():
    ann = ApprovalNeuralNetwork()

    ages = np.array([35])
    scores = np.array([800])
    risk_scores = np.array([0.2])
    debt_ratios = np.array([0.2])
    limit_ratios = np.array([0.5])
    employment = np.array([1.0])

    labels = ann._label_from_rules(ages, scores, risk_scores, debt_ratios, limit_ratios, employment)

    assert labels[0] == 0


def test_decide_approval_pending_for_age_over_75():
    ann = ApprovalNeuralNetwork()

    profile = CustomerProfile(
        customer_id="CUST-4",
        name="Test User",
        age=80,
        gender=Gender.MALE,
        marital_status=MaritalStatus.SINGLE,
        income=8_000.0,
        credit_score=750,
        debt_to_income_ratio=0.2,
        employment_status=EmploymentStatus.EMPLOYED,
        time_at_job_months=12,
        has_bank_account=True,
        has_bacen_restriction=False,
        num_credit_inquiries=1,
        num_existing_loans=0,
    )

    risk_assessment = RiskAssessment(
        risk_level=RiskLevel.MEDIUM,
        risk_score=0.3,
        risk_factors={},
        main_risk_factors=[],
        confidence_score=0.8,
    )

    status, _, _, probs = ann.decide_approval(
        profile=profile,
        approved_limit=10_000.0,
        requested_amount=9_000.0,
        risk_assessment=risk_assessment,
    )

    assert status.value == "pending_review"
    assert probs["pending"] >= probs["approved"]
