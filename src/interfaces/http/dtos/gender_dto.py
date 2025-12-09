from enum import Enum


class GenderDTO(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"
