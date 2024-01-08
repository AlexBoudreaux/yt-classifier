import json
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import extract
import os
import openai

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

def main():

    # Load playlists
    with open('playlists.json', 'r') as file:
        playlists = json.load(file)

    training_data = []

    youtube = get_authenticated_service()

    for playlist in playlists:
        playlist_id = playlist["Playlist ID"]

        # Print playlist name
        print(f"Playlist name: {playlist['Playlist Name']}")

        # Get videos from playlist
        request = youtube.playlistItems().list(
            part='snippet',
            maxResults=50,
            playlistId=playlist_id
        )

        response = request.execute()

        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']

            # # Print video title
            # print(f"Video title: {item['snippet']['title']}")
            
            # Transcribe the video
            try:
                transcription = transcribe_video(video_id)

                # Summarize the transcription using the OpenAI API
                completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo-16k-0613",
                    messages=[
                        {"role": "system", "content": "You will provided the first 1000 words of a Youtube video transcription. Please create a short summary of the video."},
                        {"role": "user", "content": transcription},
                    ]
                )

                summary = completion.choices[0].message["content"]

            except:
                summary = "No summary available."

            # Video description
            description_text = item['snippet']['description']
            description = " ".join(description_text.split()[:500])

            # Append to training data
            training_data.append({
                "prompt": {
                    "Video Name": item['snippet']['title'],
                    "Creator": item['snippet']['videoOwnerChannelTitle'],
                    "Description": description,
                    "Summary": summary
                },
                "completion": playlist['Playlist Name']
            })

    print(training_data)


    # # Save training data
    # with open('training-data.txt', 'w') as file:
    #     for item in training_data:
    #         file.write(json.dumps(item) + '\n')

    # print("Training data has been saved.")

if __name__ == "__main__":
    main()
