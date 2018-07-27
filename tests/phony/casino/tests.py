import json
from typing import Any

from django.test import TestCase
from django.urls import reverse

from slotomania.exceptions import MissingField


class ViewTestCase(TestCase):
    def POST(self, url: str, data: dict) -> Any:
        return self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )

    def test_missing_username(self) -> None:
        url = reverse("api", args=["LoginApp"])
        with self.assertRaises(MissingField):
            self.POST(
                url,
                data={},
            )

    def test_login_success(self) -> None:
        url = reverse("api", args=["LoginApp"])
        response = self.POST(
            url,
            data={
                "username": "abc",
                "password": "abc"
            },
        )
        assert response.status_code == 200
        assert response.data["errors"] == "bad credential"
