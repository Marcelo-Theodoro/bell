from restless.preparers import FieldsPreparer

REPORT = {
    "destination": "destination",
    "call_start_date": "call_start_date",
    "call_start_time": "call_start_time",
    "call_duration": "call_duration",
    "call_duration": "call_duration",
    "price": "price_label",
}
REPORT_PREPARER = FieldsPreparer(fields=REPORT)
