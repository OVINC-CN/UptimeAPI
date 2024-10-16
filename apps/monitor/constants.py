from django.utils.translation import gettext_lazy
from ovinc_client.core.models import IntegerChoices, TextChoices


class OnlineStatus(IntegerChoices):
    """
    online status of service
    """

    ONLINE = 0, gettext_lazy("Online")
    OFFLINE = 1, gettext_lazy("Offline")
    TIMEOUT = 2, gettext_lazy("Timeout")


class HTTPMethod(TextChoices):
    """
    http method
    """

    GET = "GET", gettext_lazy("GET")
