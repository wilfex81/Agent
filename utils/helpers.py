from fcm_django.models import FCMDevice

def send_push_notification(user, title, message):
    """Send a push notification to the user"""
    devices = FCMDevice.objects.filter(user=user)
    if devices.exists():
        devices.send_message(title=title, body=message)