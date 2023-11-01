# import os
# import openai
# openai.api_key ="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" MINE...
# print(openai.Model.list())


import os
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = open('OPEN_AI_API_KEY').read()
chat_completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "I my name is russell. Whats yours?"}])

print(chat_completion)

