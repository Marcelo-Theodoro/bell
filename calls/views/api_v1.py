from ..forms import EndRecordForm, StartRecordForm
from ..preparers import END_RECORD_PREPARER, START_RECORD_PREPARER
from .views import BaseResource


class StartRecordResource(BaseResource):
    preparer = START_RECORD_PREPARER
    form = StartRecordForm


class EndRecordResource(BaseResource):
    preparer = END_RECORD_PREPARER
    form = EndRecordForm
