from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r"^\+380\d{9}$",
    message="Phone number must be in the format: '+380XXXXXXXXX'.",
)
