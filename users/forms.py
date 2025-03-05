from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User

class UserCreationForm(BaseUserCreationForm):
    """
    Form for creating a new user.

    This form extends the BaseUserCreationForm provided by Django to include additional
    fields such as phone number, email address.
    It is used for creating new user accounts.

    Attributes:
        phone (CharField): Field for the user's phone number.
        email (EmailField): Field for the user's email address.
        first_name (CharField): Field for the user's first name.
        middle_name (CharField): Field for the user's middle name.
        last_name (CharField): Field for the user's last name.
        passport_or_id (CharField): Field for the user's ID or passport

    Meta:
        model (User): The User model to which this form is associated.
        fields (tuple): The fields to be included in the form.
    """

    phone = forms.CharField(max_length=20, required=True, help_text='Phone number')
    email = forms.EmailField(required=True, help_text='Email address')
    first_name = forms.CharField(max_length=150, required=True, help_text='First name')
    middle_name = forms.CharField(max_length=150, required=False, help_text='Middle name')
    last_name = forms.CharField(max_length=150, required=True, help_text='Last name')
    passport_or_id = forms.CharField(max_length=150, required=False, help_text='passport or ID number')

    class Meta:
        model = User
        fields = ('email', 'phone', 'first_name', 'middle_name', 'last_name', 'passport_or_id','username', 'avatar', 'password1', 'password2')