# news/firebase.py
import os
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from django.conf import settings

def get_firebase_auth():
    """Initialize Firebase if not already initialized and return the auth object."""
    if not firebase_admin._apps:
        cred_path = settings.FIREBASE_SERVICE_ACCOUNT_FILE
        if not os.path.exists(cred_path):
            raise ValueError(f"Firebase service account file not found: {cred_path}")
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    return firebase_auth
