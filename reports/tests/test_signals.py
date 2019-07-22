from copy import copy
from unittest import mock

from calls.models import Record
from dateutil.parser import parse
from django.test import TestCase


class SignalTestCase(TestCase):
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

    @mock.patch("reports.models.Report.save")
    def test_create_report_record_completed(self, mocked_save_report):
        record = Record(**self.data)
        record.save()
        mocked_save_report.assert_called_with()

    @mock.patch("reports.models.Report.save")
    def test_record_not_completed(self, mocked_save_report):
        data = copy(self.data)
        del data["ended_at"]
        record = Record(**data)
        record.save()
        mocked_save_report.assert_not_called()
