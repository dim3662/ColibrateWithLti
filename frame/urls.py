from django.urls import path
from . import views

app_name = 'bridge'

urlpatterns = [
    path('provider', views.provider),
    path('tests', views.tests)
]