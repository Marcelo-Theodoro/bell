from calls.models import Record
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Report


@receiver(post_save, sender=Record)
def create_report_instance(*args, instance, **kwargs):
    if instance.completed:
        report = Report()
        report.subscriber = instance.source
        report.destination = instance.destination
        report.call_started_at = instance.started_at
        report.call_ended_at = instance.ended_at
        report.save()
