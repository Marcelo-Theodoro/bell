import locale
from datetime import datetime
from decimal import Decimal

import pendulum
from django.conf import settings
from django.db import models


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
        minutes_to_charge = []

        call_started_at = pendulum.instance(self.call_started_at)
        call_ended_at = pendulum.instance(self.call_ended_at)

        call_start_day = pendulum.instance(call_started_at)
        call_end_day = pendulum.instance(call_ended_at)

        total_duration = pendulum.period(call_start_day, call_end_day)
        for day in total_duration.range("days"):

            start_standard_charge = pendulum.instance(
                datetime.combine(day, self.standard_starts_at)
            )
            stop_standard_charge = pendulum.instance(
                datetime.combine(day, self.standard_ends_at)
            )

            start_charging_at = max(call_started_at, start_standard_charge)
            stop_charging_at = min(call_ended_at, stop_standard_charge)

            minutes_to_charge_day = (stop_charging_at - start_charging_at).in_minutes()
            minutes_to_charge.append(minutes_to_charge_day)

        standard_minutes = sum(minutes_to_charge)
        reduced_minutes = total_duration.in_minutes() - standard_minutes

        return {
            "reduced": max(0, reduced_minutes),
            "standard": max(0, standard_minutes),
        }

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
