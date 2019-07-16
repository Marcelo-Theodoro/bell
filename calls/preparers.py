from restless.preparers import FieldsPreparer

START_RECORD = {
    "call_id": "call_id",
    "source": "source",
    "destination": "destination",
    "started_at": "started_at",
}
START_RECORD_PREPARER = FieldsPreparer(fields=START_RECORD)


END_RECORD = {"call_id": "call_id", "ended_at": "ended_at"}
END_RECORD_PREPARER = FieldsPreparer(fields=END_RECORD)
