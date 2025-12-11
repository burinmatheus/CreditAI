from src.domain.entities.credit_request import (
    CustomerProfile,
    CreditRequest,
    Gender,
    MaritalStatus,
    EmploymentStatus,
    ProductType,
)
from src.domain.services.persona_filter_dfs import PersonaFilterDFS
from src.domain.services.credit_limit_bfs import CreditLimitBFS


def make_profile(**overrides):
    base = dict(
        customer_id="CUST-LIMIT",
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


def make_request(profile: CustomerProfile, *, product=ProductType.PERSONAL_LOAN, amount=20_000.0, installments=24):
    return CreditRequest(
        customer_profile=profile,
        requested_amount=amount,
        product_type=product,
        requested_installments=installments,
    )


def test_credit_limit_bfs_respects_cap_and_affordability():
    profile = make_profile(income=10_000.0, credit_score=780, debt_to_income_ratio=0.2, employment_status=EmploymentStatus.EMPLOYED)
    req = make_request(profile, amount=30_000.0, installments=36)

    persona_limits = PersonaFilterDFS().get_persona_limits("standard")
    svc = CreditLimitBFS()

    approved, factors = svc.calculate_limit(req, persona_limits)

    assert approved <= factors["search_cap"]
    assert factors["monthly_payment"] <= profile.income * 0.3
    assert approved > 0


def test_credit_limit_bfs_validate_requested_amount():
    profile = make_profile(income=6_000.0, credit_score=650)
    req = make_request(profile, amount=10_000.0, installments=12)
    persona_limits = PersonaFilterDFS().get_persona_limits("basic")
    svc = CreditLimitBFS()

    approved, _ = svc.calculate_limit(req, persona_limits)

    ok, _ = svc.validate_requested_amount(requested_amount=approved, calculated_limit=approved)
    nok, _ = svc.validate_requested_amount(requested_amount=approved + 1_000, calculated_limit=approved)

    assert ok is True
    assert nok is False
