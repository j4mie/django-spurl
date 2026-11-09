from django.http import HttpResponse
from django.urls import path

urlpatterns = [
    path("test/", lambda request: HttpResponse("ok"), name="test"),
]
