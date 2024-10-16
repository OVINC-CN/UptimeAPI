from ovinc_client.core.logger import celery_logger

from apps.cel import app
from apps.monitor.models import MonitorConfig


@app.task(bind=True)
def run_monitor(self, monitor_config_id: str):
    celery_logger.info("[CheckServiceStatus] Start %s %s", self.request.id, monitor_config_id)
    monitor_config: MonitorConfig = MonitorConfig.objects.filter(id=monitor_config_id).first()
    if not monitor_config:
        celery_logger.error("monitor config with id %s not found", monitor_config_id)
        return
    monitor_config.run()
    celery_logger.info("[CheckServiceStatus] End %s %s", self.request.id, monitor_config_id)
