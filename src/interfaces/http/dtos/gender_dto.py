from enum import Enum


class GenderDTO(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
