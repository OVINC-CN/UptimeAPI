import abc
import traceback
from dataclasses import asdict

from django.db import transaction
from django.utils import timezone

from apps.monitor.constants import OnlineStatus
from apps.monitor.models import MonitorConfig, ServiceStatus, StatusExtra


class BaseHandler:
    """
    base monitor handler
    """

    def __init__(self, monitor_config: MonitorConfig) -> None:
        self.monitor_config = monitor_config
        self.status = OnlineStatus.UNKNOWN
        self.status_msg = ""
        self.duration = None
        self.extra = StatusExtra()

    def run(self) -> None:
        try:
            self.check()
        except Exception as e:  # pylint: disable=W0718
            self.status = OnlineStatus.UNKNOWN
            self.status_msg = str(e)
            self.extra.traceback = traceback.format_exc()
        finally:
            self.save_db()

    @abc.abstractmethod
    def check(self) -> None:
        raise NotImplementedError()

    @transaction.atomic()
    def save_db(self) -> None:
        now = timezone.now()
        ServiceStatus.objects.create(
            service=self.monitor_config.service,
            timestamp=int(now.timestamp()),
            datetime=now,
            status=self.status,
            status_msg=self.status_msg,
            duration=self.duration,
            extra=asdict(self.extra),
        )
        self.monitor_config.refresh_from_db()
        self.monitor_config.last_check_time = max(self.monitor_config.last_check_time, int(now.timestamp()))
        self.monitor_config.save(update_fields=["last_check_time"])
