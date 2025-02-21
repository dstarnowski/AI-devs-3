"""
Solution to 6th task
- download the .zip file with recordings
- unzip the file
- send each recording to AI transcription
- compose a prompt with all transcribed texts
- ask GPT to find the street where the Institute is located
"""

import os
import requests
import zipfile
from pprint import pp

from sekrety import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI
from lib.aidevs import send_task_response

ai = MyAI(openai_api_key, False, 10)    # Limit to 10 cents, 2 is not enough :)
model = "gpt-4o-mini"

# Quick unzip function generated by 4o
def download_and_extract_zip(url, download_dir='downloaded', zip_filename='downloaded_zipfile.zip', extract_dir='extracted'):
    # Create download subdirectory if it doesn't exist
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    # Download the file
    local_zip_path = os.path.join(download_dir, zip_filename)
    response = requests.get(url)
    if response.status_code == 200:
        with open(local_zip_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded ZIP file to {local_zip_path}")
    else:
        print("Failed to download the file.")
        return
    # Create extraction subdirectory if it doesn't exist
    full_extract_dir = os.path.join(download_dir, extract_dir)
    if not os.path.exists(full_extract_dir):
        os.makedirs(full_extract_dir)
    # Extract the ZIP file
    with zipfile.ZipFile(local_zip_path, 'r') as zip_ref:
        zip_ref.extractall(full_extract_dir)
        print(f"Extracted files to {full_extract_dir}")
    # List all extracted files
    extracted_files = os.listdir(full_extract_dir)
    print("Extracted files:")
    pp(extracted_files, indent=4)
    return full_extract_dir

# Download and extract the recordings
url = f"https://centrala.{central_domain}/dane/przesluchania.zip"
recordings = download_and_extract_zip(url, "downloads", "task0201.zip", "recordings")

# Send the recordings for Whisper transcription and store texts in a table
transcriptions = []
for filename in os.listdir(recordings):
    file = os.path.join(recordings,filename)
    with open(file, "rb") as audio_file:
        transcriptions.append(ai.transcribe(audio_file))

# Compose system and user messages for AI to find the answer
prompt = """
You are a detective.
You need to carefully read the testimonies of few witnesses.
Some of them can be contradicting, some of them may complement each other.
Your task is to identify the Institute name within the university where professor Andrzej Maj is giving the lectures.
Please quote all parts of witnesses testimonies, that relate to the university and the Institute.
Once you identify the Institute, identify the name of the street, where the Institute is, using your general knowledge.
In the end, please output "ODPOWIEDŹ: " Followed by the street name.
"""
testimonies = ""
witness = 0
for testimony in transcriptions:
    witness += 1
    testimonies += f"## Testimony of witness {witness}\n\n{testimony}\n\n"
print (f"The prompt is: {prompt}")
print (f"The testimonies are: {testimonies}")
messages = [
    {"role": "system", "content": prompt},
    {"role": "user", "content": testimonies}
]

# Get answer from AI and send it to Central
answer = ai.chat_completion(messages, model, 1000, 0)
print (f"Odpowiedź to: {answer}")
task_response = send_task_response(aidevs_api_key, "mp3", answer, f"https://centrala.{central_domain}/report")
pp(task_response)