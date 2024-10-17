import signal
import time

from django.conf import settings
from django.core.management import BaseCommand
from django.utils import timezone
from ovinc_client.core.logger import logger

from apps.cel.tasks import run_monitor
from apps.monitor.models import MonitorConfig


class Command(BaseCommand):
    """
    command for scheduler
    """

    running = True

    def handle(self, *args, **options):
        self.watch_signal()
        self.schedule()

    def schedule(self):
        while self.running:
            logger.info("[Scheduler] Start")
            now = timezone.now().timestamp()
            sleep_times = [settings.MONITOR_CHECK_MAX_SLEEP_TIME]
            monitor_configs = MonitorConfig.objects.filter(is_enabled=True)
            logger.info("[Scheduler] Configs %s", monitor_configs.count())
            for monitor_config in monitor_configs:
                next_run_time = monitor_config.last_check_time + monitor_config.check_interval
                if next_run_time < now:
                    run_monitor.apply_async(kwargs={"monitor_config_id": monitor_config.id})
                    sleep_times.append(monitor_config.check_interval)
                    logger.info("[Scheduler] Scheduled %s", monitor_config.service.name)
                else:
                    sleep_times.append(next_run_time - now)
                    logger.info("[Scheduler] Ignored %s", monitor_config.service.name)
            sleep_time = round(max(settings.MONITOR_CHECK_MIN_SLEEP_TIME, min(sleep_times)), 3)
            logger.info("[Scheduler] Sleep %s", sleep_time)
            time.sleep(sleep_time)

    def watch_signal(self):
        signal.signal(signal.SIGTERM, self.stop)
        signal.signal(signal.SIGINT, self.stop)

    def stop(self, *args, **kwargs):
        self.running = False
