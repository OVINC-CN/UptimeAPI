from typing import Dict, List, Type, Union

from django.utils.translation import gettext
from ovinc_client.core.models import IntegerChoices, TextChoices


def choices_to_list(choices: Union[Type[TextChoices], Type[IntegerChoices]]) -> List[Dict[str, str]]:
    return [{"value": value, "label": gettext(label)} for value, label in choices.choices]
