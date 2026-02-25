from django import forms
from .models import ContactMessage

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

# Add your forms here