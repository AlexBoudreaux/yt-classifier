import os
import logging
from dotenv import load_dotenv
from youtube_operations import (
    get_authenticated_service,
    fetch_videos_from_playlist,
    add_to_playlist,
    print_video
)
from video_processing import (
    process_video,
    classify_video,
    process_cooking_video
)
from database_operations import (
    get_playlist_map,
    get_all_videos,
    insert_into_firebase
)
from pinecone_operations import (
    initialize_pinecone,
    embed_and_store_in_pinecone
)
from js_operations import (
    add_watchlater_to_temp,
    deselect_cooking_videos,
    execute_js_function
)
from firebase_init import initialize_firebase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting video processing script")
    try:
        # Execute JavaScript to add Watch Later videos to Temp playlist
        execute_js_function(add_watchlater_to_temp)

        # Setup
        db = initialize_firebase()
        youtube = get_authenticated_service()
        pinecone = initialize_pinecone()

        # Get playlist map and temp playlist ID
        playlist_map = get_playlist_map(db)
        temp_playlist_id = playlist_map.get('Temp Playlist', '')
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
            logging.info(f"Classified as: {category}")

            if category.strip().lower().replace('"', '') == "cooking":
                logging.info("Processing cooking video")
                video_data["url"] = f"https://www.youtube.com/watch?v={video_id}"
                try:
                    video_data = process_cooking_video(video_data)
                    embed_and_store_in_pinecone(pinecone, video_data)
                except Exception as e:
                    logging.error(f"Error processing cooking video: {str(e)}")
                    continue

            # Add to appropriate playlist and database
            cleaned_category = category.strip().replace('"', '')
            target_playlist_id = playlist_map.get(cleaned_category)

            if target_playlist_id:
                video_data["playlist_name"] = category
                video_data["playlist_id"] = target_playlist_id

                try:
                    if add_to_playlist(youtube, video_id, target_playlist_id, video_data["title"]):
                        insert_into_firebase(db, video_data)
                        print_video(snippet.get('title'), category)
                        logging.info("Video added to playlist and inserted into Firebase")
                    else:
                        logging.info("Video already in playlist or couldn't be added")
                except Exception as e:
                    logging.error(f"Error adding to playlist or inserting into Firebase: {str(e)}")
            else:
                logging.warning(f"No target playlist found for category: {category}")

        # Execute JavaScript to deselect cooking videos from Watch Later
        execute_js_function(deselect_cooking_videos)

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logging.info("Video processing script completed")

if __name__ == "__main__":
    main()
