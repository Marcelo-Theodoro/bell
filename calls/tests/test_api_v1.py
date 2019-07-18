import json
from copy import copy

from dateutil.parser import parse
from django.db import connection, reset_queries
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Record


class BaseResourceTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.start_record_data = {
            "call_id": "1",
            "source": "11123456789",
            "destination": "12123456789",
            "timestamp": "2016-02-29T12:00:00Z",
        }
        cls.end_record_data = {"call_id": "1", "timestamp": "2016-02-29T23:13:15Z"}

    def post(self, data, max_queries=False):
        client = Client()
        reset_queries()
        with self.settings(DEBUG=bool(max_queries)):
            response = client.post(self.endpoint, data, content_type="application/json")
        if max_queries:
            queries = self._get_len_queries()
            self.assertLessEqual(
                len(queries), max_queries, msg="\n" + "\n".join(queries)
            )
        return response

    def _parse_error_response(self, response):
        content = response.content.decode("utf-8")
        return json.loads(content)["error"]

    def _get_len_queries(self):
        valid_prefixes = ("SELECT", "INSERT", "UPDATE", "DELETE")
        queries = [
            q["sql"] for q in connection.queries if q["sql"].startswith(valid_prefixes)
        ]
        return queries


class StartResourceTestCase(BaseResourceTestCase):
    endpoint = reverse("api_startrecord_list")

    def test_start_record(self):
        response = self.post(self.start_record_data, max_queries=2)
        self.assertEqual(response.status_code, 201)

        record = Record.objects.get(call_id=self.start_record_data["call_id"])
        self.assertEqual(record.source, self.start_record_data["source"])
        self.assertEqual(record.destination, self.start_record_data["destination"])
        self.assertEqual(record.started_at, parse(self.start_record_data["timestamp"]))
        self.assertEqual(record.ended_at, None)
        self.assertTrue(record.start_record_completed)

    def test_create_start_record_end_exists(self):
        end_record_data = copy(self.end_record_data)
        end_record_data["ended_at"] = end_record_data.pop("timestamp")
        Record.objects.create(**end_record_data)

        response = self.post(self.start_record_data, max_queries=3)
        self.assertEqual(response.status_code, 201)

        record = Record.objects.get(call_id=self.start_record_data["call_id"])
        self.assertEqual(record.source, self.start_record_data["source"])
        self.assertEqual(record.destination, self.start_record_data["destination"])
        self.assertEqual(record.started_at, parse(self.start_record_data["timestamp"]))
        self.assertEqual(record.ended_at, parse(end_record_data["ended_at"]))
        self.assertTrue(record.completed)

    def test_create_start_record_without_call_id(self):
        data = copy(self.start_record_data)
        del data["call_id"]
        response = self.post(data, max_queries=0)
        self.assertEqual(response.status_code, 400)

        expected = {"call_id": ["This field is required."]}
        self.assertEqual(self._parse_error_response(response), expected)

    def test_create_start_record_exists(self):
        data = copy(self.start_record_data)
        data["started_at"] = data.pop("timestamp")
        Record.objects.create(**data)

        response = self.post(self.start_record_data, max_queries=1)

        expected = {"__all__": ["The start record of this call is completed"]}
        self.assertEqual(expected, self._parse_error_response(response))

    def test_create_record_completed(self):
        data = copy(self.start_record_data)
        data["started_at"] = parse(data.pop("timestamp"))

        end_data = copy(self.end_record_data)
        end_data["ended_at"] = parse(end_data.pop("timestamp"))

        data.update(end_data)
        Record.objects.create(**data)

        response = self.post(self.start_record_data, max_queries=1)

        expected = {"__all__": ["This record is completed"]}
        self.assertEqual(expected, self._parse_error_response(response))


class EndResourceTestCase(BaseResourceTestCase):
    endpoint = reverse("api_endrecord_list")

    def test_create_end_record(self):
        response = self.post(self.end_record_data, max_queries=2)
        self.assertEqual(response.status_code, 201)

        record = Record.objects.get(call_id=self.end_record_data["call_id"])
        self.assertEqual(record.ended_at, parse(self.end_record_data["timestamp"]))
        self.assertEqual(record.started_at, None)
        self.assertTrue(record.end_record_completed)

    def test_create_end_record_start_exists(self):
        start_record_data = copy(self.start_record_data)
        start_record_data["started_at"] = start_record_data.pop("timestamp")
        Record.objects.create(**start_record_data)

        response = self.post(self.end_record_data, max_queries=3)
        self.assertEqual(response.status_code, 201)

        record = Record.objects.get(call_id=self.end_record_data["call_id"])
        self.assertEqual(record.ended_at, parse(self.end_record_data["timestamp"]))
        self.assertEqual(record.started_at, parse(start_record_data["started_at"]))
        self.assertTrue(record.completed)

    def test_create_end_record_without_timestamp(self):
        data = copy(self.end_record_data)
        del data["timestamp"]
        response = self.post(data, max_queries=0)
        self.assertEqual(response.status_code, 400)

        expected = {"timestamp": ["This field is required."]}
        self.assertEqual(self._parse_error_response(response), expected)

    def test_create_end_record_exists(self):
        data = copy(self.end_record_data)
        data["ended_at"] = data.pop("timestamp")
        Record.objects.create(**data)

        response = self.post(self.end_record_data, max_queries=1)

        expected = {"__all__": ["The end record of this call is completed"]}
        self.assertEqual(expected, self._parse_error_response(response))
