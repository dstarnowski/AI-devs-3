"""
Solution to 9th task
- download and unpack .zip file with reports
- prepare list of files for each category - .txt, .png, .mp3
- prepare variables with .txt contents, .mp3 transcriptions
- send the texts for category decision (people, hardware, software, other)
- send the pictures for category decision (as above)
- sort the lists
- send the answer
"""

import requests
import json
import os
import zipfile
import re
import base64
from pprint import pp

from lib.aidevs import send_task_response
from secrets import aidevs_api_key, central_domain, openai_api_key
from lib.myai import MyAI

ai = MyAI(openai_api_key, True, 10)
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

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Download and extract the reports
url = f"https://centrala.{central_domain}/dane/pliki_z_fabryki.zip"
reports_dir = download_and_extract_zip(url, "downloads", "task0204.zip", "task0204")
files = {
    'txt': [],
    'png': [],
    'mp3': []
}
# Classify files based on the extension
for filename in os.listdir(reports_dir):
    for extension in ['txt','mp3','png']:
        if filename.endswith(f'.{extension}'):
            files[extension].append(filename)
text_reports = []
# Read text files directly
for filename in files['txt']:
    with open(os.path.join(reports_dir, filename),'r') as text_file:
        text_reports.append(text_file.read())
# Transcribe audio files
for filename in files['mp3']:
    with open(os.path.join(reports_dir, filename),'rb') as audio_file:
        text_reports.append(ai.transcribe(audio_file))
# Set the universal prompt
prompt = """
Your task is to read the report sent by user and assign it to one of four categories: HARDWARE, PEOPLE, SOFTWARE, OTHER.
If the report mentions captured people, or if any specific people were spotted or their presence was noticed in the area - answer with category name PEOPLE.
If the report mentions any hardware fixes - answer with category name HARDWARE.
If the report mentions any software fixes (without hardware fixes) - answer with category name SOFTWARE.
If the report doesn't fit to other categories, or mentions people but without their capture or their presence being noticed - answer with category name OTHER.
Please respond with just category name, and nothing else.
"""
task_response = {
    "people": [],
    "hardware": []
}
# Send text files for category selection
for filename in files['txt']:
    with open(os.path.join(reports_dir, filename),'r') as text_file:
        text_report = text_file.read()
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text_report}
        ]
        answer = ai.chat_completion(messages, model, 10, 0)
        print (f"File: {filename} -> {answer}")
        if answer=="PEOPLE":
            task_response['people'].append(filename)
        if answer=="HARDWARE":
            task_response['hardware'].append(filename)
# send audio files for transcription and category selection
for filename in files['mp3']:
    with open(os.path.join(reports_dir, filename),'rb') as audio_file:
        text_report = ai.transcribe(audio_file)
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": text_report}
        ]
        answer = ai.chat_completion(messages, model, 10, 0)
        print (f"File: {filename} -> {answer}")
        if answer=="PEOPLE":
            task_response['people'].append(filename)
        if answer=="HARDWARE":
            task_response['hardware'].append(filename)
# send photos for category selection
for filename in files['png']:
    image = encode_image(os.path.join(reports_dir, filename))
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": [{
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{image}"
            }
        }]
        }
    ]
    answer = ai.chat_completion(messages, model, 10, 0)
    print (f"File: {filename} -> {answer}")
    if answer=="PEOPLE":
        task_response['people'].append(filename)
    if answer=="HARDWARE":
        task_response['hardware'].append(filename)
# Sort the answers
for category in ["people","hardware"]:
    task_response[category].sort()
pp (task_response, indent=4)
# Send answers
response = send_task_response(aidevs_api_key, "kategorie", task_response, f"https://centrala.{central_domain}/report")
pp (response, indent=4)
