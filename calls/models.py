from django.db import models


class Record(models.Model):
    call_id = models.IntegerField(unique=True)
    source = models.CharField(null=True, max_length=11)
    destination = models.CharField(null=True, max_length=11)
    started_at = models.DateTimeField(null=True)
    ended_at = models.DateTimeField(null=True)

    @property
    def completed(self):
        return self.start_record_completed and self.end_record_completed

    @property
    def start_record_completed(self):
        return all([self.source, self.destination, self.started_at])

    @property
    def end_record_completed(self):
        return all([self.ended_at])
