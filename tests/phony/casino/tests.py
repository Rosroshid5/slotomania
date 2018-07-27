import json

from django.test import TestCase
from django.urls import reverse

from slotomania.exceptions import MissingField


class ViewTestCase(TestCase):
    def test_view(self) -> None:
        url = reverse("api", args=["LoginApp"])
        with self.assertRaises(MissingField):
            response = self.client.post(
                url,
                data=json.dumps({}),
                content_type="application/json",
            )
