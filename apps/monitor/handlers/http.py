import time
import traceback

import httpx
from django.utils.translation import gettext

from apps.monitor.constants import OnlineStatus
from apps.monitor.handlers.base import BaseHandler
from apps.monitor.models import MonitorConfig


class HTTPHandler(BaseHandler):
    """
    check url match given status code
    """

    def __init__(self, monitor_config: MonitorConfig):
        super().__init__(monitor_config)
        self.start_time = None
        self.end_time = None

    def check(self) -> None:
        # request url
        with httpx.Client(event_hooks={"request": [self.log_request], "response": [self.log_response]}) as client:
            try:
                response: httpx.Response = client.request(
                    method=self.monitor_config.http_method,
                    url=self.monitor_config.http_url,
                    headers=self.monitor_config.http_headers,
                    timeout=self.monitor_config.check_timeout,
                    follow_redirects=self.monitor_config.http_follow_redirect,
                )
            except httpx.TimeoutException:
                self.status = OnlineStatus.TIMEOUT
                self.status_msg = gettext("request timeout after %ds") % self.monitor_config.check_timeout
                self.extra.traceback = traceback.format_exc()
                return
        # check status
        if response.status_code == self.monitor_config.http_check_status_code:
            self.status = OnlineStatus.ONLINE
            self.duration = (self.end_time - self.start_time) / 10**6
            return
        self.status = OnlineStatus.OFFLINE
        self.status_msg = gettext("response with status %d") % response.status_code
        self.extra.http_response_header = dict(response.headers)

    def log_request(self, request: httpx.Request):
        self.start_time = time.time_ns()

    def log_response(self, response: httpx.Response):
        self.end_time = time.time_ns()
