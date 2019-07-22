from datetime import datetime

from dateutil.relativedelta import relativedelta
from django import forms


class PeriodForm(forms.Form):
    period = forms.CharField(max_length=7, required=False)

    @property
    def _last_closed_period(self):
        return datetime.now() - relativedelta(months=1)

    def clean_period(self):
        period_requested = self.cleaned_data.get("period")
        if period_requested:
            try:
                period = datetime.strptime(period_requested, "%m/%Y")
            except ValueError:
                self.add_error("period", "Invalid period format.")
            else:
                return period

        return self._last_closed_period
