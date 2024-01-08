import os
from datetime import datetime
from rich import print
import sys

from supabase import create_client
# from openai import OpenAI
import openai

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import time
from selenium import webdriver

# Configuration
DEVELOPER_KEY = "AIzaSyComDNKoDV8ODeb2PJ8a7y-IErz732PuTQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

PROFILE_PATH = "/Users/alexboudreaux/Library/Application Support/Google/Chrome/Default"

# client = OpenAI(api_key="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")
openai.api_key = "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"

def add_watchlater_to_temp():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument(f"user-data-dir={PROFILE_PATH}")

    driver = webdriver.Chrome(options=chrome_options)

    # # Navigate to Watch Later playlist
    driver.get('https://www.youtube.com/playlist?list=WL')

    # Here's your JavaScript code as a multi-line string
    js_code = """
    var videoIndex = 0;
    var consecutiveAddedCount = 0;

    function randomDelay(min, max) {
        return Math.random() * (max - min) + min;
    }

    function findStartingPoint() {
        var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
        if (videoIndex >= videos.length) {
            console.log('All videos processed in findStartingPoint');
            return;
        }

        var video = videos[videoIndex];
        video.querySelector('#primary button[aria-label="Action menu"]').click();

        setTimeout(function() {
            var saveButton = document.evaluate(
                '//yt-formatted-string[contains(text(),"Save to playlist")]',
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            ).singleNodeValue;

            if (saveButton) {
                saveButton.click();

                setTimeout(function() {
                    var tempPlaylistCheckbox = document.evaluate(
                        '//yt-formatted-string[contains(text(),"Temp Playlist")]/ancestor::tp-yt-paper-checkbox',
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;

                    if (tempPlaylistCheckbox && tempPlaylistCheckbox.getAttribute('aria-checked') === 'true') {
                        consecutiveAddedCount++;
                        if (consecutiveAddedCount >= 5) {
                            console.log('Found starting point at video index:', videoIndex - 4); // Adjusting for 0-based index and to go 5 videos up
                            videoIndex -= 5;  // Adjust to the starting point for adding videos
                            addVideosToTemp();  // Start the second function
                            return;
                        }
                    } else {
                        consecutiveAddedCount = 0;  // Reset the counter if a video not in Temp Playlist is found
                    }
                    videoIndex++;
                    findStartingPoint();
                }, randomDelay(1000, 2000));
            } else {
                console.log('Save to playlist button not found at video index:', videoIndex);
                videoIndex++;
                findStartingPoint();
            }
        }, randomDelay(1000, 2000));
    }

    function addVideosToTemp() {
        if (videoIndex < 0) {
            console.log('All videos processed');
            window.scriptCompleted = true;
            return;
        }

        var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
        var video = videos[videoIndex];
        video.querySelector('#primary button[aria-label="Action menu"]').click();

        setTimeout(function() {
            var saveButton = document.evaluate(
                '//yt-formatted-string[contains(text(),"Save to playlist")]',
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            ).singleNodeValue;

            if (saveButton) {
                saveButton.click();

                setTimeout(function() {
                    var tempPlaylistButton = document.evaluate(
                        '//yt-formatted-string[contains(text(),"Temp Playlist")]/ancestor::tp-yt-paper-checkbox',
                        document,
                        null,
                        XPathResult.FIRST_ORDERED_NODE_TYPE,
                        null
                    ).singleNodeValue;

                    if (tempPlaylistButton) {
                        tempPlaylistButton.click();

                        setTimeout(function() {
                            var exitButton = document.querySelector('button[aria-label="Cancel"]');
                            if (exitButton) {
                                exitButton.click();
                                videoIndex--;
                                addVideosToTemp();  // Move to the previous video and continue
                            } else {
                                console.log('Exit button not found');
                            }
                        }, randomDelay(1000, 2000));
                    } else {
                        console.log('Temp Playlist button not found');
                    }
                }, randomDelay(1000, 2000));
            } else {
                console.log('Save to playlist button not found');
            }
        }, randomDelay(1000, 2000));
    }

    findStartingPoint();  // Start the first function
    """

    # Execute the JavaScript code
    driver.execute_script(js_code)

    def is_script_completed():
        return driver.execute_script("return window.scriptCompleted;")

    # Wait for the JavaScript code to complete
    while not is_script_completed():
        time.sleep(1)  # Check every second

def setup_supabase():
    url = "https://bbrcyfqrvwqbboudayre.supabase.co"
    key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJicmN5ZnFydndxYmJvdWRheXJlIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTQ1Nzc0MzAsImV4cCI6MjAxMDE1MzQzMH0.SPNLpnm_cIHUdYMOKOK4d56VmgfNpuTComWRigMBwTg"
    return create_client(url, key)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_authenticated_service():
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    creds = None

    token_json_path = resource_path('token.json')
    creds_json_path = resource_path('creds.json')

    # Load the credentials from the 'token.json' if it exists
    if os.path.exists(token_json_path):
        creds = Credentials.from_authorized_user_file(token_json_path, SCOPES)

    # If the credentials are not valid, authenticate through OAuth2
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_json_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials to 'token.json'
        with open(token_json_path, "w") as token:
            token.write(creds.to_json())

    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=creds, cache_discovery=False)

def transcribe_video(video_id, video_title):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_words = [i["text"].replace("\xa0", "").replace("\n", " ") for i in transcript_data]
        transcription = " ".join(transcript_words[:1000])  # Take the first 1000 words
        return transcription # Truncate after 1000 words
    except :
        transcription = "Transcription not available."
        # Print the video name with "x" emoji
        print(f"\N{cross mark} Video {video_title} could not be transcribed.")
        return transcription
    
def summarize_video(video_title, transcription):
    try:
        completion = openai.ChatCompletion.create(model="gpt-3.5-turbo-16k-0613",
        messages=[
            {"role": "system", "content": "You will be provided the first 1000 words of a Youtube video transcription. Please create a short summary of the video."},
            {"role": "user", "content": transcription},
        ])
        summary = completion.choices[0].message["content"]
        return summary
    except:
        summary = "Summary not available."
        print(f"\N{cross mark} Video {video_title} could not be summarized.")
        return summary
    
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

def classify_video(video_data):
    try:
        # Prepare the content in a more readable format
        user_message_content = f"""
        Title: {video_data['title']}
        Creator: {video_data['creator']}
        Description: {video_data['description']}
        Summary: {video_data['summary']}
        """
        
        classification_completion = openai.ChatCompletion.create(model="ft:gpt-3.5-turbo-0613:personal::7tMpsDay",
        messages=[
            {
                "role": "system",
                "content": "You are a Youtube Video Classifier. You will be fed a Youtube video Title, Description, Transcript, and Summary and you will output the classification of the video. The possible classifications are \"Cooking\", \"Late Night Jammers\", \"Shows\", \"Development\", \"Podcast/Comedy\", \"Woodworking/DIY\", \"Arduino/Pi/SmartHome\", \"Work/Growth\", \"Finance\", \"Gaming\", \"Science/History\", \"AI\", \"Startup/Business\" or if you are not sure enough respond with \"Misc.\". You will be scored on how well you classify the videos. Only respond with one of those classifications or \"Misc.\"."
            },
            {
                "role": "user",
                "content": user_message_content
            }
        ])
        
        classification = classification_completion.choices[0].message["content"]
        return classification

    except Exception as e:
        print(f"An error occurred while classifying the video: {str(e)}")
        return "Misc."  # Fallback category

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

def update_playlists_with_videos(youtube, playlists):
    for pl in playlists:
        playlist_id = pl.get('Playlist ID', '')
        if playlist_id:  # Check to make sure there's a playlist ID
            video_data = fetch_videos_from_playlist(youtube, playlist_id)
            video_ids = [vid['snippet']['resourceId']['videoId'] for vid in video_data]
            pl['Videos'] = video_ids
            pl['videos_num'] = len(video_ids)

def print_video(video_title, category):
    print(f"[green]✓[/green] [bold blue]{video_title}[/bold blue]   ->   playlist: [magenta]{category}[/magenta]")

def insert_into_supabase(supabase, video_data):
    # Fetch the id from the playlists table based on the playlist_id
    response = supabase.table('playlists').select('id').eq('playlist_id', video_data['playlist_id']).execute()
    
    # Extract the id from the response, handle cases where data is empty or None
    playlist_fk_id = None
    if response.data and len(response.data) > 0:
        playlist_fk_id = response.data[0].get('id')

    if not playlist_fk_id:
        print(f"Error: No matching playlist found for playlist_id: {video_data['playlist_id']}")
        return None

    # Prepare data to insert into the videos table
    data = {
        "playlist_id_fk": playlist_fk_id,
        "category": video_data['playlist_name'],
        "playlist_id": video_data['playlist_id'],
        "video_id": video_data['video_id'],
        "video_name": video_data['title'],
        "creator": video_data['creator'],
        "description": video_data['description'],
        "transcript": video_data['transcript'],
        "summary": video_data['summary'],
        "date_added_to_playlist": datetime.utcnow().isoformat(),
        "embedding": video_data.get('embedding', None)
    }

    # Insert into the videos table
    response = supabase.table('videos').insert(data).execute()
    return response

def get_all_videos(supabase, page_size=1000):
    all_videos = []
    start_idx = 0

    while True:
        table = supabase.table('videos')
        response = table.select('*').range(start_idx, start_idx + page_size - 1).execute()
        
        # Directly accessing the data from the response object
        videos_chunk = response.data
        
        if not videos_chunk:
            break

        all_videos.extend(videos_chunk)
        start_idx += page_size

    return all_videos

def compute_embedding_for_video(video_data, max_tokens=8192, model="text-embedding-ada-002"):
    # Combine text fields from video_data
    combined_text = f"{video_data['title']} by {video_data['creator']} {video_data['description']} {video_data['summary']} {video_data['transcript']}"

    # Replace newlines and truncate text if necessary
    combined_text = combined_text.replace("\n", " ")
    tokens = combined_text.split()
    if len(tokens) > max_tokens:
        combined_text = ' '.join(tokens[:max_tokens])

    # Compute the embedding
    try:
        response = openai.Embedding.create(input=[combined_text], model=model)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error during API call: {e}")
        return None

def main():

    add_watchlater_to_temp()

    supabase = setup_supabase()

    # Get playlist_map from Supabase
    playlist_map = {}
    response = supabase.table('playlists').select('playlist_name, playlist_id').execute()
    for pl in response.data:
        playlist_map[pl['playlist_name']] = pl['playlist_id']

    youtube = get_authenticated_service()

    temp_playlist_id = playlist_map.get('Temp Playlist', '')
    if not temp_playlist_id:
        print("Temp Playlist not found.")
        return

    # Fetch videos from the temp playlist and reverse the order
    temp_videos = fetch_videos_from_playlist(youtube, temp_playlist_id)[::-1]

    saved_videos = get_all_videos(supabase)

    for video in temp_videos:
        snippet = video.get('snippet', {})
        video_id = snippet.get('resourceId', {}).get('videoId', '')

        # Check if video is a "Private" or "Deleted" video
        if snippet.get('title') == "Private video" or snippet.get('title') == "Deleted video":
            continue

        # Check if video_id and if the video_id is already in 
        if video_id and not any(v['video_id'] == video_id for v in saved_videos):
            
            # Transcribe the video
            transcription = transcribe_video(video_id, snippet.get("title"))

            # Summarize the video
            summary = summarize_video(snippet.get("title"), transcription)

            # Truncate the description to 250 words
            description = " ".join(video['snippet']['description'].split()[:250])
            
            # Create new Video object
            video_data = {
                "video_id": video_id,
                "title": snippet.get("title"),
                "creator": snippet.get("videoOwnerChannelTitle"),
                "description": description,
                "transcript": transcription,
                "summary": summary
            }

            # Classify the video
            category = classify_video(video_data)[1:-1]

            # If the video is a cooking video, embed it and store with the embedding
            if category == "Cooking":
                # Embed the video
                embedding = compute_embedding_for_video(video_data)
                video_data["embedding"] = embedding

            target_playlist_id = playlist_map.get(category)

            if target_playlist_id:
                # add playlist name and id to video_data object
                video_data["playlist_name"] = category
                video_data["playlist_id"] = target_playlist_id

                # If add_to_playlist is successful, insert into supabase
                if (add_to_playlist(youtube, video_id, target_playlist_id, video_data["title"])):
                    insert_into_supabase(supabase, video_data)
                    print_video(snippet.get('title'), category)

if __name__ == "__main__":
    main()
