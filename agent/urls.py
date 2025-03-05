from django.urls import path
from django.shortcuts import render
from .views import CreateRideRequestView, RideListView

urlpatterns = [
    path('rides/', RideListView.as_view(), name="ride-list"),
    path('rides/create/', CreateRideRequestView.as_view(), name="create-ride"),
]
