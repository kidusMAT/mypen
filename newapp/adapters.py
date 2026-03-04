from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from newapp.models import AuthorProfile

User = get_user_model()

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Ignore existing social accounts, just do this stuff for new ones
        if sociallogin.is_existing:
            return

        # some social logins don't have an email address, e.g. facebook accounts
        # with mobile numbers only, but allauth takes care of this case so just
        # ignore it
        if 'email' not in sociallogin.account.extra_data:
            return

        # check if given email address already exists.
        # Note: __iexact is used to ignore cases
        try:
            email = sociallogin.account.extra_data.get('email').lower()
            user = User.objects.get(email__iexact=email)

            # if it does, connect this new social login to the existing user
            sociallogin.connect(request, user)
        except User.DoesNotExist:
            pass

    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.

        For convenience, we populate several common fields.

        Note that the user instance being populated represents a
        suggested User instance that represents the social account that is
        in the process of being logged in.

        The User instance need not be completely valid and conflict free.
        For example, verifying whether or not the username already exists,
        is not a responsibility.
        """
        user = super().populate_user(request, sociallogin, data)
        # We need to make sure the user has a username that validates against the custom validators
        if not user.username:
            email = data.get('email')
            if email:
                user.username = email.split('@')[0]
            else:
                user.username = data.get('first_name', '') + data.get('last_name', '')

        return user
