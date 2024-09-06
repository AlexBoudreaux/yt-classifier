import logging
from youtube_operations import get_authenticated_service, add_to_playlist, print_video, video_exists_in_playlists
from video_processing import process_video, classify_video, process_cooking_video
from database_operations import get_playlist_map, insert_into_firebase
from firebase_init import initialize_firebase
from pinecone_operations import initialize_pinecone, embed_and_store_in_pinecone
from config import OPENAI_API_KEY
import openai
import json

# Configure OpenAI API
openai.api_key = OPENAI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_single_video():
    logging.info("Starting single video test")
    try:
        # Setup
        db = initialize_firebase()
        youtube = get_authenticated_service()
        pinecone = initialize_pinecone()

        # Get playlist map
        playlist_map = get_playlist_map(db)
        
        # Specify a test video ID
        test_video_id = "SVJ9WYsBBkU"  # Replace with an actual video ID you want to test
        
        # Fetch video details
        video_details = youtube.videos().list(
            part="snippet",
            id=test_video_id
        ).execute()

        if not video_details['items']:
            logging.error(f"No video found with ID: {test_video_id}")
            return

        snippet = video_details['items'][0]['snippet']
        logging.info(f"Snippet received: {snippet}")

        # Check if video already exists in any playlist
        if video_exists_in_playlists(youtube, playlist_map, test_video_id):
            logging.info("Video already exists in a playlist")
            return

        # Process video
        video_data = process_video(test_video_id, snippet)
        logging.info(f"Processed video data: {video_data}")

        classification_result = classify_video(video_data)
        print(classification_result)
        category = classification_result.split('<video_classification>')[1].split('</video_classification>')[0].strip().strip('"')
        logging.info(f"Classified as: {category}")

        if category.lower() == "cooking":
            logging.info("Entering cooking video processing")
            video_data["url"] = f"https://www.youtube.com/watch?v={test_video_id}"
            try:
                video_data = process_cooking_video(video_data)
                logging.info(f"Processed cooking video data: {json.dumps(video_data, indent=2)}")
            except Exception as e:
                logging.error(f"Error in process_cooking_video: {str(e)}")
                return

            try:
                embed_and_store_in_pinecone(pinecone, video_data)
                logging.info("Embedded and stored in Pinecone")
            except Exception as e:
                logging.error(f"Error in embed_and_store_in_pinecone: {str(e)}")
                return

        target_playlist = playlist_map.get(category)

        if target_playlist:
            video_data["playlist_name"] = category
            video_data["playlist_id"] = target_playlist['playlist_id']
            video_data["playlist_firebase_id"] = target_playlist['firebase_id']

            try:
                if add_to_playlist(youtube, test_video_id, target_playlist['playlist_id'], video_data["title"]):
                    insert_into_firebase(db, video_data)
                    print_video(snippet.get('title'), category)
                    logging.info("Video added to playlist and inserted into Firebase")
                else:
                    logging.info("Video already in playlist or couldn't be added")
            except Exception as e:
                logging.error(f"Error in add_to_playlist or insert_into_firebase: {str(e)}")
                return
        else:
            logging.warning(f"No target playlist found for category: {category}")

    except Exception as e:
        logging.error(f"An error occurred: {str(e)}", exc_info=True)
    finally:
        logging.info("Single video test completed")

if __name__ == "__main__":
    test_single_video()
