import os
from supabase import create_client, Client
from datetime import datetime

def setup_supabase() -> Client:
    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return supabase

def get_playlist_map(supabase: Client) -> dict:
    response = supabase.table('playlists').select('playlist_name, playlist_id').execute()
    return {pl['playlist_name']: pl['playlist_id'] for pl in response.data}

def get_all_videos(supabase: Client, page_size: int = 1000) -> list:
    all_videos = []
    start_idx = 0
    while True:
        response = supabase.table('videos').select('*').range(start_idx, start_idx + page_size - 1).execute()
        videos_chunk = response.data
        if not videos_chunk:
            break
        all_videos.extend(videos_chunk)
        start_idx += page_size
    return all_videos

def insert_into_supabase(supabase: Client, video_data: dict) -> dict:
    response = supabase.table('playlists').select('id').eq('playlist_id', video_data['playlist_id']).execute()
    
    playlist_fk_id = response.data[0].get('id') if response.data else None
    if not playlist_fk_id:
        raise ValueError(f"No matching playlist found for playlist_id: {video_data['playlist_id']}")

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
        "date_added_to_playlist": datetime.utcnow().isoformat(),
        "recipe": video_data.get('recipe'),
        "personalized_description": video_data.get('personalized_description'),
        "food_category": video_data.get('food_category')
    }

    response = supabase.table('videos').insert(data).execute()
    return response.data[0] if response.data else None
