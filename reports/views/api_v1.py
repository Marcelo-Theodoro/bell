from restless.dj import DjangoResource
from restless.exceptions import BadRequest

from ..forms import PeriodForm
from ..models import Report
from ..preparers import REPORT_PREPARER


class ReportResource(DjangoResource):
    preparer = REPORT_PREPARER

    def base_query(self):
        return Report.objects.all()

    @property
    def period(self):
        form = PeriodForm(self.request.GET)
        if not form.is_valid():
            raise BadRequest(form.errors)
        return (form.cleaned_data["period"].year, form.cleaned_data["period"].month)

    def list(self, subscriber):
        year, month = self.period

        return self.base_query().filter(
            call_ended_at__year=year, call_ended_at__month=month, subscriber=subscriber
        )
