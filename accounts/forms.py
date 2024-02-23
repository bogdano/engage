""" from django import forms

class UserRegistrationForm(forms.Form):
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    position = forms.CharField(required=False)  # Assuming 'position' is optional
    profile_picture = forms.ImageField(required=False)
    description = forms.CharField(required=False, widget=forms.Textarea) """