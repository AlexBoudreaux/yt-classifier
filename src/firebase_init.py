import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def initialize_firebase():
    cred = credentials.Certificate("../yt-search-409720-firebase-adminsdk-7g5pb-91edf7f73e.json")
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db
