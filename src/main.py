import logging
from tenacity import retry, stop_after_attempt, wait_fixed
from src.youtube_operations import get_authenticated_service, fetch_videos_from_playlist, add_to_playlist, print_video, video_exists_in_playlists
from video_processing import process_video, classify_video, process_cooking_video
from database_operations import get_playlist_map, get_all_videos, insert_into_firebase
from firebase_init import initialize_firebase
from js_operations import deselect_cooking_videos
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

        # Fetch videos from temp playlist
        try:
            temp_videos = retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(fetch_videos_from_playlist)(youtube, temp_playlist_id)[::-1]
        except Exception as e:
            logging.error(f"Error fetching videos from playlist: {str(e)}", exc_info=True)
            return
        for video in temp_videos:
            snippet = video.get('snippet', {})
            video_id = snippet.get('resourceId', {}).get('videoId', '')

            if snippet.get('title') in ["Private video", "Deleted video"] or not video_id:
                continue

            # Check if video already exists in any playlist
            if video_exists_in_playlists(youtube, playlist_map, video_id):
                continue

            # Process video
            try:
                video_data = process_video(video_id, snippet)
                classification_result = classify_video(video_data)
            except Exception as e:
                logging.error(f"Error processing or classifying video {video_id}: {str(e)}", exc_info=True)
                continue
            category = classification_result.split('<video_classification>')[1].split('</video_classification>')[0].strip().strip('"')
            logging.info(f"Classified as: {category}")

            if category.lower() == "cooking":
                logging.info("Entering cooking video processing")
                video_data["url"] = f"https://www.youtube.com/watch?v={video_id}"
                try:
                    try:
                        video_data = process_cooking_video(video_data)
                    except Exception as e:
                        logging.error(f"Error in process_cooking_video for video {video_id}: {str(e)}", exc_info=True)
                        continue
                    logging.info(f"Processed cooking video data: {json.dumps(video_data, indent=2)}")
                except Exception as e:
                    logging.error(f"Error in process_cooking_video: {str(e)}")
                    continue

                try:
                    try:
                        embed_and_store_in_pinecone(pinecone, video_data)
                    except Exception as e:
                        logging.error(f"Error in embed_and_store_in_pinecone for video {video_id}: {str(e)}", exc_info=True)
                        continue
                    logging.info("Embedded and stored in Pinecone")
                except Exception as e:
                    logging.error(f"Error in embed_and_store_in_pinecone: {str(e)}")
                    continue

            target_playlist = playlist_map.get(category)

            if target_playlist:
                video_data["playlist_name"] = category
                video_data["playlist_id"] = target_playlist['playlist_id']
                video_data["playlist_firebase_id"] = target_playlist['firebase_id']

                try:
                    try:
                        if retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(add_to_playlist)(youtube, video_id, target_playlist['playlist_id'], video_data["title"]):
                            insert_into_firebase(db, video_data)
                            print_video(snippet.get('title'), category)
                            logging.info("Video added to playlist and inserted into Firebase")
                        else:
                            logging.info("Video already in playlist or couldn't be added")
                    except Exception as e:
                        logging.error(f"Error in add_to_playlist or insert_into_firebase for video {video_id}: {str(e)}", exc_info=True)
                        continue
                except Exception as e:
                    logging.error(f"Error in add_to_playlist or insert_into_firebase: {str(e)}")
                    continue
            else:
                logging.warning(f"No target playlist found for category: {category}")

        deselect_cooking_videos()
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logging.info("Video processing script completed")

if __name__ == "__main__":
    main()
