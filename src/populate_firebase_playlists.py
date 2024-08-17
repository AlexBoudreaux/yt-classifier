from firebase_init import initialize_firebase

def populate_playlists(db):
    playlists = [
        {"name": "Development/AI", "id": "PLbWDhxwM_45mPVToqaboOI3pWGltM-9lA"},
        {"name": "Podcast/Comedy", "id": "PLbWDhxwM_45lQKrOBD5QLH6lRvQT_9_Qe"},
        {"name": "Woodworking/DIY", "id": "PLbWDhxwM_45nMF0Jt_vGhVZ_Ob_QZsHIx"},
        {"name": "Arduino/Pi/SmartHome", "id": "PLbWDhxwM_45mXhNXxhWZZXZXwlHNO_5Yk"},
        {"name": "Work/Growth", "id": "PLbWDhxwM_45lxWVIbLluOhNUODXfOONsO"},
        {"name": "Finance", "id": "PLbWDhxwM_45nXZLvTwHqvK7v-4Oc8aQwj"},
        {"name": "Gaming", "id": "PLbWDhxwM_45nXZLvTwHqvK7v-4Oc8aQwj"},
        {"name": "Science/History", "id": "PLbWDhxwM_45lQKrOBD5QLH6lRvQT_9_Qe"},
        {"name": "Startup/Business", "id": "PLbWDhxwM_45lQKrOBD5QLH6lRvQT_9_Qe"},
        {"name": "General Entertainment/News/Politics/Shows", "id": "PLbWDhxwM_45lQKrOBD5QLH6lRvQT_9_Qe"},
        {"name": "Cooking", "id": "PLbWDhxwM_45mXhNXxhWZZXZXwlHNO_5Yk"},
        {"name": "Temp Playlist", "id": "PLbWDhxwM_45nXZLvTwHqvK7v-4Oc8aQwj"}
    ]

    playlists_ref = db.collection('playlists')

    for playlist in playlists:
        playlists_ref.add({
            'playlist_name': playlist['name'],
            'playlist_id': playlist['id']
        })

    print("Playlists have been populated in Firebase.")

def main():
    db = initialize_firebase()
    populate_playlists(db)

if __name__ == "__main__":
    main()
