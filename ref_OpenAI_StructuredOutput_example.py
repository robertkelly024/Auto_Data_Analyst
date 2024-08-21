#This script shows how to get structured output from openai api
import os
from openai import OpenAI
from pydantic import BaseModel

#save api key as environmental variable
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

#Define object
class some_class(BaseModel):
    class_attribute1: str
    class_attribute2: str

# Use the dynamic model in the OpenAI completion request
completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": "SYSTEM MESSAGE GOES HERE"},
        {"role": "user", "content": "USER MESSAGE GOES HERE"},
    ],
    response_format=some_class,
)

#Print attribute from structured response
event = completion.choices[0].message.parsed
class_attribute = event.class_attribute1
print(event.class_attribute1)