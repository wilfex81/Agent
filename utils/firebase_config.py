# import firebase_admin
# from firebase_admin import credentials, messaging

# cred = credentials.Certificate("/home/updated_virus/devworks/Agent/serviceAccountKey.json")  # Add your Firebase JSON key
# firebase_admin.initialize_app(cred)

# def send_push_notification(token, title, body):
#     message = messaging.Message(
#         notification=messaging.Notification(title=title, body=body),
#         token=token
#     )
#     response = messaging.send(message)
#     return response
