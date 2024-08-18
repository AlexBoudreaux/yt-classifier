from youtube_transcript_api import YouTubeTranscriptApi
import openai
import logging

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
        return " ".join(transcript_words)  # Return the full transcript
    except:
        print(f"Video {video_title} could not be transcribed.")
        return "Transcription not available."

def summarize_video(video_title, transcription):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube video transcripts. You will be given the first 1000 words of a youtube video."},
                {"role": "user", "content": f"Please summarize the following video transcript in a concise paragraph:\n\n{transcription}"}
            ]
        )
        return completion.choices[0].message["content"].strip()
    except:
        print(f"Video {video_title} could not be summarized.")
        return "Summary not available."

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

                    "Cooking"
                    <description>Videos about cooking. This category includes recipes, cooking tips, and cooking techniques. Key indicators include cooking terminology, cooking tips, and cooking techniques.</description>
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

                    Use the following template of a <scratchpad> to reason about the classification in your response (give the scratchpad and your thoughts as well as the video classification in your answer):

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

def process_cooking_video(video_data):
    # Generate recipe using full transcript
    recipe = generate_recipe(video_data)
    video_data["recipe"] = recipe
    
    # Assign food categories
    food_categories = assign_food_categories(video_data)
    video_data["food_category"] = food_categories
    
    # Create personalized description
    personalized_description = create_personalized_description(video_data)
    video_data["personalized_description"] = personalized_description

    return video_data

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
    
