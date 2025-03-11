from firebase_admin import messaging

def send_push_notification(token, title, body, data=None):
    """Send a push notification via Firebase Cloud Messaging (FCM)."""
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token,
        data=data or {},
    )
    response = messaging.send(message)
    print(f"FCM Notification Sent: {response}")