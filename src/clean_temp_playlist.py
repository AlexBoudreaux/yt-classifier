import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

def get_authenticated_service():
    credentials = None
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', scopes)
    
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', scopes)
            credentials = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(credentials.to_json())

    return googleapiclient.discovery.build('youtube', 'v3', credentials=credentials)

def clean_temp_playlist(youtube, playlist_id, target_video_id):
    next_page_token = None
    videos_to_remove = []
    target_found = False

    while not target_found:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            if video_id == target_video_id:
                target_found = True
                break
            videos_to_remove.append(item['id'])

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    print(f"Found {len(videos_to_remove)} videos to remove.")

    for item_id in videos_to_remove:
        try:
            youtube.playlistItems().delete(id=item_id).execute()
            print(f"Removed video with playlist item ID: {item_id}")
        except googleapiclient.errors.HttpError as e:
            print(f"An error occurred: {e}")

    print("Playlist cleaning completed.")

def main():
    youtube = get_authenticated_service()
    playlist_id = "PLZyXQ3RMIWiFjebCO49yXWpZ_q555zP5u"
    target_video_id = "T0869sx7CAg"
    
    clean_temp_playlist(youtube, playlist_id, target_video_id)

if __name__ == "__main__":
    main()
