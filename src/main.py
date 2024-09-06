import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from youtube_operations import get_authenticated_service, fetch_videos_from_playlist, add_to_playlist, print_video, video_exists_in_playlists, count_videos_in_playlist
from video_processing import process_video, classify_video, process_cooking_video
from database_operations import get_playlist_map, get_all_videos, insert_into_firebase, get_processed_video_ids
from firebase_init import initialize_firebase
from js_operations import add_watchlater_to_temp, deselect_cooking_and_podcast_videos
from pinecone_operations import initialize_pinecone, embed_and_store_in_pinecone
from config import OPENAI_API_KEY
import openai
import json

# Configure OpenAI API
openai.api_key = OPENAI_API_KEY

# Configure logging
logging.basicConfig(filename='video_processing.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    logging.info("Starting video processing script")
    try:

        logging.info("Starting to add watchlater to temp")
        add_watchlater_to_temp()
        logging.info("Completed adding watchlater to temp")

        # Setup
        try:
            db = retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(initialize_firebase)()
            youtube = retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(get_authenticated_service)()
            pinecone = retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(initialize_pinecone)()
        except Exception as e:
            logging.error(f"Error during setup: {str(e)}", exc_info=True)
            return

        # Get playlist map and temp playlist ID
        playlist_map = get_playlist_map(db)
        temp_playlist_id = playlist_map.get('Temp Playlist', {}).get('playlist_id')
        if not temp_playlist_id:
            logging.error("Temp Playlist not found.")
            return

        # Count and log the number of videos in the temp playlist
        video_count = count_videos_in_playlist(youtube, temp_playlist_id)
        logging.info(f"Number of videos in Temp Playlist: {video_count}")

        # Fetch videos from temp playlist
        try:
            temp_videos = retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(fetch_videos_from_playlist)(youtube, temp_playlist_id)[::-1]
        except Exception as e:
            logging.error(f"Error fetching videos from playlist: {str(e)}", exc_info=True)
            return
        logging.info(f"Fetched {len(temp_videos)} videos from Temp Playlist")

        # Get already processed video IDs
        processed_video_ids = get_processed_video_ids(db)
        logging.info(f"Found {len(processed_video_ids)} already processed videos")

        for video in temp_videos:
            snippet = video.get('snippet', {})
            video_id = snippet.get('resourceId', {}).get('videoId', '')

            if not video_id:
                logging.error("Video ID not found in snippet.")
                continue

            # Check if the video has already been processed
            if video_id in processed_video_ids:
                logging.info(f"Skipping already processed video: {video_id}")
                continue

            # Check if the video is private or deleted
            if snippet.get('title') == 'Private video' or snippet.get('title') == 'Deleted video':
                logging.info(f"Skipping private or deleted video: {video_id}")
                continue

            # Initialize video_data
            video_data = {}
            
            logging.info(f"Processing video: {snippet.get('title', 'Unknown Title')} (ID: {video_id})")
            logging.debug(f"Snippet received: {snippet}")

            # Process video
            try:
                video_data = process_video(video_id, snippet)
                logging.info(f"Processed video data: {json.dumps(video_data, indent=2)}")
                
                classification_result = classify_video(video_data)
                category = classification_result.split('<video_classification>')[1].split('</video_classification>')[0].strip().strip('"')
                logging.info(f"Classified as: {category}")

            except Exception as e:
                logging.error(f"Error processing or classifying video {video_id}: {str(e)}", exc_info=True)
                continue

            if category.lower() == "cooking":
                logging.info("Entering cooking video processing")
                video_data["url"] = f"https://www.youtube.com/watch?v={video_id}"
                try:
                    video_data = process_cooking_video(video_data)
                    logging.info(f"Processed cooking video data: {json.dumps(video_data, indent=2)}")
                except Exception as e:
                    logging.error(f"Error in process_cooking_video for video {video_id}: {str(e)}", exc_info=True)
                    continue

                try:
                    embed_and_store_in_pinecone(pinecone, video_data)
                    logging.info("Embedded and stored in Pinecone")
                except Exception as e:
                    logging.error(f"Error in embed_and_store_in_pinecone for video {video_id}: {str(e)}", exc_info=True)
                    continue

            target_playlist = playlist_map.get(category)

            if target_playlist:
                video_data["playlist_name"] = category
                video_data["playlist_id"] = target_playlist['playlist_id']
                video_data["playlist_firebase_id"] = target_playlist['firebase_id']

                try:
                    add_to_playlist_result = add_to_playlist(youtube, video_id, target_playlist['playlist_id'], video_data["title"])
                    if add_to_playlist_result:
                        logging.info(f"Video {video_id} added to playlist {category}")
                    else:
                        logging.info(f"Video {video_id} already in playlist {category}")
                    
                    # Always insert into Firebase, regardless of playlist addition result
                    insert_into_firebase(db, video_data)
                    # Move this line here, after all operations are successful:
                    print_video(snippet.get('title'), category)
                    logging.info(f"Video {video_id} inserted into Firebase")
                except Exception as e:
                    if "403" in str(e) or "quotaExceeded" in str(e):
                        logging.error(f"403 error or quota exceeded: {str(e)}. Exiting program.")
                        return  # This will exit the main function
                    logging.error(f"Error in add_to_playlist or insert_into_firebase for video {video_id}: {str(e)}", exc_info=True)
                    continue
            else:
                logging.warning(f"No target playlist found for category: {category}")

        logging.info("Starting to deselect cooking and podcast videos")
        deselect_cooking_and_podcast_videos()
        logging.info("Completed deselecting cooking and podcast videos")
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logging.info("Video processing script completed")

if __name__ == "__main__":
    main()
