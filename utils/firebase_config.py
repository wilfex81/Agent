import firebase_admin
from firebase_admin import credentials, messaging

cred = credentials.Certificate("/")
firebase_admin.initialize_app(cred)

def send_push_notification(token, title, body,data=None):
    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        token=token
    )
    data = data if data else {}
    response = messaging.send(message)
    return response
