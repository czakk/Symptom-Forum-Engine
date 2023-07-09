from django import forms
from django.contrib.auth.models import User


class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password',
                               widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password',
                               widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_confirm_password(self):
        cd = self.cleaned_data
        if cd['password'] != cd['confirm_password']:
            raise forms.ValidationError('Password don\'t match')
        return cd['confirm_password']

    def clean_email(self):
        cd = self.cleaned_data
        if User.objects.filter(email=cd['email']).exists():
            raise forms.ValidationError('Email is already used')
        return cd['email']