from django import forms
from django.conf import settings
from django.core.mail import send_mail

def should_be_empty(value):
    if value:
        raise forms.ValidationError('Field is not empty')

class ContactForm(forms.Form):
    contact_name = forms.CharField(max_length=80)
    contact_email = forms.EmailField(max_length=50)
    message = forms.CharField(widget=forms.Textarea)
    forcefield = forms.CharField(
        required=False, widget=forms.HiddenInput, label="Leave empty", validators=[should_be_empty]
        )