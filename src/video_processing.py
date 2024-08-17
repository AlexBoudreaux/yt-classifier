from youtube_transcript_api import YouTubeTranscriptApi
import openai

def process_video(video_id, snippet):
    video_data = {
        'video_id': video_id,
        'title': snippet.get('title', ''),
        'description': snippet.get('description', ''),
        'creator': snippet.get('videoOwnerChannelTitle', '')
    }
    
    # Transcribe video
    video_data['transcript'] = transcribe_video(video_id, video_data['title'])
    
    # Summarize video
    video_data['summary'] = summarize_video(video_data['title'], video_data['transcript'])
    
    return video_data

def transcribe_video(video_id, video_title):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_words = [i["text"].replace("\xa0", "").replace("\n", " ") for i in transcript_data]
        return " ".join(transcript_words[:1000])  # Limit to first 1000 words
    except:
        print(f"Video {video_title} could not be transcribed.")
        return "Transcription not available."

def summarize_video(video_title, transcription):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube video transcripts."},
                {"role": "user", "content": f"Please summarize the following video transcript in a concise paragraph:\n\n{transcription}"}
            ]
        )
        return completion.choices[0].message["content"].strip()
    except:
        print(f"Video {video_title} could not be summarized.")
        return "Summary not available."

def classify_video(video_data):
    pass

def process_cooking_video(video_data):
    pass

def transcribe_video(video_id, video_title):
    pass

def summarize_video(video_title, transcription):
    pass

def generate_recipe(video_data):
    pass

def create_personalized_description(video_data):
    pass

def assign_food_categories(video_data):
    pass
