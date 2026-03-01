from django.apps import AppConfig


class NewappConfig(AppConfig):
    name = 'newapp'

    def ready(self):
        from django.contrib.auth.models import User
        from django.core.validators import RegexValidator
        
        # This will remove the default restriction and allow spaces
        username_field = User._meta.get_field('username')
        username_field.validators = [
            RegexValidator(
                r'^[\w.@+ -]+$',
                'Enter a valid username. This value may contain only letters, numbers, spaces and @/./+/-/_ characters.',
                'invalid'
            ),
        ]
