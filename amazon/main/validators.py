import re
from django.core.exceptions import ValidationError

class SimplePasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError("The password must be at least 8 characters long.")
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("The password must contain at least one letter.")

        if not re.search(r'\d', password):
            raise ValidationError("The password must contain at least one digit.")

        if re.search(r'[\s.]', password):
            raise ValidationError("The password must not contain spaces or periods.")

    def get_help_text(self):
        return "Minimum 8 characters, 1 letter, 1 digit, no spaces or periods."