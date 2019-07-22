class PhoneNumberConverter:
    regex = r"\d?\d{10}"

    def to_python(self, value):
        return str(value)

    def to_url(self, value):
        return str(value)
