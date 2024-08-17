import os
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

def get_authenticated_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

def get_playlist_items(youtube, playlist_id):
    items = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        items.extend(response['items'])
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return items

def main():
    youtube = get_authenticated_service()

    # List of playlist IDs (including Watch Later)
    playlist_ids = [
        'WL',  # Watch Later playlist
        'PLxxxxxxxxxxxxxxx1',  # Replace with your actual playlist IDs
        'PLxxxxxxxxxxxxxxx2',
        'PLxxxxxxxxxxxxxxx3',
        'PLxxxxxxxxxxxxxxx4',
        'PLxxxxxxxxxxxxxxx5',
        'PLxxxxxxxxxxxxxxx6',
        'PLxxxxxxxxxxxxxxx7',
        'PLxxxxxxxxxxxxxxx8',
        'PLxxxxxxxxxxxxxxx9',
        'PLxxxxxxxxxxxxxA',
        'PLxxxxxxxxxxxxxB'
    ]

    master_list = []

    for playlist_id in playlist_ids:
        print(f"Fetching videos from playlist: {playlist_id}")
        playlist_items = get_playlist_items(youtube, playlist_id)
        for item in playlist_items:
            video_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            master_list.append({
                'video_id': video_id,
                'title': title,
                'playlist_id': playlist_id
            })

    # Save the master list to a JSON file
    with open('master_video_list.json', 'w') as f:
        json.dump(master_list, f, indent=2)

    print(f"Master list created with {len(master_list)} videos.")

if __name__ == '__main__':
    main()
