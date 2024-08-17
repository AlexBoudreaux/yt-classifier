import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def initialize_firebase():
    cred = credentials.Certificate("path/to/your/serviceAccountKey.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db
