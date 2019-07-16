from copy import copy

from django import forms
from django.utils.functional import cached_property

from .models import Record


class BaseRecordForm(forms.Form):
    call_id = forms.IntegerField(required=True)
    timestamp = forms.DateTimeField(required=True)

    def record(self, call_id):
        if call_id:
            # This will make we always return 201 and update to the last value sent
            return Record.objects.filter(call_id=call_id).first() or Record(
                call_id=call_id
            )

    @cached_property
    def instance(self):
        return self.record(self.data.get("call_id"))

    def save(self):
        data = self.prepared_data
        record = self.instance
        for key, value in data.items():
            setattr(record, key, value)
        record.save()
        return record


class StartRecordForm(BaseRecordForm):
    source = forms.IntegerField(required=True)
    destination = forms.IntegerField(required=True)

    def clean_timestamp(self):
        started_at = self.cleaned_data["timestamp"]
        if (
            self.instance
            and self.instance.ended_at
            and self.instance.ended_at < started_at
        ):
            self.add_error("timestamp", "Call end time before start time")
        return started_at

    @property
    def prepared_data(self):
        data = copy(self.cleaned_data)
        data["started_at"] = data.pop("timestamp")
        return data


class EndRecordForm(BaseRecordForm):
    @property
    def prepared_data(self):
        data = copy(self.cleaned_data)
        data["ended_at"] = data.pop("timestamp")
        return data

    def clean_timestamp(self):
        ended_at = self.cleaned_data["timestamp"]
        if (
            self.instance
            and self.instance.started_at
            and self.instance.started_at > ended_at
        ):
            self.add_error("timestamp", "Call start time after end time")
        return ended_at
