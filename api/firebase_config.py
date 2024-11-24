
# # firebase_config.py
# import os

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# import firebase_admin
# from firebase_admin import credentials
# from firebase_admin import credentials, messaging

# def initialize_firebase():
#     FIREBASE_CREDENTIALS_PATH = f'{BASE_DIR}/erp_backend/firebase-cred.json'
#     cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)  # Path to your Firebase service account JSON file
#     firebase_admin.initialize_app(cred)
#     print(FIREBASE_CREDENTIALS_PATH)

