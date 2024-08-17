def get_authenticated_service():
    pass

def fetch_videos_from_playlist(youtube, playlist_id):
    pass

def add_to_playlist(youtube, video_id, playlist_id, video_title):
    pass

def print_video(video_title, category):
    pass

def video_exists_in_playlists(youtube, playlist_map):
    for playlist in playlist_map.values():
        playlist_items = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist['playlist_id'],
            videoId=video_id
        ).execute()
        
        if playlist_items['items']:
            return True
    return False
