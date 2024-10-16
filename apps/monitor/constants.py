from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy
from ovinc_client.core.models import IntegerChoices, TextChoices


class CheckType(TextChoices):
    """
    check type
    """

    HTTP = "HTTP", gettext_lazy("HTTP")

    @classmethod
    def get_handler(cls, check_type: str):
        match check_type:
            case cls.HTTP:
                return import_string("apps.monitor.handlers.HTTPHandler")
        raise ValueError(f"invalid check type: {check_type}")


class OnlineStatus(IntegerChoices):
    """
    online status of service
    """

    ONLINE = 0, gettext_lazy("Online")
    OFFLINE = 1, gettext_lazy("Offline")
    TIMEOUT = 2, gettext_lazy("Timeout")
    UNKNOWN = 3, gettext_lazy("Unknown")


class HTTPMethod(TextChoices):
    """
    http method
    """

    GET = "GET", gettext_lazy("GET")


class DefaultMonitorConfig:
    """
    default monitor configuration
    """

    CHECK_INTERVAL = 60
    CHECK_TIMEOUT = 10
    CHECK_RETRIES = 3
