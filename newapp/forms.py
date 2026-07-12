from django import forms
from django.contrib.auth import get_user_model
from allauth.account.forms import LoginForm
from .models import ContactMessage, AuthorProfile

User = get_user_model()


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = 'Username or email'
        self.fields['login'].widget.attrs.update({
            'placeholder': 'Enter your username or email',
            'autocomplete': 'username',
            'class': 'auth-input',
        })
        self.fields['password'].widget.attrs.update({
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
            'class': 'auth-input',
        })
        self.fields['remember'].widget.attrs.update({'class': 'auth-checkbox'})


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
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'your_username',
        }),
        help_text='Letters, digits and @/./+/-/_ only.',
    )

    class Meta:
        model = AuthorProfile
        fields = ['pen_name', 'bio', 'profile_picture', 'phone_number']
        widgets = {
            'pen_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Your Pen Name'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Tell us about yourself...', 'rows': 4}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+999999999'}),
        }

    def __init__(self, *args, **kwargs):
        # Pop the current user so we can exclude them from the uniqueness check
        self.current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Pre-fill the username field with the current username
        if self.current_user:
            self.fields['username'].initial = self.current_user.username

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username__iexact=username)
        if self.current_user:
            qs = qs.exclude(pk=self.current_user.pk)
        if qs.exists():
            raise forms.ValidationError('That username is already taken.')
        return username