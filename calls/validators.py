from django.core.validators import RegexValidator

PhoneNumberValidator = RegexValidator(
    regex=r"^\d{10,11}$", message="Invalid phone number"
)
