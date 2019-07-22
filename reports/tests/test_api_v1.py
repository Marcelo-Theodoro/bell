import json

from dateutil.parser import parse
from django.db import connection, reset_queries
from django.test import Client, TestCase
from django.urls import reverse
from freezegun import freeze_time

from ..models import Report


class ReportTestCase(TestCase):
    endpoint = reverse("api_report_list", args=["99988526423"])

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Report.objects.create(
            subscriber="99988526423",
            destination="9933468278",
            call_started_at=parse("2016-02-29T12:00:00Z"),
            call_ended_at=parse("2016-02-29T14:00:00Z"),
        )
        Report.objects.create(
            subscriber="99988526423",
            destination="9933468278",
            call_started_at=parse("2016-02-01T14:00:00Z"),
            call_ended_at=parse("2016-02-01T14:12:00Z"),
        )
        Report.objects.create(
            subscriber="99988526423",
            destination="9933468278",
            call_started_at=parse("2016-02-15T23:43:00Z"),
            call_ended_at=parse("2016-02-16T01:10:00Z"),
        )

    def get(self, url_params=None, max_queries=False, expected_status=200):
        client = Client()
        reset_queries()
        with self.settings(DEBUG=bool(max_queries)):
            response = client.get(
                self.endpoint, url_params, content_type="application/json"
            )
        if max_queries:
            queries = self._get_len_queries()
            self.assertLessEqual(
                len(queries), max_queries, msg="\n" + "\n".join(queries)
            )
        self.assertEqual(response.status_code, expected_status)
        return self._parse_response(response)

    def _get_len_queries(self):
        valid_prefixes = ("SELECT", "INSERT", "UPDATE", "DELETE")
        queries = [
            q["sql"] for q in connection.queries if q["sql"].startswith(valid_prefixes)
        ]
        return queries

    def _parse_response(self, response):
        content = response.content.decode("utf-8")
        return json.loads(content)

    @freeze_time("2016-03-15")
    def test_list_reports_without_pariod(self):
        response = self.get(max_queries=1)
        expected = {
            "objects": [
                {
                    "destination": "9933468278",
                    "call_start_date": "2016-02-29",
                    "call_start_time": "12:00:00",
                    "call_duration": "2h0m0s",
                    "price": "R$ 11,16",
                },
                {
                    "destination": "9933468278",
                    "call_start_date": "2016-02-01",
                    "call_start_time": "14:00:00",
                    "call_duration": "0h12m0s",
                    "price": "R$ 1,44",
                },
                {
                    "destination": "9933468278",
                    "call_start_date": "2016-02-15",
                    "call_start_time": "23:43:00",
                    "call_duration": "1h27m0s",
                    "price": "R$ 0,36",
                },
            ]
        }
        self.assertEqual(response, expected)

    def test_list_report_with_period(self):
        response = self.get(url_params={"period": "02/2016"}, max_queries=1)
        expected = {
            "objects": [
                {
                    "destination": "9933468278",
                    "call_start_date": "2016-02-29",
                    "call_start_time": "12:00:00",
                    "call_duration": "2h0m0s",
                    "price": "R$ 11,16",
                },
                {
                    "destination": "9933468278",
                    "call_start_date": "2016-02-01",
                    "call_start_time": "14:00:00",
                    "call_duration": "0h12m0s",
                    "price": "R$ 1,44",
                },
                {
                    "destination": "9933468278",
                    "call_start_date": "2016-02-15",
                    "call_start_time": "23:43:00",
                    "call_duration": "1h27m0s",
                    "price": "R$ 0,36",
                },
            ]
        }
        self.assertEqual(response, expected)

    def test_list_report_with_invalid_period(self):
        response = self.get(url_params={"period": "2/16"}, expected_status=400)
        expected = {"error": {"period": ["Invalid period format."]}}
        self.assertEqual(response, expected)
