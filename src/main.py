import os
import logging
from dotenv import load_dotenv
from youtube_operations import get_authenticated_service, fetch_videos_from_playlist
from video_processing import process_video, classify_video
from database_operations import get_playlist_map, get_all_videos, insert_into_firebase
from firebase_init import initialize_firebase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting video processing script")
    try:
        # Setup
        db = initialize_firebase()
        youtube = get_authenticated_service()

        # Get playlist map and temp playlist ID
        playlist_map = get_playlist_map(db)
        temp_playlist_id = playlist_map.get('Temp Playlist', {}).get('playlist_id')
        if not temp_playlist_id:
            logging.error("Temp Playlist not found.")
            return

        # Fetch videos from temp playlist
        temp_videos = fetch_videos_from_playlist(youtube, temp_playlist_id)[::-1]
        saved_videos = get_all_videos(db)

        for video in temp_videos:
            snippet = video.get('snippet', {})
            video_id = snippet.get('resourceId', {}).get('videoId', '')

            if snippet.get('title') in ["Private video", "Deleted video"] or not video_id:
                continue

            if any(v['video_id'] == video_id for v in saved_videos):
                continue

            # Process video
            video_data = process_video(video_id, snippet)
            category = classify_video(video_data)
            logging.info(f"Processed video: {video_data['title']} - Classified as: {category}")

            # Add to appropriate playlist and database
            cleaned_category = category.strip().replace('"', '')
            target_playlist = playlist_map.get(cleaned_category)

            if target_playlist:
                video_data["playlist_name"] = cleaned_category
                video_data["playlist_id"] = target_playlist['playlist_id']
                video_data["playlist_firebase_id"] = target_playlist['firebase_id']

                try:
                    insert_into_firebase(db, video_data)
                    logging.info(f"Video '{video_data['title']}' inserted into Firebase")
                except Exception as e:
                    logging.error(f"Error inserting video into Firebase: {str(e)}")
            else:
                logging.warning(f"No target playlist found for category: {category}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logging.info("Video processing script completed")

if __name__ == "__main__":
    main()
