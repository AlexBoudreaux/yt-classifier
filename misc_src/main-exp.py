import os
from datetime import datetime
from rich import print
import sys
import json
from dotenv import load_dotenv

import openai
from youtube_transcript_api import YouTubeTranscriptApi
from supabase import create_client
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pinecone import Pinecone

import logging

logging.basicConfig(filename='video_processing.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

import time
from selenium import webdriver

# Configuration
DEVELOPER_KEY = "AIzaSyComDNKoDV8ODeb2PJ8a7y-IErz732PuTQ"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

PROFILE_PATH = "/Users/alexboudreaux/Library/Application Support/Google/Chrome/Default"

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

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

def deselect_cooking_videos():
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
    var cookingVideosRemoved = 0;

    function randomDelay(min, max) {
    return Math.random() * (max - min) + min;
    }

    function deselectWatchLater() {
    var videos = document.getElementsByTagName('ytd-playlist-video-renderer');
    if (videoIndex >= videos.length) {
        console.log('All videos processed');
        console.log('Total cooking videos removed from Watch Later:', cookingVideosRemoved);
        return;
    }
    var video = videos[videoIndex];
    video.querySelector('#primary button[aria-label="Action menu"]').click();
    setTimeout(() => {
        var saveButton = document.evaluate(
        '//yt-formatted-string[contains(text(),"Save to playlist")]',
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
        ).singleNodeValue;
        if (saveButton) {
        saveButton.click();
        setTimeout(() => {
            var cookingPlaylistCheckbox = document.evaluate(
            '//yt-formatted-string[contains(text(),"Cooking")]/ancestor::tp-yt-paper-checkbox',
            document,
            null,
            XPathResult.FIRST_ORDERED_NODE_TYPE,
            null
            ).singleNodeValue;
            if (cookingPlaylistCheckbox && cookingPlaylistCheckbox.getAttribute('aria-checked') === 'true') {
            var watchLaterCheckbox = document.querySelector('ytd-playlist-add-to-option-renderer tp-yt-paper-checkbox[checked] #label[title="Watch later"]');
            if (watchLaterCheckbox) {
                watchLaterCheckbox.click();
                console.log('Cooking video removed from Watch Later at index:', videoIndex);
                cookingVideosRemoved++;
                setTimeout(() => {
                var closeButton = document.querySelector('yt-icon-button[icon="close"], button[aria-label="Close"]');
                if (!closeButton) {
                    closeButton = document.querySelector('button[aria-label="Cancel"]');
                }
                if (closeButton) {
                    closeButton.click();
                }
                videoIndex++;
                setTimeout(deselectWatchLater, randomDelay(1000, 2000)); // Process next video after a delay
                }, randomDelay(500, 1500)); // Wait for the checkbox interaction
            } else {
                closeSaveMenuAndProceed();
            }
            } else {
            closeSaveMenuAndProceed();
            }
        }, randomDelay(1000, 2000));
        } else {
        videoIndex++;
        deselectWatchLater();
        }
    }, randomDelay(500, 1000));
    }

    function closeSaveMenuAndProceed() {
    var closeButton = document.querySelector('yt-icon-button[icon="close"], button[aria-label="Close"]');
    if (!closeButton) {
        closeButton = document.querySelector('button[aria-label="Cancel"]');
    }
    if (closeButton) {
        closeButton.click();
    }
    videoIndex++;
    setTimeout(deselectWatchLater, randomDelay(1000, 2000)); // Proceed to next video after a delay
    }

    deselectWatchLater(); // Start the script
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

def get_authenticated_service():
    SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build("youtube", "v3", credentials=creds)

def initialize_pinecone():
    return Pinecone(api_key="2620e8ef-afe4-44a2-907d-a340565666d0")

def process_video(video_id, snippet):
    transcription = transcribe_video(video_id, snippet.get("title"))
    summary = summarize_video(snippet.get("title"), transcription)
    description = " ".join(snippet.get('description', '').split()[:500])

    return {
        "video_id": video_id,
        "title": snippet.get("title"),
        "creator": snippet.get("videoOwnerChannelTitle"),
        "description": description,
        "transcript": transcription,
        "summary": summary,
        "url": f"https://www.youtube.com/watch?v={video_id}"
    }

def process_cooking_video(video_data):
    try:
        # Generate recipe
        recipe = generate_recipe(video_data)
        video_data["recipe"] = recipe
        
        # Assign food categories
        food_categories = assign_food_categories(video_data)
        video_data["food_category"] = food_categories
        
        # Create personalized description
        personalized_description = create_personalized_description(video_data)
        video_data["personalized_description"] = personalized_description

        return video_data
    except Exception as e:
        logging.error(f"Error in process_cooking_video: {str(e)}")
        raise

def transcribe_video(video_id, video_title):
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_words = [i["text"].replace("\xa0", "").replace("\n", " ") for i in transcript_data]
        return " ".join(transcript_words[:1000])
    except:
        print(f"\N{cross mark} Video {video_title} could not be transcribed.")
        return "Transcription not available."

def generate_recipe(video_data):
    def create_system_prompt():
        system_prompt = """
        You are an expert chef and food writer. I will provide you with details from a cooking video, including the name, description, and transcript of the video. Your task is to create a detailed recipe based on the provided information. Follow the template below to format the recipe. If the video includes multiple dishes, create separate sections for each dish.

        Provide a formatted shopping list for the recipe broken up by section of the grocery along with the amount needed. Use these categories: Produce, Dairy, Meat & Seafood, Bakery, Canned Goods, Dry Goods & Pasta, Snacks, Frozen Foods, Beverages, Pantry Staples or any other that need to be added.

        Then provide the ingredients for the recipe broken down by components of the overall dish along with the amount. For instance have section for the main dish and then the sauce and then the garnish. 
        
        Then provide the steps need to take for the recipe in an ordered list.

        Lastly, provide any notes about the recipe that the cook might need to know.

        Please use clear and concise language suitable for intermediate level home cooks. Strictly follow the template given below and only output the information requested. 

        And if the transcript and data provide don't not give enough information for a recipe than return "No Recipe Available".

        The dish name does not have to be the title of the video but can be a direct name of the dish shown.
        And output nothing after the recipe. 

        **Example Output:**

        **Ultimate Seafood Tower**

        **Shopping list:**

        * Produce:
        - Lemons, 2
        - Parsley, 1 bunch

        * Dairy:
        - Butter, 1/2 cup

        * Meat & Seafood:
        - Lobster tails, 2
        - Shrimp, 1 lb
        - Oysters, 12

        * Pantry Staples:
        - Salt, 1 tsp
        - Sugar, 1 tbsp

        **Ingredients:**

        - Main Dish:
        - Lobster tails, 2
        - Shrimp, 1 lb
        - Oysters, 12
        - Lemons, 2 sliced

        - Sauce:
        - Butter, 1/2 cup
        - Salt, 1 tsp
        - Sugar, 1 tbsp

        *1. Prepare the Seafood:*
        - **Lobster:** Boil or steam the lobster tails until fully cooked. Chill and split in half.
        - **Shrimp:** Poach the shrimp in simmering salted water until pink. Immediately submerge in ice water to chill.
        - **Crab:** Steamed or cooked as desired, cracked for easy access.
        - **Mussels:** Source pre-smoked mussels or smoke them yourself.
        - **Oysters:** Cryo-shuck using liquid nitrogen or manually shuck as detailed in the transcript.
        - **Tuna Confit:** Brine tuna in salt, sugar, and water mixture for 30–40 minutes. Cook using sous vide at a precise temperature, chill and cut just prior to serving.
        - **Scallops:** Cure the scallops between kombu and season with lemon, olive oil, lemon zest, parsley, and chili flakes.
        - **Salmon Mi-Cuit:** Prepare as outlined in the separate link, cooking to buttery, flaky texture.
        - **Octopus:** Sous vide the octopus at 75°C for 5 hours. Dress with a ramp, mint, and parsley pesto.
        - **Geoduck:** Thinly slice for crudo and serve raw.

        *2. Prepare Sauces:*
        - **Cocktail Sauce:** Blend together ketchup, horseradish, tomato paste, rice vinegar, chopped Fresno pepper, chopped shallots, lemon zest, and salt to taste. Refrigerate until ready to use.

        *3. Potato Chips (Optional):*
        - Slice potatoes thin using a mandolin, fry at 300°F until golden and crispy, season with fine salt.

        *4. Building the Seafood Tower:*
        - Start with a sturdy base such as yoga mat slices to prevent slipping.
        - On each tier layer a bed of dry ice and rock salt to keep the seafood cold.
        - Use layers of ice and place ingredients strategically for visual appeal and convenience.
        - Add the cooked and chilled seafood. Garnish with lemon slices and a sprig of parsley.

        **Notes:**
        - Make sure to serve the seafood fresh and cold.

        <br />
        <br />
        <br />

        **Flour Tortillas**

        **Shopping list:**

        * Dairy:
        - Butter, 1/2 cup

        * Dry Goods & Pasta:
        - All-purpose flour, 2 cups

        * Pantry Staples:
        - Salt, 1 tsp
        - Water, 3/4 cup (warm)

        **Ingredients:**

        - Main Dish:
        - All-purpose flour, 2 cups
        - Butter, 1/2 cup, softened
        - Salt, 1 tsp
        - Warm water, 3/4 cup

        *1. Combine Dry Ingredients:*
        - In a bowl, combine the 2 cups of all-purpose flour and 1 tsp of salt.

        *2. Incorporate Butter:*
        - Add the softened 1/2 cup of butter to the flour mixture.
        - Mix thoroughly until the mixture resembles coarse crumbs.

        *3. Add Water and Knead:*
        - Gradually add the 3/4 cup of warm water to the mixture while continuously mixing.
        - Knead the mixture until a smooth and elastic dough forms.

        *4. Rest the Dough:*
        - Cover the dough with a towel and let it rest for 10 minutes to allow the gluten to relax and the dough to become more pliable.

        *5. Divide and Roll:*
        - After resting, divide the dough into small, equal-sized balls.
        - Lightly flour your work surface and rolling pin.
        - Roll out each ball into a thin, round tortilla, aiming for a 7-inch diameter, ensuring even thickness.

        *6. Cook Tortillas:*
        - Preheat a cast-iron griddle or skillet over medium heat.
        - Lightly oil the surface and wipe off any excess with a dry towel.
        - Cook each tortilla on the preheated skillet. When bubbles start to form on the surface, flip the tortilla.
        - Cook each side until golden brown spots appear. Ensure not to overcook, as this will make the tortillas dry and tough.

        *7. Keep Warm:*
        - Keep the cooked tortillas warm by wrapping them in a clean towel. This helps maintain their softness and elasticity.

        **Notes:**
        - Using warm water helps the gluten develop faster, resulting in fluffier tortillas.
        - If the dough feels too wet or sticky, add a little more flour; if it's too dry, add a bit more water.
        - Consistently flipping the tortillas while rolling them out ensures even thickness and prevents the edges from becoming too thin and burning.
        - Store the tortillas in an airtight container or wrapped in a towel to keep them warm and tender until ready to serve.
        """
        return system_prompt

    def create_recipe_prompt(video_data):
        prompt_template = """
        Here is the video details I would like a formatted recipe for:

        <Title> {title} </Title>
        <Description> {description} </Description>
        <Creator> {creator} </Creator>
        <Transcript> {transcript} </Transcript>
        """

        user_prompt = prompt_template.format(
            title=video_data['title'],
            description=video_data['description'],
            creator=video_data['creator'],
            transcript=video_data['transcript']
        )

        return user_prompt

    try:
        system_prompt = create_system_prompt()
        user_prompt = create_recipe_prompt(video_data)

        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )
        recipe = completion.choices[0].message["content"].strip()
        return recipe if recipe != "No Recipe Available" else "Recipe not available."
    except Exception as e:
        print(f"\N{cross mark} Recipe could not be generated for {video_data['title']}. Error: {e}")
        return "Recipe not available."

def create_personalized_description(video_data):
    prompt = f"""
    Create a personalized description for this cooking video:
    <Title> {video_data['title']} </Title>
    <Creator> {video_data['creator']} </Creator>
    <Description> {video_data['description']} </Description>
    <Summary> {video_data['summary']} </Summary>
    <Recipe> {video_data.get('recipe', 'No recipe available')} </Recipe>
    
    Include the main dish, cuisine type, course type, and what it pairs well with.
    """
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a culinary content specialist. Based on the provided video data, generate a personalized description for each video and its recipe. The personalized description should include:

                      1. The main dish(s) of the video and any side components.
                      2. The cuisine of the dish(s) (can be multiple).
                      3. The course of the dish (e.g., side, entree, dessert, etc.).
                      4. What other dishes the dish would pair well with (e.g., if it's a grilled side, the pairing would be grilled entrees).
                      5. Whether the video is focused on a technique, a recipe, or a combination of both. If it includes a technique, provide a brief description of the technique.

                      The output should very direct with no exuberant adjectives. The goal is to show the contents of the video, the dishes, and how the dishes would be connected to other dishes. This will be used for semantic searches on these videos to find recipes.
                      Write the response in mulit-sentence form."""},
                {"role": "user", "content": prompt},
            ]
        )
        return completion.choices[0].message["content"]
    except:
        print(f"\N{cross mark} Personalized description could not be generated for {video_data['title']}.")
        return "Personalized description not available."

def assign_food_categories(video_data):
    prompt = f"""
    Assign food categories to this cooking video:
    <Title> {video_data['title']} </Title>
    <Creator> {video_data['creator']} </Creator>
    <Description> {video_data['description']} </Description>
    <Summary> {video_data['summary']} </Summary>
    <Recipe> {video_data.get('recipe', 'No recipe available')} </Recipe>
    
    Provide categories as a JSON array. Use only these categories: "Entree", "Side Dish", "Dessert", "Beverage", "Appetizer", "Snack", "Soup", "Salad", "Breakfast", "Condiment", "Dip", "Cocktail", or "Other".
    """
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a culinary content specialist. Based on the provided video data, categorize each video into one or more of the following categories: Entree (Main Course), Side Dish, Dessert, Beverage, Appetizer, Snack, Soup, Salad, Breakfast, Condiment, Dip, Cocktail, or Other. Only use these categories and do not introduce any new categories. The categories should be provided in an array format, and only one array. Ensure the output is formatted as follows: ["Category1", "Category2"]"""},
                {"role": "user", "content": prompt},
            ]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        logging.error(f"Error in assign_food_categories: {str(e)}")
        return '["Other"]'
    
def embed_and_store_in_pinecone(pinecone, video_data, max_tokens=8192, model="text-embedding-ada-002"):
    index_name = "recipes"
    index = pinecone.Index(index_name)
    
    combined_text = f"{video_data['title']} by {video_data['creator']} {video_data['description']} {video_data['summary']} {video_data['recipe']} {video_data['personalized_description']}"
    
    combined_text = combined_text.replace("\n", " ")
    tokens = combined_text.split()
    if len(tokens) > max_tokens:
        combined_text = ' '.join(tokens[:max_tokens])
    
    try:
        response = openai.Embedding.create(
            input=[combined_text],
            model=model
        )
        embedding = response['data'][0]['embedding']
        
        namespaces = ["All"]
        try:
            food_categories = eval(video_data['food_category'])
            if isinstance(food_categories, list):
                namespaces.extend(food_categories)
            else:
                print(f"Warning: food_category is not a list for video {video_data['video_id']}")
        except Exception as e:
            print(f"Error processing food categories for video {video_data['video_id']}: {e}")
        
        for namespace in namespaces:
            index.upsert(
                vectors=[{
                    "id": f"{video_data['video_id']}_{namespace}",
                    "values": embedding,
                    "metadata": {
                        "title": video_data['title'],
                        "creator": video_data['creator'],
                        "personalized_description": video_data['personalized_description'],
                        "recipe": video_data['recipe'],
                        "food_category": video_data['food_category'],
                        "url": f"https://www.youtube.com/watch?v={video_data['video_id']}",
                        "video_id": video_data['video_id'],
                        "transcript": video_data['transcript'],
                        "description": video_data['description']
                    }
                }],
                namespace=namespace
            )
    except Exception as e:
        print(f"Error during embedding or storage: {e}")

def insert_into_supabase(supabase, video_data):
    response = supabase.table('playlists').select('id').eq('playlist_id', video_data['playlist_id']).execute()
    
    playlist_fk_id = None
    if response.data and len(response.data) > 0:
        playlist_fk_id = response.data[0].get('id')

    if not playlist_fk_id:
        print(f"Error: No matching playlist found for playlist_id: {video_data['playlist_id']}")
        return None

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
        "recipe": video_data.get('recipe'),
        "personalized_description": video_data.get('personalized_description'),
        "food_category": video_data.get('food_category')
    }

    response = supabase.table('videos').insert(data).execute()
    return response
    
def get_playlist_map(supabase):
    playlist_map = {}
    response = supabase.table('playlists').select('playlist_name, playlist_id').execute()
    for pl in response.data:
        playlist_map[pl['playlist_name']] = pl['playlist_id']
    return playlist_map

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
    
def summarize_video(video_title, transcription):
    try:
        completion = openai.ChatCompletion.create(model="gpt-4o-mini",
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
        Here is the information about the video you need to classify:
        
        <video_title>
        {video_data['title']}
        </video_title>
        <video_creator>
        {video_data['creator']}
        </video_creator>
        <video_description>
        {video_data['description']}
        </video_description>
        <video_summary>
        {video_data['summary']}
        </video_summary>
        """
        
        classification_completion = openai.ChatCompletion.create(model="ft:gpt-4o-mini-2024-07-18:alexs-org:yt-video-classification-v2:9x23ZDo5",
        messages=[
            {
                "role": "system",
                "content": """You are a Youtube Video Classifier. Your task is to classify a given video into one of the following categories:

                    "Development/AI"
                    <description>Content related to computer science, artificial intelligence, web development, and related news or tools. This category covers programming tutorials, AI advancements, development tool reviews, and tech industry updates. Key indicators include coding terminology, AI concepts, and discussions of software development practices.</description>
                    "Podcast/Comedy"
                    <description>Videos in a podcast format, including comedy podcasts and stand-up comedy sessions. This category features long-form conversational content, comedic performances, and interview-style shows. Key indicators include extended discussions, laugh tracks, and comedy-specific terminology.</description>
                    "Woodworking/DIY"
                    <description>Videos about makers, woodworkers, DIY projects, and home improvement. This category includes tutorials, project demonstrations, and tips for crafting and home renovation. Key indicators include tool usage, project plans, and home improvement terminology.</description>
                    "Arduino/Pi/SmartHome"
                    <description>Content focused on electronics projects, particularly those involving Arduino, Raspberry Pi, or smart home technology. This category covers non-home electrical projects, electronics creation, and maker culture for tech enthusiasts. Key indicators include circuit diagrams, coding for hardware, and discussions of electronic components.</description>
                    "Work/Growth"
                    <description>Videos about personal development, productivity at home and work, and self-improvement tips. This category includes motivational content, time management strategies, and career advancement advice. Key indicators include productivity techniques, personal growth strategies, and workplace efficiency discussions. Or anything about fitness.</description>
                    "Finance"
                    <description>Content covering financial news, personal finance tips, investment strategies, and economic trends. This category includes stock market analysis, budgeting advice, and discussions on financial planning. Key indicators include financial terminology, market statistics, and money management tips.</description>
                    "Gaming"
                    <description>Videos about video games, including game streaming, gaming news, reviews, and e-sports coverage. This category covers gameplay footage, game industry updates, and gaming culture discussions. Key indicators include game titles, gaming jargon, and references to gaming platforms or events.</description>
                    "Science/History"
                    <description>Educational content focusing on scientific topics and historical events. This category includes documentaries, lectures, and news about scientific discoveries or historical research. Key indicators include scientific terminology, historical dates and figures, and in-depth explanations of natural phenomena or past events.</description>
                    "Startup/Business"
                    <description>Content related to startup ideas, business strategies, and industry news. This category covers entrepreneurship, business model discussions, and market analysis, excluding personal finance topics. Key indicators include startup terminology, business strategy concepts, and discussions of market trends.</description>
                    "General Entertainment/News/Politics/Shows"
                    <description>A broad category covering consumer tech reviews, political news, general world news, and entertainment content not fitting into other specific categories. This includes current events, pop culture discussions, and general interest topics. Key indicators include references to current events, entertainment industry news, and discussions of popular culture or political issues. Videos featuring TV shows, sports events, skits or shorts from TV shows, and YouTube short films. This category includes documentaries not specifically about science or history. It excludes podcasts, comedy podcasts, and stand-up comedy sessions. Key indicators include episodic content, sports footage, and short-form entertainment.</description>

                    Analyze the content provided carefully. Consider the topic, themes, and keywords present in the title, description, transcript, and summary. Look for clear indicators that align with one of the given categories.

                    After your analysis, provide your final classification. Respond with only one word, which should be one of the listed categories. Your response should be in the following format:

                    <video_classification>
                    [Your one-word classification here]
                    </video_classification>

                    Use the following <scratchpad> to reason about the classification in your response:

                    <scratchpad>
                    1. What is the main topic of the video?
                    2. Are there any keywords or themes that strongly indicate a specific category?
                    3. Does the content align clearly with one of the given categories?
                    4. If it's not clear, what are the possible categories it could fall under?
                    </scratchpad>"""
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

def print_video(video_title, category):
    print(f"[green]✓[/green] [bold blue]{video_title}[/bold blue]   ->   playlist: [magenta]{category}[/magenta]")

def insert_into_supabase(supabase, video_data):
    response = supabase.table('playlists').select('id').eq('playlist_id', video_data['playlist_id']).execute()
    
    playlist_fk_id = None
    if response.data and len(response.data) > 0:
        playlist_fk_id = response.data[0].get('id')

    if not playlist_fk_id:
        print(f"Error: No matching playlist found for playlist_id: {video_data['playlist_id']}")
        return None

    # Remove quotes from the category name
    cleaned_category = video_data['playlist_name'].strip().replace('"', '')

    data = {
        "playlist_id_fk": playlist_fk_id,
        "category": cleaned_category,
        "playlist_id": video_data['playlist_id'],
        "video_id": video_data['video_id'],
        "video_name": video_data['title'],
        "creator": video_data['creator'],
        "description": video_data['description'],
        "transcript": video_data['transcript'],
        "summary": video_data['summary'],
        "date_added_to_playlist": datetime.utcnow().isoformat(),
        "recipe": video_data.get('recipe'),
        "personalized_description": video_data.get('personalized_description'),
        "food_category": video_data.get('food_category')
    }

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

# -----------------------------------------------------------

def main():
    logging.info("Starting video processing script")
    try:
        add_watchlater_to_temp()

        supabase = setup_supabase()
        youtube = get_authenticated_service()
        pinecone = initialize_pinecone()

        playlist_map = get_playlist_map(supabase)
        temp_playlist_id = playlist_map.get('Temp Playlist', '')
        if not temp_playlist_id:
            print("Temp Playlist not found.")
            return

        temp_videos = fetch_videos_from_playlist(youtube, temp_playlist_id)[::-1]
        saved_videos = get_all_videos(supabase)

        for video in temp_videos:
            snippet = video.get('snippet', {})
            video_id = snippet.get('resourceId', {}).get('videoId', '')

            if snippet.get('title') in ["Private video", "Deleted video"] or not video_id:
                continue

            if any(v['video_id'] == video_id for v in saved_videos):
                continue

            video_data = process_video(video_id, snippet)
            category = classify_video(video_data)
            logging.info(f"Classified as: {category}")

            if category.strip().lower().replace('"', '') == "cooking":
                logging.info("Entering cooking video processing")
                video_data["url"] = f"https://www.youtube.com/watch?v={video_id}"
                try:
                    video_data = process_cooking_video(video_data)
                    logging.info(f"Processed cooking video data: {json.dumps(video_data, indent=2)}")
                except Exception as e:
                    logging.error(f"Error in process_cooking_video: {str(e)}")
                    continue

                try:
                    embed_and_store_in_pinecone(pinecone, video_data)
                    logging.info("Embedded and stored in Pinecone")
                except Exception as e:
                    logging.error(f"Error in embed_and_store_in_pinecone: {str(e)}")
                    continue

            cleaned_category = category.strip().replace('"', '')
            target_playlist_id = playlist_map.get(cleaned_category)

            if target_playlist_id:
                video_data["playlist_name"] = category
                video_data["playlist_id"] = target_playlist_id

                try:
                    if add_to_playlist(youtube, video_id, target_playlist_id, video_data["title"]):
                        insert_into_supabase(supabase, video_data)
                        print_video(snippet.get('title'), category)
                        logging.info("Video added to playlist and inserted into Supabase")
                    else:
                        logging.info("Video already in playlist or couldn't be added")
                except Exception as e:
                    logging.error(f"Error in add_to_playlist or insert_into_supabase: {str(e)}")
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

