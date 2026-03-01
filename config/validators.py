from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

# A more permissive validator that allows spaces
custom_username_validators = [
    RegexValidator(
        r'^[\w.@+ -]+$',
        _('Enter a valid username. This value may contain only letters, numbers, spaces and @/./+/-/_ characters.'),
        'invalid'
    ),
]
