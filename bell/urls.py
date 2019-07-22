from django.http import HttpResponse
from django.urls import include, path


def ping(request):
    return HttpResponse("pong")


urlpatterns = [
    path("ping/", ping),
    path("v1/calls/", include("calls.urls.url_v1")),
    path("v1/reports/", include("reports.urls.url_v1")),
]
