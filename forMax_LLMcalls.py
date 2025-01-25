#pip install openai
from openai import OpenAI
from pydantic import BaseModel

###uncomment to run with gpt-4o; need openAI API key; THIS SENDS DATA TO OPENAI:
#import os
#OpenAI.api_key = os.getenv('OPENAI_API_KEY') #or hard code your api key
#client = OpenAI()
#llm="gpt-4o-2024-08-06"

#or run locally; THIS KEEPS DATA ON YOUR COMPUTER ONLY:
#1-download LMStudio (there are other ways to do this, including ollama and huggingface, but this code works with LMStudio)
#2-open LMStudio app and browse models. download a small gguf model (try llama-3.2-3b-instruct with Q4 size, use lmstudio-community provider)
#3-go to developer tab in LMStudio, and toggle server on (top left corner) and load downloaded model
BASE_URL="http://localhost:1234/v1" #will be your local host
API_KEY = "noKey" #this argument is req'd, but local models have no actual API key
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
llm="llama-3.2-3b-instruct" #replace with model's api identifier if using different model


#####SIMPLE CHAT COMPLETION EXAMPLE - YOU SEND LLM A PROMPT, IT RESPONDS#####
# Simple chat completions - you can insert objects into the system or user content space
completion = client.chat.completions.create(
    model=llm,
    messages=[
        {"role": "system", "content": "You are a helpful Assistant"},
        {"role": "user", "content": "Tell me the average weather in Phoenix in January."},
    ],
    stream=True #True means you receive each token as it is produced, False means you get the entire response after it is done
)

print("\n\n\n+++++++++Chat Completion Output+++++++++++\n")
##This "streams" the print - you can also wait for the entire response:
#stream=true
for chunk in completion:
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="", flush=True)

##This prints the entire response at once (only works when stream=false in the llm call):
#stream=false
#event = completion.choices[0].message.content
#print(event)


#####STRUCTURED OUTPUT EXAMPLE - YOU SEND LLM A PROMPT, IT RESPONDS WITH A STRUCTURED OBJECT#####
#Define pydantic object
class some_class(BaseModel):
    weather_summary: str
    avg_degrees_farenheit: int

# Use the dynamic model in the OpenAI completion request
completion = client.beta.chat.completions.parse(
    model=llm,
    messages=[
        {"role": "system", "content": "You are a helpful Assistant"},
        {"role": "user", "content": "Tell me the average weather in Phoenix in January."},
    ],
    response_format=some_class,
)

#Print attribute from structured response
event = completion.choices[0].message.parsed
print("\n\n\n+++++++++STRUCTURED OUTPUT - ENTIRE EVENT PRINT+++++++++++\n")
print(event)

print("\n\n\n+++++++++STRUCTURED OUTPUT - PARSED FOR SINGLE OBJECT ATTRIBUTE PRINT+++++++++++\n")
class_attribute = event.avg_degrees_farenheit
print(f"avg degrees: {class_attribute}")