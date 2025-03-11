from django.urls import path
from .views import (
    RideRequest,
    RideAccept,
    ScheduleRide,
    CancelScheduledRide,
    AssignScheduledRidesView,
    AutoCancelUnconfirmedRidesView
)

urlpatterns = [
    path("request-ride/", RideRequest.as_view(), name="request-ride"),
    path("accept-ride/", RideAccept.as_view(), name="accept-ride"),
    path("schedule-ride/", ScheduleRide.as_view(), name="schedule-ride"),
    path("cancel-scheduled-ride/<int:ride_id>/", CancelScheduledRide.as_view(), name="cancel-scheduled-ride"),
    path("assign-scheduled-rides/", AssignScheduledRidesView.as_view(), name="assign-scheduled-rides"),#remove this later on
    path("auto-cancel-unconfirmed-rides/", AutoCancelUnconfirmedRidesView.as_view(), name="auto-cancel-unconfirmed-rides"),#remove this later on
]
