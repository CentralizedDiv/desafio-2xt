from django.urls import path
from . import views

urlpatterns = [
    path('', views.flightSearch, name='flightSearch'),
    path('gatheredData/', views.gatheredData, name='gatheredData'),
]

