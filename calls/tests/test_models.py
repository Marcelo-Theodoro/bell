from copy import copy

from dateutil.parser import parse
from django.test import TestCase

from ..models import Record


class RecordTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = {
            "call_id": "1",
            "source": "11123456789",
            "destination": "1212345678",
            "started_at": parse("2016-02-29T15:00:00Z"),
            "ended_at": parse("2016-02-29T16:00:00Z"),
        }

    def _test_completed(self, data, status_expeceted, status_method="completed"):
        record = Record.objects.create(**data)
        self.assertEqual(getattr(record, status_method), status_expeceted)

    def test_record_completed(self):
        self._test_completed(self.data, True)

    def test_record_without_end(self):
        data = copy(self.data)
        del data["ended_at"]
        self._test_completed(data, False, status_method="end_record_completed")

    def test_record_without_start(self):
        data = copy(self.data)
        del data["started_at"]
        self._test_completed(data, False, status_method="start_record_completed")
