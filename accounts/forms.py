from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            self.fields['password1'].help_text = ''
            self.fields['password2'].help_text = ''

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "bio", "password1", "password2"]