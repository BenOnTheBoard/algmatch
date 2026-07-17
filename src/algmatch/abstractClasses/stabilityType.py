from enum import Enum

class StabilityType(Enum):
    STRONG = "strong"
    SUPER = "super"
    WEAK = "weak"

    @classmethod
    def from_value(cls, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Expected stability type to be str: {value}")
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        raise ValueError("Stability type ttype must be 'super', 'strong', or 'weak'")