import os 
import numpy as np
import pandas as pd

# Import questions and answers, solve this problem now for simplicity and speed. 
#df_qa = pd.read_csv('info_page_qa.csv', index_col=0)[['QA']]
# Goal: split entries of multiple questions into separate entries programatically, append with knowledge base questions, and use these to train model. 

# Step 1. Ingest all the data in text files and save in pandas 
txt_files = [f for f in os.listdir('data/temp_cache/') if f != '.DS_Store']

qa = []
for f in txt_files: 
    with open('data/temp_cache/' + f) as file: 
        lines = file.read()        
        qa.append({'QA': lines})

df = pd.DataFrame.from_records(qa)
df['questions'] = df['QA'].str.split('QUESTION: ')
df2 = df.explode(column='questions')
df2 = df2.loc[df2['questions'].str.len() > 0][['questions']]
df3 = df2['questions'].str.split('ANSWER: ', expand=True).rename(columns={0: 'prompt', 1: 'completion'})[['prompt', 'completion']]


# Import df_faq. no preprocessing due to time constraints. 
df_faq = pd.read_csv('data/knowledge_base.csv')
df_faq.rename(columns={'title': 'prompt', 'content': 'completion'}, inplace=True)
df_faq = df_faq[['prompt', 'completion']]


df_fine_tune = pd.concat([df3, df_faq])
df_fine_tune['prompt'] = df_fine_tune['prompt'] + '\n\n###\n\n'
df_fine_tune['completion'] = ' ' + df_fine_tune['completion'] + '###'

df_fine_tune.to_csv('data/fine_tune_data.csv', index=None)




# Each prompt should end with a fixed separator to inform model when the prompt ends and completion begins. 
# Simple separator can be \n\n###\n\n

# Each completion should start with whitespace due to our tokenization 
# EAch completion should end with a fixed stop sequence to inform model when completion ends. 
# Stop sequence could be \n, ###, or any other token not appearing in completion.

# For inference, you should format prompts in the same way as you did when creating the training dataset. 
# Also, specify the same stop sequence. 