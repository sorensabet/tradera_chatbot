# Open AI: 

#   Content Generation 
#   Summarization 
#   Classification, Categorization, and Sentiment Analysis 
#   Data Extraction 
#   Translation 
#   Many more 

#   Completions endpoint: 
    #  Given a prompt, the model returns one or more predicted completions, and also returns the probabilities 
    #  of alternative tokens at each position 

# Simple test: Give ChatGPT 


# Helper function to send questions to ChatGPT 



import os 
import openai 
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
openai.orgaization='Personal'
openai.api_key = config.get('secrets', 'openai_api_key')


def prompt_gpt(prompt, model='gpt-3.5-turbo'): 
    response = openai.ChatCompletion.create(
        model=model, 
        messages=[
            {"role": "system", "content": "You are an AI powered customer service agent for a Nordic secondhand auction website marketplace called Tradera"},
            {"role": "user", "content": "What can I sell on Tradera"}, 
            {"role": "assistant", "content": "You can sell anything as long as it does not violate our terms of service"}, 
            {"role": "user", "content": "Where can I find more information?"},
    ])
    
    return response 

gpt_response = prompt_gpt('')
answer = gpt_response['choices'][0]['message']

openai.ChatCOmpletion.create(
    model="gpt-3.5-turbo",
    messages=[
            {"role": "system": "You are an assistant that generates question answer pairs for a Nordic e-commerce site called Tradera."},
            {"role": "user": "You are an assistant that generates question answer pairs for a Nordic e-commerce site called Tradera. Using " \
             " the following information. please generate 3 different questions for me: \n\n. The world is 500 years old, and the sky is blue."}
        ]
    )

# Okay/ 
    

