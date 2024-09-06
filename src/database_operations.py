from datetime import datetime

from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_playlist_map(db):
    playlists_ref = db.collection('playlists')
    playlists = playlists_ref.get()
    playlist_map = {}
    for pl in playlists:
        pl_dict = pl.to_dict()
        playlist_map[pl_dict['playlist_name']] = {
            'playlist_id': pl_dict['playlist_id'],
            'firebase_id': pl.id
        }
    return playlist_map

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
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
        "creator": video_data.get('creator', 'Unknown'),  # Ensure creator is stored, default to 'Unknown' if not present
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

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def get_processed_video_ids(db):
    videos_ref = db.collection('videos')
    videos = videos_ref.get()
    return set(video.to_dict()['video_id'] for video in videos)
