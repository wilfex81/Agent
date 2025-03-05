from celery import shared_task
from agent.models import RideRequest

@shared_task
def auto_cancel_scheduled_rides():
    """Checks for unconfirmed scheduled rides and cancels them"""
    scheduled_rides = RideRequest.objects.filter(status="pending", scheduled_time__isnull=False)
    
    for ride in scheduled_rides:
        if ride.auto_cancel_if_not_confirmed():
            print(f"Ride {ride.id} auto-cancelled.")
