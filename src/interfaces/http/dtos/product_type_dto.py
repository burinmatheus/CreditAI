from enum import Enum


class ProductTypeDTO(str, Enum):
    PERSONAL_LOAN = "personal_loan"
    CREDIT_CARD = "credit_card"
    AUTO_LOAN = "auto_loan"
    HOME_LOAN = "home_loan"
