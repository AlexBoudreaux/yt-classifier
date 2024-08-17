import json
from typing import List, Dict

def read_jsonl(file_path: str) -> List[Dict]:
    """Read a JSONL file and return a list of dictionaries."""
    with open(file_path, 'r') as file:
        return [json.loads(line) for line in file]

def write_jsonl(data: List[Dict], file_path: str):
    """Write a list of dictionaries to a JSONL file."""
    with open(file_path, 'w') as file:
        for item in data:
            json.dump(item, file)
            file.write('\n')

def convert_format(old_format: Dict) -> Dict:
    """Convert old format to new format."""
    old_user_content = json.loads(old_format['messages'][1]['content'])
    old_classification = old_format['messages'][2]['content'].strip()

    new_format = {
        "messages": [
            {
                "role": "system",
                "content": """You are a Youtube Video Classifier. Your task is to classify a given video into one of the following categories:

"Cooking"
<description>Videos focusing on food preparation, recipes, and culinary techniques. This category includes cooking tutorials, recipe demonstrations, food reviews, and kitchen tips. Key indicators include ingredient lists, cooking instructions, and food-related terminology.</description>

"Shows"
<description>Videos featuring TV shows, sports events, skits or shorts from TV shows, and YouTube short films. This category includes documentaries not specifically about science or history. It excludes podcasts, comedy podcasts, and stand-up comedy sessions. Key indicators include episodic content, sports footage, and short-form entertainment.</description>

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

"General Entertainment/News/Politics"
<description>A broad category covering consumer tech reviews, political news, general world news, and entertainment content not fitting into other specific categories. This includes current events, pop culture discussions, and general interest topics. Key indicators include references to current events, entertainment industry news, and discussions of popular culture or political issues.</description>

Analyze the content provided carefully. Consider the topic, themes, and keywords present in the title, description, and summary. Look for clear indicators that align with one of the given categories.

After your analysis, provide your final classification. Respond with only one word, which should be one of the listed categories. Your response should be in the following format:

<video_classification>
[Your one-word classification here]
</video_classification>"""
            },
            {
                "role": "user",
                "content": f"""Here is the information about the video you need to classify:

<video_title>
{old_user_content['Video Name']}
</video_title>
<video_creator>
{old_user_content['Creator']}
</video_creator>
<video_description>
{old_user_content['Description']}
</video_description>
<video_summary>
{old_user_content['Summary']}
</video_summary>"""
            },
            {
                "role": "assistant",
                "content": f"<video_classification>\n{old_classification}\n</video_classification>"
            }
        ]
    }
    return new_format

def convert_data(input_file: str, output_file: str):
    """Convert data from old format to new format."""
    # Read input data
    data = read_jsonl(input_file)
    
    # Convert data
    converted_data = [convert_format(item) for item in data if convert_format(item) is not None]
    
    # Write output file
    write_jsonl(converted_data, output_file)
    
    print(f"Total samples converted: {len(converted_data)}")
    print(f"Samples skipped: {len(data) - len(converted_data)}")

if __name__ == "__main__":
    input_file = "./training-data-all_8-14.jsonl"
    output_file = "./training-data-new-all_8-15.jsonl"
    
    convert_data(input_file, output_file)
