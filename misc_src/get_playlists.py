from googleapiclient.discovery import build

DEVELOPER_KEY = "AIzaSyComDNKoDV8ODeb2PJ8a7y-IErz732PuTQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def get_authenticated_service():
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

# Create the YouTube API client
youtube = get_authenticated_service()

# Call the playlists.list method to retrieve the user's public playlists (channel ID required)
channel_id = 'UCFjc7d6ePwwneu38jl0DKug'
request = youtube.playlists().list(
    part='snippet',
    channelId=channel_id,
    maxResults=25
)

response = request.execute()

# Print the names and IDs of the playlists
print(f"You have {len(response['items'])} public playlists:")
print('-' * 60)
print(f"{'Playlist Name':<40} | {'Playlist ID'}")
print('-' * 60)
for item in response['items']:
    print(f"{item['snippet']['title'][:37]:<40} | {item['id']}")
print('-' * 60)
