import json
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract
import os
import openai

###############***************################
# model name: ft:gpt-3.5-turbo-0613:personal::7tMpsDay
###############***************################

DEVELOPER_KEY = "AIzaSyComDNKoDV8ODeb2PJ8a7y-IErz732PuTQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

openai.organization = "org-T6bYvYJr8ulggtQqe0MnmbmL"
openai.api_key = "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"


def get_authenticated_service():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def transcribe_video(video_id):
    transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_words = [i["text"].replace("\xa0", "").replace("\n", " ") for i in transcript_data]
    truncated_transcript = " ".join(transcript_words[:1000])  # Take the first 1000 words
    return truncated_transcript # Truncate after 1000 words

def add_to_food_playlist(youtube, video_id, food_playlist_id):
    youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": food_playlist_id,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": video_id
                }
            }
        }
    ).execute()


def main():

    # Load playlists
    with open('playlists.json', 'r') as file:
        playlists = json.load(file)

    data = []

    youtube = get_authenticated_service()
    food_playlist_id = 'PLZyXQ3RMIWiFa3DSYm1yTce-sbGUT2OZV'# Replace with the actual Food Playlist ID
    temp_playlist_id = 'PLZyXQ3RMIWiFjebCO49yXWpZ_q555zP5u'

    # CHANGE: Only loop "Temp Playlist"
    for playlist in playlists:
        if playlist['Playlist Name'] == 'Temp Playlist':
            playlist_id = playlist["Playlist ID"]

            # Print playlist name
            print(f"Playlist name: {playlist['Playlist Name']}")

            # Get videos from playlist
            request = youtube.playlistItems().list(
                part='snippet',
                maxResults=50,  # This is the maximum allowed value
                playlistId=temp_playlist_id
            )

            while request:
                response = request.execute()

                for item in response['items']:
                    video_id = item['snippet']['resourceId']['videoId']
                
                    # Transcribe the video
                    # try:
                    #     transcription = transcribe_video(video_id)

                    #     # Summarize the transcription using the OpenAI API
                    #     completion = openai.ChatCompletion.create(
                    #         model="gpt-3.5-turbo-16k-0613",
                    #         messages=[
                    #             {"role": "system", "content": "You will provided the first 1000 words of a Youtube video transcription. Please create a short summary of the video."},
                    #             {"role": "user", "content": transcription},
                    #         ]
                    #     )

                    #     summary = completion.choices[0].message["content"]

                    # except:
                    #     summary = "No summary available."

                    # Video description
                    description_text = item['snippet']['description']
                    description = " ".join(description_text.split()[:500])

                    # TODO: Feed to chatgpt to get classification using gpt-3.5-turbo-16k-0613
                    user_content = {
                        "Video Name": item['snippet']['title'],
                        "Creator": item['snippet']['videoOwnerChannelTitle'],
                        "Description": description,
                        # "Summary": summary
                    }

                    classification_completion = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-16k-0613", # Replace with the actual fine-tuned model name
                        messages=[
                            {
                                "role": "system",
                                "content": "You are a Youtube Video Classifier. You will be fed a Youtube video Title, Description, Transcript, and Summary and you will output the classification of the video. The possible classifications are \"Cooking\", \"Late Night Jammers\", \"Shows\", \"Development\", \"Podcast/Comedy\", \"Woodworking/DIY\", \"Arduino/Pi/SmartHome\", \"Work/Growth\", \"Finance\", \"Gaming\", \"Science/History\", \"AI\", \"Startup/Business\" or if you are not sure enough respond with \"Misc.\". You will be scored on how well you classify the videos. Only respond with one of those classifications or \"Misc.\"."
                            },
                            {
                                "role": "user",
                                "content": json.dumps(user_content)
                            }
                        ]
                    )
                    classification = classification_completion.choices[0].message["content"]

                    # TODO: If the video is food related, Save video to Food Playlist
                    if classification == "cooking": # Modify the condition based on your specific classification results
                        add_to_food_playlist(youtube, video_id, food_playlist_id)
                        print(f"Video {item['snippet']['title']} added to Cooking Playlist.")

                if 'nextPageToken' in response:
                    request = youtube.playlistItems().list(
                        part='snippet',
                        maxResults=50,
                        playlistId=temp_playlist_id,
                        pageToken=response['nextPageToken']
                    )
                else:
                    request = None  # No more results


    print("Done.")


if __name__ == "__main__":
    main()
