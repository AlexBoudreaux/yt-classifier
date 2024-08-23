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

def clean_temp_playlist(youtube, playlist_id, target_video_id, dry_run=True):
    videos_to_remove = []
    next_page_token = None
    target_found = False

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in reversed(response['items']):
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            video_creator = item['snippet']['videoOwnerChannelTitle']
            
            if target_found:
                break
            
            videos_to_remove.append((item['id'], video_title, video_creator))
            
            if video_id == target_video_id:
                target_found = True

        if target_found or not response.get('nextPageToken'):
            break
        
        next_page_token = response.get('nextPageToken')

    total_videos = len(videos_to_remove)
    print(f"Found {total_videos} videos that would be removed.")
    print("\nFirst 5 videos that would be deleted:")
    for i, (item_id, title, creator) in enumerate(videos_to_remove[:5], 1):
        print(f"{i}. '{title}' by {creator}")
    
    print(f"\nTotal number of videos that would be deleted: {total_videos}")

    if not dry_run:
        for item_id, title, _ in videos_to_remove:
            try:
                youtube.playlistItems().delete(id=item_id).execute()
                print(f"Removed video: '{title}' with playlist item ID: {item_id}")
            except googleapiclient.errors.HttpError as e:
                print(f"An error occurred while trying to remove '{title}': {e}")

    print("Playlist cleaning completed.")

def count_videos_in_playlist(youtube, playlist_id):
    request = youtube.playlistItems().list(
        part="id",
        playlistId=playlist_id,
        maxResults=50
    )
    response = request.execute()
    total_videos = response['pageInfo']['totalResults']
    return total_videos

def main():
    youtube = get_authenticated_service()
    playlist_id = "PLZyXQ3RMIWiFjebCO49yXWpZ_q555zP5u"
    target_video_id = "T0869sx7CAg"
    
    # Count and log the number of videos in the temp playlist
    video_count = count_videos_in_playlist(youtube, playlist_id)
    print(f"Number of videos in Temp Playlist: {video_count}")
    
    # Perform a dry run first
    print("Performing dry run...")
    clean_temp_playlist(youtube, playlist_id, target_video_id, dry_run=True)
    
    # Ask for confirmation before actual deletion
    user_input = input("Do you want to proceed with the actual deletion? (yes/no): ").lower()
    if user_input == 'yes':
        print("Proceeding with actual deletion...")
        clean_temp_playlist(youtube, playlist_id, target_video_id, dry_run=False)
        
        # Count and log the number of videos after deletion
        new_video_count = count_videos_in_playlist(youtube, playlist_id)
        print(f"Number of videos in Temp Playlist after deletion: {new_video_count}")
        print(f"Number of videos removed: {video_count - new_video_count}")
    else:
        print("Deletion cancelled.")

if __name__ == "__main__":
    main()
