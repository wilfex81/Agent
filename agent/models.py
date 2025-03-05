from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from fcm_django.models import FCMDevice

class RideRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
        ("negotiation", "Negotiation"),
    ]

    passenger = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ride_requests")
    rider = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_rides")
    pickup_location = models.CharField(max_length=255)
    dropoff_location = models.CharField(max_length=255)
    pickup_lat = models.FloatField()
    pickup_lon = models.FloatField()
    dropoff_lat = models.FloatField()
    dropoff_lon = models.FloatField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    scheduled_time = models.DateTimeField(null=True, blank=True)  # For scheduled rides
    created_at = models.DateTimeField(auto_now_add=True)

    def is_scheduled(self):
        return self.scheduled_time is not None

    def auto_cancel_if_not_confirmed(self):
        """Auto-cancels scheduled rides if the rider doesn't confirm 15 mins before"""
        if self.is_scheduled():
            cancel_time = self.scheduled_time - timedelta(minutes=15)
            if datetime.now() > cancel_time and self.status == "pending":
                self.status = "cancelled"
                self.save()
                return True
        return False
    


def register_device(user, token):
    """Stores the FCM token for a user"""
    FCMDevice.objects.update_or_create(
        user=user, defaults={"registration_id": token, "type": "android"}
    )