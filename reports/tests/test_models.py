from copy import copy

from dateutil.parser import parse
from django.test import TestCase

from ..models import Report


class ReportTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.standard_data = {
            "subscriber": "11981094379",
            "destination": "1198109437",
            "call_started_at": parse("2016-01-01T15:00:01Z"),
            "call_ended_at": parse("2016-01-01T15:50:37Z"),
        }
        cls.reduced_data = {
            "subscriber": "11981094379",
            "destination": "1198109437",
            "call_started_at": parse("2016-01-01T22:00:00Z"),
            "call_ended_at": parse("2016-01-02T05:59:59Z"),
        }
        cls.standard_and_reduced_data = {
            "subscriber": "11981094379",
            "destination": "1198109437",
            "call_started_at": parse("2016-01-01T21:57:13Z"),
            "call_ended_at": parse("2016-01-01T22:17:53Z"),
        }
        cls.reduced_and_standard_data = {
            "subscriber": "11981094379",
            "destination": "1198109437",
            "call_started_at": parse("2017-12-12T04:57:13Z"),
            "call_ended_at": parse("2017-12-12T06:10:56Z"),
        }

        cls.report_standard_only = Report.objects.create(**cls.standard_data)
        cls.report_reduced_only = Report.objects.create(**cls.reduced_data)
        cls.report_standard_and_reduced = Report.objects.create(
            **cls.standard_and_reduced_data
        )
        cls.report_reduced_and_standard = Report.objects.create(
            **cls.reduced_and_standard_data
        )

    def test_call_price_standard_only(self):
        self.assertEqual(self.report_standard_only.price_label, "R$ 4,86")

    def test_call_price_reduced_only(self):
        self.assertEqual(self.report_reduced_only.price_label, "R$ 0,36")

    def test_call_price_standard_and_reduced(self):
        self.assertEqual(self.report_standard_and_reduced.price_label, "R$ 0,54")

    def test_call_price_reduced_and_standard(self):
        self.assertEqual(self.report_reduced_and_standard.price_label, "R$ 1,26")

    def test_call_price_over_day(self):
        data = copy(self.standard_data)
        data["call_started_at"] = parse("2017-12-13T21:57:13Z")
        data["call_ended_at"] = parse("2017-12-14T22:10:56Z")
        report = Report.objects.create(**data)
        self.assertEqual(report.price_label, "R$ 86,85")

    def test_call_price_one_minute(self):
        data = copy(self.standard_data)
        data["call_started_at"] = parse("2017-12-13T21:57:13Z")
        data["call_ended_at"] = parse("2017-12-13T21:58:13Z")
        report = Report.objects.create(**data)
        self.assertEqual(report.price_label, "R$ 0,45")

    def test_call_price_less_than_one_minute(self):
        data = copy(self.standard_data)
        data["call_ended_at"] = parse("2016-01-01T15:00:59Z")
        report = Report.objects.create(**data)
        self.assertEqual(report.price_label, "R$ 0,36")

    def test_call_price_two_hours(self):
        data = copy(self.standard_data)
        data["call_ended_at"] = parse("2016-01-01T17:00:01Z")
        report = Report.objects.create(**data)
        self.assertEqual(report.price_label, "R$ 11,16")

    def test_call_start_date(self):
        self.assertEqual(
            self.report_standard_only.call_start_date,
            self.standard_data["call_started_at"].date(),
        )

    def test_call_start_time(self):
        self.assertEqual(
            self.report_standard_only.call_start_time,
            self.standard_data["call_started_at"].time(),
        )

    def test_call_duration(self):
        self.assertEqual(self.report_standard_only.call_duration, "0h50m36s")
        self.assertEqual(self.report_reduced_only.call_duration, "7h59m59s")
        self.assertEqual(self.report_standard_and_reduced.call_duration, "0h20m40s")
