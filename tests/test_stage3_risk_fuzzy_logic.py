import numpy as np

from src.domain.entities.credit_request import (
    CustomerProfile,
    CreditRequest,
    Gender,
    MaritalStatus,
    EmploymentStatus,
    ProductType,
)
from src.domain.entities.credit_analysis import RiskLevel
from src.domain.services.risk_fuzzy_logic import RiskFuzzyLogic


def make_profile(**overrides):
    base = dict(
        customer_id="CUST-RISK",
        name="Test User",
        age=35,
        gender=Gender.MALE,
        marital_status=MaritalStatus.SINGLE,
        income=8000.0,
        credit_score=750,
        debt_to_income_ratio=0.25,
        employment_status=EmploymentStatus.EMPLOYED,
        time_at_job_months=24,
        has_bank_account=True,
        has_bacen_restriction=False,
        num_credit_inquiries=1,
        num_existing_loans=0,
    )
    base.update(overrides)
    return CustomerProfile(**base)


def make_request(profile: CustomerProfile, *, amount=20_000.0, installments=24):
    return CreditRequest(
        customer_profile=profile,
        requested_amount=amount,
        product_type=ProductType.PERSONAL_LOAN,
        requested_installments=installments,
    )


def test_risk_fuzzy_logic_low_and_high_risk(monkeypatch):
    svc = RiskFuzzyLogic()
    monkeypatch.setattr(svc, "_plot_risk_output", lambda *_args, **_kwargs: None)

    low_profile = make_profile(
        credit_score=850,
        income=20_000.0,
        debt_to_income_ratio=0.1,
        employment_status=EmploymentStatus.EMPLOYED,
        time_at_job_months=60,
        num_credit_inquiries=0,
        num_existing_loans=1,
    )
    high_profile = make_profile(
        credit_score=300,
        income=1_500.0,
        debt_to_income_ratio=0.9,
        employment_status=EmploymentStatus.UNEMPLOYED,
        time_at_job_months=0,
        num_credit_inquiries=15,
        num_existing_loans=0,
    )

    low_req = make_request(low_profile, amount=10_000.0)
    high_req = make_request(high_profile, amount=5_000.0)

    low_risk = svc.assess_risk(low_profile, approved_limit=50_000.0, requested_amount=low_req.requested_amount)
    high_risk = svc.assess_risk(high_profile, approved_limit=5_000.0, requested_amount=high_req.requested_amount)

    assert low_risk.risk_level == RiskLevel.LOW
    assert high_risk.risk_level == RiskLevel.HIGH

    assert 0.0 <= low_risk.risk_score < 0.7
    assert high_risk.risk_score >= 0.7
