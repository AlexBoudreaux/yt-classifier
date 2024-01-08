import json

# Function to convert a single line
def convert_line(old_line):
    new_line = {
        "messages": [
            {
                "role": "system",
                "content": "You are a Youtube Video Classifier. You will be fed a Youtube video Title, Description, Transcript, and Summary and you will output the classification of the video. The possible classifications are \"Cooking\", \"Late Night Jammers\", \"Shows\", \"Development\", \"Podcast/Comedy\", \"Woodworking/DIY\", \"Arduino/Pi/SmartHome\", \"Work/Growth\", \"Finance\", \"Gaming\", \"Science/History\", \"AI\", \"Startup/Business\" or if you are not sure enough respond with \"Misc.\". You will be scored on how well you classify the videos. Only respond with one of those classifications or \"Misc.\"."
            },
            {
                "role": "user",
                "content": old_line["prompt"]
            },
            {
                "role": "assistant",
                "content": old_line["completion"]
            }
        ]
    }
    return new_line

# Read from old file and write to new file
with open('training-data_prepared_train.jsonl', 'r') as old_file, open('new-training-data_prepared_train.jsonl', 'w') as new_file:
    for line in old_file:
        old_line = json.loads(line.strip())
        new_line = convert_line(old_line)
        new_file.write(json.dumps(new_line) + '\n')
