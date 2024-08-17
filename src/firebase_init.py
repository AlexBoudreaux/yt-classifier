import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from config import FIREBASE_ADMIN_SDK_PATH

def initialize_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(FIREBASE_ADMIN_SDK_PATH)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db
