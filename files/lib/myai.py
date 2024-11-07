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

from lib.usedtokens import UsedTokens

class MyAI:
    def __init__(self, openai_api_key, quiet=True, limit=0):
        self.ai = OpenAI(api_key = openai_api_key)
        self.tokens = UsedTokens(quiet)
        self.limit = limit
    def __del__(self):
        self.tokens.print()
    def chat_completion(self, messages, model, max_tokens, temperature=1):
        try:
            chat_completion = self.ai.chat.completions.create(
                messages = messages,
                model = model,
                max_tokens = max_tokens,
                temperature = temperature
            )
            self.tokens.log(chat_completion)
            answer = chat_completion.choices[0].message.content
        except Exception as error:
            print (f"Error in OpenAI request: {error}")
            sys.exit(1)
        if self.limit>0 and self.tokens.cost()>self.limit:
            print (f"Exceeded limit of {self.limit} US Cents! Used {self.tokens.cost()} cents. EXIT.")
            sys.exit(1)
        return answer
