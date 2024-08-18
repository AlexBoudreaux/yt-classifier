from pinecone import Pinecone
import openai
import logging
from config import PINECONE_API_KEY

from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def initialize_pinecone():
    return Pinecone(api_key=PINECONE_API_KEY)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def embed_and_store_in_pinecone(pinecone, video_data, max_tokens=8192, model="text-embedding-ada-002"):
    index_name = "recipes"
    index = pinecone.Index(index_name)
    
    combined_text = f"{video_data['title']} by {video_data['creator']} {video_data['description']} {video_data['summary']} {video_data['recipe']} {video_data['personalized_description']}"
    
    combined_text = combined_text.replace("\n", " ")
    tokens = combined_text.split()
    if len(tokens) > max_tokens:
        combined_text = ' '.join(tokens[:max_tokens])
    
    try:
        response = retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(openai.Embedding.create)(
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
