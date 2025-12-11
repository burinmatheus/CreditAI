from src.domain.entities.credit_request import (
    CustomerProfile,
    CreditRequest,
    Gender,
    MaritalStatus,
    EmploymentStatus,
    ProductType,
)
from src.domain.services.persona_filter_dfs import PersonaFilterDFS


def make_profile(**overrides):
    base = dict(
        customer_id="CUST-PERSONA",
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


def make_request(profile: CustomerProfile):
    return CreditRequest(
        customer_profile=profile,
        requested_amount=20_000.0,
        product_type=ProductType.PERSONAL_LOAN,
        requested_installments=24,
    )


def test_persona_filter_assigns_personas_and_confidence():
    svc = PersonaFilterDFS()

    premium_profile = make_profile(age=40, income=15_000.0, credit_score=800, employment_status=EmploymentStatus.EMPLOYED)
    standard_profile = make_profile(age=35, income=5_000.0, credit_score=600, employment_status=EmploymentStatus.EMPLOYED)
    basic_profile = make_profile(age=25, income=500.0, credit_score=350, employment_status=EmploymentStatus.RETIRED)

    premium = svc.identify_persona(make_request(premium_profile))
    standard = svc.identify_persona(make_request(standard_profile))
    basic = svc.identify_persona(make_request(basic_profile))

    assert premium[0] == "premium"
    assert standard[0] == "standard"
    assert basic[0] == "basic"

    for _, conf in [premium, standard, basic]:
        assert 0.0 <= conf <= 1.0
