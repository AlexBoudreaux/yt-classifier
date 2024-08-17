from datetime import datetime

def get_playlist_map(db):
    playlists_ref = db.collection('playlists')
    playlists = playlists_ref.get()
    return {pl.to_dict()['playlist_name']: pl.to_dict()['playlist_id'] for pl in playlists}

def get_all_videos(db):
    videos_ref = db.collection('videos')
    videos = videos_ref.get()
    return [video.to_dict() for video in videos]

def insert_into_firebase(db, video_data):
    playlists_ref = db.collection('playlists')
    playlist_query = playlists_ref.where('playlist_id', '==', video_data['playlist_id']).get()
    
    if not playlist_query:
        raise ValueError(f"No matching playlist found for playlist_id: {video_data['playlist_id']}")

    playlist_doc = playlist_query[0]
    playlist_fk_id = playlist_doc.id

    cleaned_category = video_data['playlist_name'].strip().replace('"', '')

    data = {
        "playlist_id_fk": playlist_fk_id,
        "category": cleaned_category,
        "playlist_id": video_data['playlist_id'],
        "video_id": video_data['video_id'],
        "video_name": video_data['title'],
        "creator": video_data['creator'],
        "description": video_data['description'],
        "transcript": video_data['transcript'],
        "summary": video_data['summary'],
        "date_added_to_playlist": datetime.utcnow(),
    }

    # Add cooking-specific fields only if they exist
    for field in ['recipe', 'personalized_description', 'food_category']:
        if field in video_data:
            data[field] = video_data[field]

    videos_ref = db.collection('videos')
    new_video_ref = videos_ref.add(data)
    return new_video_ref[1].get().to_dict()
