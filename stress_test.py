"""
Locust 壓力測試 — 重機車隊報名系統

執行方式：
  pip install locust
  locust -f stress_test.py --host=https://motorcycle-registration.onrender.com

或無頭模式（終端機報告）：
  locust -f stress_test.py --host=https://motorcycle-registration.onrender.com \
    --headless -u 50 -r 10 --run-time 60s --csv=stress_result
"""
from locust import HttpUser, task, between, constant
import random


class BrowseUser(HttpUser):
    """一般瀏覽行為 — 查看頁面不需登入"""
    wait_time = between(2, 6)

    @task(5)
    def view_home(self):
        self.client.get("/")

    @task(5)
    def view_login(self):
        self.client.get("/login")

    @task(5)
    def view_events(self):
        self.client.get("/events")

    @task(3)
    def view_register(self):
        self.client.get("/register")

    @task(3)
    def view_event_detail(self):
        self.client.get("/events/1")

    @task(1)
    def view_calendar(self):
        self.client.get("/events/calendar")


class RegisteredUser(HttpUser):
    """已登入使用者行為 — 瀏覽 + 報名/取消"""
    wait_time = between(3, 8)

    def on_start(self):
        """登入測試帳號"""
        resp = self.client.get("/login")
        csrf = self._extract_csrf(resp.text)
        if csrf:
            self.client.post(
                "/login",
                data={"csrf_token": csrf, "username": "test01", "password": "test1234"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    @staticmethod
    def _extract_csrf(html):
        import re
        m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
        return m.group(1) if m else None

    @task(3)
    def view_dashboard(self):
        self.client.get("/dashboard")

    @task(3)
    def view_events(self):
        self.client.get("/events")

    @task(2)
    def view_event_detail(self):
        self.client.get("/events/1")

    @task(1)
    def view_my_registrations(self):
        self.client.get("/my/registrations")

    @task(1)
    def view_settings(self):
        self.client.get("/my/settings")

    @task(1)
    def view_members(self):
        self.client.get("/members")


class AdminUser(HttpUser):
    """管理員行為 — 管理後台操作"""
    wait_time = between(4, 10)

    def on_start(self):
        resp = self.client.get("/login")
        csrf = self._extract_csrf(resp.text)
        if csrf:
            self.client.post(
                "/login",
                data={"csrf_token": csrf, "username": "admin", "password": "admin123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

    @staticmethod
    def _extract_csrf(html):
        import re
        m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
        return m.group(1) if m else None

    @task(3)
    def admin_dashboard(self):
        self.client.get("/admin")

    @task(2)
    def admin_events(self):
        self.client.get("/admin/events")

    @task(1)
    def admin_messages(self):
        self.client.get("/admin/messages")

    @task(1)
    def admin_bulletin(self):
        self.client.get("/admin/bulletin")
