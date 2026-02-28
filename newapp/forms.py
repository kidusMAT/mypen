from django import forms
from .models import ContactMessage, AuthorProfile

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter your name', 'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Enter your email', 'class': 'form-input'}),
            'subject': forms.TextInput(attrs={'placeholder': 'Enter subject', 'class': 'form-input'}),
            'message': forms.Textarea(attrs={'placeholder': 'How can we help?', 'rows': 5, 'class': 'form-textarea'}),
        }

class AuthorProfileForm(forms.ModelForm):
    class Meta:
        model = AuthorProfile
        fields = ['pen_name', 'bio', 'profile_picture', 'phone_number']
        widgets = {
            'pen_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Pen Name'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Tell us about yourself...', 'rows': 4}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+999999999'}),
        }

# Add your forms here