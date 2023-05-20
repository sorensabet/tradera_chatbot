# Ingest the sitemap data, break it down into smaller sections, 
# Turn it into a question/answer format using chat GPT, as well as identifying questions 
# about the data that are not included for negative examples. 

# Use GPT models to generate specific question/answer pairs 


import sys
import math
import tiktoken
import numpy as np
import pandas as pd


import os 
import time 
import openai 
import configparser
# 
config = configparser.ConfigParser()
config.read('config.ini')

openai.orgaization='Personal'
openai.api_key = config.get('secrets', 'openai_api_key')

num_questions = 10
system_content = "You are an AI that generates potential question answer pairs in Swedish that users could ask from reading information pages for a Nordic e-commerce company called Tradera"
user_prompt =  "You are an AI that generates questions that users could ask from reading information pages for a Nordic e-commerce company. Given the text below CONTEXT in Swedish, please come up with " + str(num_questions) + " different questions that are answered in the text. Please write the question, a detailed answer explaining why you generated that answer, and the URL provided at the beginning of the context, in the following format:       \n\nQUESTION: question you generated\n\ANSWER: Answer you generated\nURL: The URL included at the start of the context"

def generate_questions(context): 
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": system_content}, 
                {"role": "user", "content": user_prompt + context},
            ]
    )

    return response['choices'][0]['message']['content']

# print('Starting this program - sanity check from console')

# df_urls = pd.read_csv('data/info_page_content.csv', index_col=0)
# df_urls['len_string'] = df_urls['page_text'].str.len()

# enc = tiktoken.encoding_for_model('gpt-3.5-turbo')

# df_urls['tokenized'] = df_urls['page_text'].apply(lambda x: enc.encode(x))
# df_urls['num_tokens'] = df_urls['tokenized'].str.len()

# # Split the tokens into elements of max size = 200
# df_tokens = df_urls[['tokenized']].explode(column=['tokenized'])
# df_tokens['orig_index'] = df_tokens.index
# df_tokens['new_index'] = range(0, len(df_tokens), 1)
# df_tokens['context_segment'] = df_tokens['new_index']//400
# df_tokens = df_tokens[['tokenized', 'orig_index', 'context_segment']]

# df_reagg = df_tokens.groupby(['orig_index', 'context_segment']).agg({'tokenized': lambda x: x.tolist()}).reset_index()
# df_reagg['context_segment_text'] = df_reagg['tokenized'].apply(lambda x: enc.decode(x))
# df_reagg['len_tokenized'] = df_reagg['context_segment_text'].apply(lambda x: len(x))

# # For simplicity, only generate question/answer pairs on text that is > 100 characters long after splitting apart 
# # 100 chosen arbitrarily based on quick visual inspection of content
# df_reagg = df_reagg.loc[df_reagg['len_tokenized'] > 100]

# # Join in the link information, so it can be included in the answer 
# df_reagg = df_reagg.merge(df_urls[['page_url']], left_on=['orig_index'], right_index=True, how='left')
# df_reagg['final_context_text'] = '\nURL: ' + df_reagg['page_url'] + '\nCONTEXT' + df_reagg['context_segment_text']
# df_reagg['left_idx'] = df_reagg.index


# df_reagg.to_csv('data/context_snippets_post_5h.csv')

df_reagg = pd.read_csv('data/context_snippets_post_5h.csv', index_col=0).reset_index(drop=True)[['final_context_text']]

# Because there are many requests being made, I need to cache results as they come, and
# check for results that were already completed, before making calls to openAI API. 
# data/temp_cache will store the temporary results. 
completed_indices = [int(x.replace('.txt', '')) for x in os.listdir('data/temp_cache/') if x != '.DS_Store']
df_reagg = df_reagg.loc[~df_reagg.index.isin(completed_indices)]

q_results  = [] 

iter_count = 0
for row in df_reagg.iterrows(): 
    print('Now generating questions for %d of %d' % (row[0], max(df_reagg.index)))
    
    
    try: 
        start_time = time.time()
        questions = generate_questions(row[1]['final_context_text'])
        end_time = time.time() 
        
        print('\tTook %d seconds to generate %d questions' % (end_time-start_time, num_questions))
    
        with open('data/temp_cache/' + str(row[0]) + '.txt', 'w') as f:
            f.write(questions)
    except Exception: 
        print('There was an error, delaying by a few seconds and continuing.')
        time.sleep(10) # 10 second delay in case the api has a timeout. 
        # Manually rerun the code after. 

    iter_count += 1
    


#final_df = df_reagg.merge(df_questions[['right_idx', 'QA']], left_on=['left_idx'], right_on=['right_idx'], how='left')
#final_df.to_csv('data/info_page_qa.csv')

# Okay. I now want to generate question answer pairs somehow. 
