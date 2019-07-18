from copy import copy

from dateutil.parser import parse
from django.test import TestCase

from ..forms import EndRecordForm, StartRecordForm
from ..models import Record


class MissingFieldMixin:
    def _test_missing_field(self, field):
        data = copy(self.data)
        del data[field]

        form = self.form(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors[field], ["This field is required."])


class StartRecordFormTestCase(TestCase, MissingFieldMixin):
    form = StartRecordForm

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = {
            "call_id": "1",
            "source": "11123456789",  # 11 digits
            "destination": "1212345678",  # 10 digits
            "timestamp": "2016-02-29T15:00:00Z",
        }
        cls.end_record_data = {"call_id": "1", "ended_at": "2016-02-29T16:00:00Z"}

    def test_create_start_record(self):
        form = self.form(data=self.data)
        self.assertTrue(form.is_valid())

        record = form.save()
        self.assertTrue(
            Record.objects.filter(call_id=self.data.get("call_id")).exists()
        )

        self.assertEqual(record.source, self.data.get("source"))
        self.assertEqual(record.destination, self.data.get("destination"))
        self.assertEqual(record.started_at, parse(self.data.get("timestamp")))

    def test_update_start_record(self):
        Record.objects.create(**self.end_record_data)

        data = copy(self.data)
        data["call_id"] = self.end_record_data["call_id"]

        form = self.form(data=data)
        self.assertTrue(form.is_valid())

        record = form.save()
        self.assertTrue(Record.objects.filter(call_id=data["call_id"]).exists())
        self.assertEqual(record.source, data.get("source"))
        self.assertEqual(record.destination, data.get("destination"))
        self.assertEqual(record.started_at, parse(data.get("timestamp")))
        self.assertEqual(record.ended_at, parse(self.end_record_data.get("ended_at")))

    def test_call_end_before_start(self):
        end_record_data = copy(self.end_record_data)
        end_record_data["ended_at"] = "2016-02-29T14:00:00Z"

        Record.objects.create(**end_record_data)

        data = copy(self.data)
        data["call_id"] = end_record_data["call_id"]

        form = self.form(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors["timestamp"], ["Call end time before start time"])

    def test_create_start_invalid_source_number(self):
        data = copy(self.data)
        data["source"] = "123456789"  # 9 digits
        form = self.form(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors["source"], ["Invalid phone number"])

    def test_create_start_invalid_destination_number(self):
        data = copy(self.data)
        data["destination"] = "123456789123"  # 12 digits
        form = self.form(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors["destination"], ["Invalid phone number"])

    def test_create_without_call_id_error(self):
        self._test_missing_field("call_id")

    def test_create_without_source_error(self):
        self._test_missing_field("source")

    def test_create_without_destination_error(self):
        self._test_missing_field("destination")

    def test_create_without_timestamp_error(self):
        self._test_missing_field("timestamp")


class EndRecordFormTestCase(TestCase, MissingFieldMixin):
    form = EndRecordForm

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.data = {"call_id": "1", "timestamp": "2016-02-29T16:00:00Z"}
        cls.start_record_data = {
            "call_id": "1",
            "source": "11123456789",
            "destination": "1212345678",
            "started_at": "2016-02-29T15:00:00Z",
        }

    def test_call_start_after_end(self):
        start_record_data = copy(self.start_record_data)
        start_record_data["started_at"] = "2016-02-29T17:00:00Z"

        Record.objects.create(**start_record_data)

        data = copy(self.data)
        data["call_id"] = start_record_data["call_id"]

        form = self.form(data=data)
        self.assertFalse(form.is_valid())
        self.assertEqual(len(form.errors), 1)
        self.assertEqual(form.errors["timestamp"], ["Call start time after end time"])

    def test_create_without_call_id_error(self):
        self._test_missing_field("call_id")

    def test_create_without_timestamp_error(self):
        self._test_missing_field("timestamp")
