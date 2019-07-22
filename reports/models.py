import datetime
import itertools
import locale
from decimal import Decimal

from django.conf import settings
from django.db import models


def next_minutes_generator(start_datetime):
    return (
        start_datetime + datetime.timedelta(seconds=i)
        for i in itertools.count(start=60, step=60)
    )  # pragma: no cover


class Report(models.Model):

    subscriber = models.CharField(max_length=11, db_index=True)
    destination = models.CharField(max_length=11)

    call_started_at = models.DateTimeField()
    call_ended_at = models.DateTimeField()

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.price = self.calculate_price()
        super().save(*args, **kwargs)

    def calculate_price(self):
        minutes = self.minutes_in_each_tarrif()
        per_minute_charge = self.per_minute_charge(minutes)
        charge = self.charge()
        return charge + per_minute_charge

    def charge(self):
        if (
            self.standard_starts_at.hour
            <= self.call_started_at.hour
            <= self.standard_ends_at.hour
        ):
            return self.standard_charge
        return self.reduced_charge

    def per_minute_charge(self, minutes):
        per_minute_charge = minutes["reduced"] * self.reduced_charge_per_minute
        per_minute_charge += minutes["standard"] * self.standard_charge_per_minute
        return per_minute_charge

    def minutes_in_each_tarrif(self):
        count_standard = 0
        count_reduced = 0
        for moment in next_minutes_generator(self.call_started_at):  # pragma: no branch
            if moment > self.call_ended_at:
                break
            if (
                self.standard_starts_at.hour
                <= moment.hour
                <= self.standard_ends_at.hour
            ):
                count_standard += 1
            else:
                count_reduced += 1
        return {"reduced": count_reduced, "standard": count_standard}

    @property
    def price_label(self):
        price = self.price.quantize(Decimal("0.01"))
        locale.setlocale(locale.LC_MONETARY, "pt_BR.UTF-8'")
        return locale.currency(price, grouping=True)

    @property
    def call_start_date(self):
        return self.call_started_at.date()

    @property
    def call_start_time(self):
        return self.call_started_at.time()

    @property
    def call_duration(self):
        duration = self.call_ended_at - self.call_started_at
        total_seconds = duration.total_seconds()
        hours, minutes = divmod(total_seconds, 3600)
        minutes, seconds = divmod(minutes, 60)
        return f"{int(hours)}h{int(minutes)}m{int(seconds)}s"

    @property
    def standard_starts_at(self):
        return settings.FEES["standard"]["starts_at"]

    @property
    def standard_ends_at(self):
        return settings.FEES["standard"]["ends_at"]

    @property
    def standard_charge(self):
        return settings.FEES["standard"]["charge"]

    @property
    def standard_charge_per_minute(self):
        return settings.FEES["standard"]["charge_per_minute"]

    @property
    def reduced_charge(self):
        return settings.FEES["reduced"]["charge"]

    @property
    def reduced_charge_per_minute(self):
        return settings.FEES["reduced"]["charge_per_minute"]
