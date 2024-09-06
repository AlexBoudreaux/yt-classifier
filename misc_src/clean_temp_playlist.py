import os
import time
import google_auth_oauthlib.flow
import googleapiclient.discovery
from googleapiclient.errors import HttpError
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

def gather_playlist_videos(youtube, playlist_id):
    videos = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()

        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            video_title = item['snippet']['title']
            video_creator = item['snippet'].get('videoOwnerChannelTitle', 'Unknown')
            videos.append({
                'id': item['id'],
                'video_id': video_id,
                'title': video_title,
                'creator': video_creator
            })

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos

def identify_videos_to_delete(videos, target_video_id):
    videos_to_delete = []
    target_found = False
    for video in videos:
        if target_found:
            videos_to_delete.append(video)
        if video['video_id'] == target_video_id:
            target_found = True
    return videos_to_delete

def delete_videos_from_playlist(youtube, playlist_id, videos_to_delete):
    batch_size = 50
    total_deleted = 0
    failed_deletions = []

    for i in range(0, len(videos_to_delete), batch_size):
        batch = youtube.new_batch_http_request()
        current_batch = videos_to_delete[i:i+batch_size]
        
        for video in current_batch:
            batch.add(youtube.playlistItems().delete(id=video['id']))
        
        retry_count = 0
        while retry_count < 3:
            try:
                responses = batch.execute()
                # Check if all responses in the batch were successful
                if all(response is None for response in responses):
                    total_deleted += len(current_batch)
                    print(f"Deleted batch of {len(current_batch)} videos. Total deleted: {total_deleted}")
                else:
                    print(f"Some deletions in the batch may have failed. Responses: {responses}")
                    failed_deletions.extend([video for video, response in zip(current_batch, responses) if response is not None])
                break
            except HttpError as e:
                if e.resp.status in [403, 429]:
                    retry_count += 1
                    wait_time = 2 ** retry_count
                    print(f"Rate limit hit. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    print(f"An error occurred while deleting videos: {e}")
                    failed_deletions.extend(current_batch)
                    break
        
        if retry_count == 3:
            print("Failed to delete batch after 3 retries. Moving to next batch.")
            failed_deletions.extend(current_batch)
        
        time.sleep(1)
    
    print(f"Deletion process completed. Total videos reported as deleted: {total_deleted}")
    print(f"Number of videos that failed to delete: {len(failed_deletions)}")
    
    # Verify deletions
    print("Verifying deletions...")
    remaining_videos = gather_playlist_videos(youtube, playlist_id)
    actually_deleted = len(videos_to_delete) - len(remaining_videos)
    print(f"Actual number of videos deleted: {actually_deleted}")
    
    if actually_deleted != total_deleted:
        print("Warning: There's a discrepancy between reported and actual deletions.")
        print("Some videos may not have been deleted successfully.")

    return actually_deleted, failed_deletions

def main():
    youtube = get_authenticated_service()
    playlist_id = "PLZyXQ3RMIWiFjebCO49yXWpZ_q555zP5u"
    target_video_id = "T0869sx7CAg"
    
    # Gather all videos from the playlist
    print("Gathering videos from the playlist...")
    all_videos = gather_playlist_videos(youtube, playlist_id)
    print(f"Total videos in playlist: {len(all_videos)}")
    
    # Identify videos to delete
    videos_to_delete = identify_videos_to_delete(all_videos, target_video_id)
    
    # Print information about videos to delete
    print(f"\nNumber of videos to be deleted: {len(videos_to_delete)}")
    print("\nFirst 5 videos that will be deleted:")
    for i, video in enumerate(videos_to_delete[:5], 1):
        print(f"{i}. '{video['title']}' by {video['creator']}")
    
    # Confirm deletion
    confirmation = input("\nAre you sure you want to delete these videos? (yes/no): ")
    if confirmation.lower() == 'yes':
        print("\nDeleting videos...")
        actually_deleted, failed_deletions = delete_videos_from_playlist(youtube, playlist_id, videos_to_delete)
        print(f"\nDeletion process completed. Actually deleted: {actually_deleted}")
        if failed_deletions:
            print(f"Number of videos that failed to delete: {len(failed_deletions)}")
            print("First 5 failed deletions:")
            for i, video in enumerate(failed_deletions[:5], 1):
                print(f"{i}. '{video['title']}' by {video['creator']}")
    else:
        print("\nDeletion cancelled. No videos were deleted.")

if __name__ == "__main__":
    main()
