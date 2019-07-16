from django.urls import include, path

from ..views.api_v1 import EndRecordResource, StartRecordResource

urlpatterns = [
    path("start/", include(StartRecordResource.urls())),
    path("end/", include(EndRecordResource.urls())),
]
