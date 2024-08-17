import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

def get_authenticated_service():
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def fetch_videos_from_playlist(youtube, playlist_id):
    videos = []
    request = youtube.playlistItems().list(
        part='snippet',
        maxResults=50,
        playlistId=playlist_id
    )
    while request:
        response = request.execute()
        videos.extend(response['items'])
        request = youtube.playlistItems().list(
            part='snippet',
            maxResults=50,
            playlistId=playlist_id,
            pageToken=response.get('nextPageToken')
        ) if 'nextPageToken' in response else None
    return videos

def add_to_playlist(youtube, video_id, playlist_id, video_title):
    videos = fetch_videos_from_playlist(youtube, playlist_id)
    
    existing_video_ids = {video['snippet']['resourceId']['videoId'] for video in videos}
    
    if video_id not in existing_video_ids:
        youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": video_id
                    }
                }
            }
        ).execute()
        return True

    else:
        # print(f"\N{cross mark} Video {video_title} already in playlist.")
        return False

def print_video(video_title, category):
    print(f"[green]✓[/green] [bold blue]{video_title}[/bold blue]   ->   playlist: [magenta]{category}[/magenta]")

def video_exists_in_playlists(youtube, playlist_map, video_id):
    for playlist in playlist_map.values():
        try:
            playlist_items = youtube.playlistItems().list(
                part="snippet",
                playlistId=playlist['playlist_id'],
                videoId=video_id
            ).execute()
            
            if playlist_items['items']:
                return True
        except Exception as e:
            print(f"Error checking playlist {playlist['playlist_id']}: {str(e)}")
    return False
