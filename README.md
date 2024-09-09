# YouTube Video Organizer and Recipe Extractor

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Overview](#architecture-overview)
3. [Setup and Installation](#setup-and-installation)
   - [Prerequisites](#prerequisites)
   - [macOS Setup](#macos-setup)
   - [Raspberry Pi Setup](#raspberry-pi-setup)
4. [Obtaining Credentials](#obtaining-credentials)
   - [YouTube API](#youtube-api)
   - [Firebase](#firebase)
   - [OpenAI API](#openai-api)
   - [Pinecone API](#pinecone-api)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)
9. [Contributing](#contributing)
10. [License](#license)

## Project Overview

This project is a YouTube video organizer and recipe extractor. It automatically processes videos from a user's "Watch Later" playlist, categorizes them using a fine-tuned OpenAI model trained on a custom dataset of my videos, and moves them to appropriate playlists. For cooking videos, it extracts recipe information and stores it in a searchable vector database. The system uses AI to classify videos, generate recipes, and create personalized descriptions.

## Architecture Overview

The application consists of several components:

1. **YouTube API Integration**: Fetches video data and manages playlists.
2. **Video Processing**: Uses OpenAI's GPT models to classify videos and extract recipe information.
3. **Database Operations**: Stores processed video data in Firebase.
4. **Vector Database**: Uses Pinecone to store and search recipe embeddings.
5. **Web Automation**: Uses Selenium to interact with YouTube's web interface for certain operations like moving videos from the "Watch Later" playlist to a "Temp Playlist" and then removing the cooking and podcast videos from the WatchLater playlist.

The system flows as follows:
1. Fetch videos from the "Watch Later" playlist.
2. Process each video (classify, extract information).
3. For cooking videos, generate recipe and store in Pinecone.
4. Move the video to the appropriate playlist.
5. Store video data in Firebase.

## Setup and Installation

### Prerequisites

- Python 3.7+
- Google account with YouTube access
- Firebase account
- OpenAI API account
- Pinecone account
- Chrome browser (for web automation)

### macOS Setup

1. Clone the repository:
   ```
   git clone https://github.com/AlexBoudreaux/yt-classifier.git
   cd yt-classifier
   ```

2. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install ChromeDriver if chrome is not installed:
   ```
   brew install --cask chromedriver
   ```

### Raspberry Pi Setup


NOTES: 

NEED TO UPDATE THIS WHOLE PART OF THE README

1. Update and upgrade your Raspberry Pi:
   ```
   sudo apt update && sudo apt upgrade -y
   ```

2. Install required packages:
   ```
   sudo apt install -y python3-pip python3-venv chromium-chromedriver chromium-browser
   ```

3. Clone the repository:
   ```
   git clone https://github.com/AlexBoudreaux/yt-classifier.git
   cd yt-classifier
   ```

4. Create a virtual environment:
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

6. Open Chromium and sign in to YouTube:
   ```
   chromium-browser
   ```

7. Set up Cron Job:
   ```
   chmod +x home/alexboudreaux19/yt-classifier/src/main.py
   ```
  
   ```
   sudo crontab -e
   ```

   Add the following line to run the script at 10:00 PM every day:
   ```
   0 0-23/2 * * * /bin/bash -c 'source /home/alexboudreaux19/yt-classifier/venv/bin/activate && /usr/bin/python3 /home/alexboudreaux19/yt-classifier/src/main.py'
   ```


8. Enable Watchdog Timer:
   ```
   sudo apt install watchdog -y
   sudo nano /etc/watchdog.conf
   ```
   Uncomment these lines in the file:
   ```
   watchdog-device = /dev/watchdog
   max-load-1 = 24
   ```
   Then enable and start the watchdog service:
   ```
   sudo systemctl enable watchdog
   sudo systemctl start watchdog
   ```

9. Set up Automatic Reboots on Network Loss:
   Create a network check script:
   ```
   nano /home/pi/check_internet.sh
   ```
   Add this content to the file:
   ```
   #!/bin/bash

   ping -c 1 google.com > /dev/null 2>&1
   if [ $? -ne 0 ]; then
       sudo reboot
   fi
   ```
   Make the script executable:
   ```
   chmod +x /home/pi/check_internet.sh
   ```
   Add it to the crontab to check every 5 minutes:
   ```
   crontab -e
   ```
   Add this line to the crontab file:
   ```
   */5 * * * * /home/pi/check_internet.sh
   ```


## Obtaining Credentials

### YouTube API

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project.
3. Enable the YouTube Data API v3.
4. Create credentials (OAuth 2.0 Client ID).
5. Download the client configuration and save it as `creds.json` in the project root.

### Firebase

1. Go to the [Firebase Console](https://console.firebase.google.com/).
2. Create a new project.
3. In the project settings, go to "Service Accounts".
4. Generate a new private key and save it as `yt-search-firebase-creds.json` in the project root.

### OpenAI API

1. Go to [OpenAI](https://beta.openai.com/signup/) and sign up for an account.
2. Navigate to the API section and create a new API key.

### Pinecone API

1. Sign up for a [Pinecone account](https://www.pinecone.io/).
2. Create a new project and index.
3. Get your API key from the dashboard.

## Configuration

1. Copy the `.env.sample` file to `.env`:
   ```
   cp .env.sample .env
   ```

2. Edit the `.env` file and fill in your API keys and paths.
    ```
    The yt-search-firebase-creds.json file should be in the src directory of the project.
    ```

## Running the Application

To run the application:

```
python src/main.py
```

For Raspberry Pi, the application should start automatically on boot due to the systemd service we set up. To manually control the service:

- Start: `sudo systemctl start youtube-organizer.service`
- Stop: `sudo systemctl stop youtube-organizer.service`
- Restart: `sudo systemctl restart youtube-organizer.service`
- Check status: `sudo systemctl status youtube-organizer.service`

## Testing

To test a single video:
```
python misc_src/test_single_video.py
```

## Troubleshooting

- If you encounter authentication issues, ensure your `token.json` file is up to date.
- For Selenium issues, make sure you have the correct ChromeDriver version installed.
- Check the `video_processing.log` file for detailed error messages.
- All tokens, keys and creds can be found in my Google Drive at: [Google Drive Folder](https://drive.google.com/drive/u/0/folders/1LU-9b3goAsTC7Myj92tMJldeXhirgEdU)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.