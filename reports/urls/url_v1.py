from django.urls import include, path, register_converter

from ..views.api_v1 import ReportResource
from .converters import PhoneNumberConverter

register_converter(PhoneNumberConverter, "phone")


urlpatterns = [path("report/<phone:subscriber>/", include(ReportResource.urls()))]
