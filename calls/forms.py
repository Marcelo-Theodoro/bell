from copy import copy

from django import forms
from django.utils.functional import cached_property

from .models import Record
from .validators import PhoneNumberValidator


class BaseRecordForm(forms.Form):
    call_id = forms.IntegerField(required=True)
    timestamp = forms.DateTimeField(required=True)

    def record(self, call_id):
        if call_id:
            return Record.objects.filter(call_id=call_id).first() or Record(
                call_id=call_id
            )

    @cached_property
    def instance(self):
        return self.record(self.data.get("call_id"))

    def clean(self, *args, **kwargs):
        response = super().clean(*args, **kwargs)
        if self.instance and self.instance.completed:
            raise forms.ValidationError("This record is completed")
        return response

    def save(self):
        data = self.prepared_data
        record = self.instance
        for key, value in data.items():
            setattr(record, key, value)
        record.save()
        return record


class StartRecordForm(BaseRecordForm):
    source = forms.CharField(validators=[PhoneNumberValidator], required=True)
    destination = forms.CharField(validators=[PhoneNumberValidator], required=True)

    def clean_timestamp(self):
        started_at = self.cleaned_data["timestamp"]
        if (
            self.instance
            and self.instance.ended_at
            and self.instance.ended_at < started_at
        ):
            self.add_error("timestamp", "Call end time before start time")
        return started_at

    def clean(self, *args, **kwargs):
        response = super().clean(*args, **kwargs)
        if self.instance and self.instance.start_record_completed:
            raise forms.ValidationError("The start record of this call is completed")
        return response

    @property
    def prepared_data(self):
        data = copy(self.cleaned_data)
        data["started_at"] = data.pop("timestamp")
        return data


class EndRecordForm(BaseRecordForm):
    def clean(self, *args, **kwargs):
        response = super().clean(*args, **kwargs)
        if self.instance and self.instance.end_record_completed:
            raise forms.ValidationError("The end record of this call is completed")

        return response

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
