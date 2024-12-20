"""
MyAI - my wrapper for OpenAI.
- handles exceptions (if failed - just report error and stop program)
- counts used tokens
Usage:
my_ai = MyAI("MYSECRETAPIKEY", True, 2.5)
 - first parameter is OpenAI API key
 - second parameter is "quiet" for counting tokens
   (True - stay quiet and just report at the end,
    False - report on screen every API operation)
 - third parameter is limit of US Cents for the program - if exceeded, will raise exception.
"""

import requests
import sys
from openai import OpenAI
from pprint import pp

from lib.usedtokens import UsedTokens

class MyAI:
    def __init__(self, openai_api_key, quiet=True, limit=0):
        self.ai = OpenAI(api_key = openai_api_key)
        self.tokens = UsedTokens(quiet)
        self.limit = limit
    def __del__(self):
        self.tokens.print()
    def chat_completion(self, messages, model, max_tokens, temperature=1, source=""):
        try:
            chat_completion = self.ai.chat.completions.create(
                messages = messages,
                model = model,
                max_tokens = max_tokens,
                temperature = temperature
            )
            self.tokens.log(chat_completion, source)
            answer = chat_completion.choices[0].message.content
        except Exception as error:
            print (f"Error in OpenAI request: {error}")
            sys.exit(1)
        if self.limit>0 and self.tokens.cost()>self.limit:
            print (f"Exceeded limit of {self.limit} US Cents! Used {self.tokens.cost()} cents. EXIT.")
            sys.exit(1)
        return answer
    def chat_completion_json(self, messages, model, max_tokens, temperature=1, source=""):
        try:
            chat_completion = self.ai.chat.completions.create(
                messages = messages,
                model = model,
                max_tokens = max_tokens,
                temperature = temperature,
                response_format = {"type": "json_object"}
            )
            self.tokens.log(chat_completion, source)
            answer = chat_completion.choices[0].message.content
        except Exception as error:
            print (f"Error in OpenAI request: {error}")
            sys.exit(1)
        if self.limit>0 and self.tokens.cost()>self.limit:
            print (f"Exceeded limit of {self.limit} US Cents! Used {self.tokens.cost()} cents. EXIT.")
            sys.exit(1)
        return answer
    def images_generate(self, prompt, model="dall-e-3", size="1024x1024", quality="standard", n=1):
        try:
            response = self.ai.images.generate(
                model = model,
                prompt = prompt,
                size = size,
                quality = quality,
                n = n
            )
        except Exception as error:
            print (f"Error in OpenAI request: {error}")
            sys.exit(1)
        if self.limit>0 and self.tokens.cost()>self.limit:
            print (f"Exceeded limit of {self.limit} US Cents! Used {self.tokens.cost()} cents. EXIT.")
            sys.exit(1)
        return response
    def transcribe(self, file, source="", model="whisper-1"):
        try:
            transcription = self.ai.audio.transcriptions.create(
                model = model,
                file = file,
                response_format = "verbose_json"
            )
            self.tokens.log_transcription(transcription.duration, model, source=source)
        except Exception as error:
            print (f"Error in OpenAI request: {error}")
            sys.exit(1)
        if self.limit>0 and self.tokens.cost()>self.limit:
            print (f"Exceeded limit of {self.limit} US Cents! Used {self.tokens.cost()} cents. EXIT.")
            sys.exit(1)
        return transcription.text
    def embedding(self, text, model="text-embedding-3-small", source=""):
        try:
            parsed_text = text.replace("\n", " ")
            embedding = self.ai.embeddings.create(input = [parsed_text], model=model)
            self.tokens.log_embedding(embedding, source)
            answer = embedding.data[0].embedding
        except Exception as error:
            print (f"Error in OpenAI request (embedding): {error}")
            sys.exit(1)
        if self.limit>0 and self.tokens.cost()>self.limit:
            print (f"Exceeded limit of {self.limit} US Cents! Used {self.tokens.cost()} cents. EXIT.")
            sys.exit(1)
        return answer
