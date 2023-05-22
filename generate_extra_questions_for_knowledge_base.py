# Step 1. Import knowledge base 
# Step 2. Get the FAQs 
# Step 3. For each question, generate 10 new questions 
# Step 4. Link the existing content to the new questions 
# Step 5. Save as extra content to be added to FAQs and sitemap content 

import time
import sys
import math
import tiktoken
import numpy as np
import pandas as pd

import os 
import time 
import openai 
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
openai.orgaization='Personal'
openai.api_key = config.get('secrets', 'openai_api_key')

system_content = 'You are an AI chatbot for the Nordic e-commerce company Tradera.  Given the following questions, find 10 different ways to rephrase the content under QUESTION that a buyer might ask.'
user_prompt = 'You are an AI chatbot for the Nordic e-commerce company Tradera.  Given the following questions, find 10 different ways to rephrase the content under QUESTION that a buyer might ask, and print a numbered list: QUESTION\n'

def generate_questions(question): 
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": system_content}, 
                {"role": "user", "content": user_prompt + question},
            ]
    )

    # print(question, response['choices'][0]['message']['content'])


    return response['choices'][0]['message']['content']


df_faq = pd.read_csv('data/knowledge_base.csv')[['title', 'content']]
df_faq = df_faq.loc[~df_faq['title'].isnull()]

results = []
for row in df_faq.iterrows(): 
    print(row[0], len(df_faq))
    
    try: 
        results.append({'df_faq_idx': row[0], 'result': generate_questions(row[1]['title'])})
    except Exception: 
        time.sleep(2)
        try:
            results.append({'df_faq_idx': row[0], 'result': generate_questions(row[1]['title'])})
        except Exception: 
            print("Error getting questions for %d" % row[0])

df_results = pd.DataFrame.from_records(results)
df_results.to_csv('data/unprocessed_extra_questions')
