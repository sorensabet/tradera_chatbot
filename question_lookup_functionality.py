# Given a question by the user: 
    
# Step 1. Find the nearest sentence 
# Step 2. Find the nearest whole chunk of context 
# Step 3. Call ChatGPT with all the relevant context and the answer, and have it return the answer

import os 
import openai 
import tiktoken 
import numpy as np 
import configparser
import pandas as pd 
from sklearn.metrics.pairwise import cosine_similarity

# Get top N most similar questions 
n = 10

def get_embedding(user_question): 
    embedding = openai.Embedding.create(
        input=user_question,
        model='text-embedding-ada-002')['data'][0]['embedding']
    return np.array(embedding).reshape(-1,1)

def check_for_answer(context, question):    
    
    response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo",
      messages=[
            {"role": "system", "content": "You are an AI powered customer service chatbot for the Nordic e-commerce company Tradera."},
            {"role": "user", "content": "Given the following CONTEXT, return a summary of the answer to the QUESTION if it exists in the CONTEXT and add the closest URL to the answer, otherwise say NO_ANSWER_FOUND. \nCONTEXT:" + context +  '\nQUESTION: ' + question + "\n"},
        ]
    )
    
    return response['choices'][0]['message']['content']
    
enc = tiktoken.encoding_for_model('gpt-3.5-turbo')

question = 'Vad kostar det att skicka ett paket på 1 kg med Schenker i Sverige?'
question_enc = enc.encode(question)

df_sll = pd.read_csv('data/sentence_level_lookup.csv', index_col=0)
df_pll = pd.read_csv('data/page_level_lookup.csv', index_col=0)
sent_embs = np.load('data/all_sentence_level_embeddings.npy')

config = configparser.ConfigParser()
config.read('config.ini')
openai.orgaization='Personal'
openai.api_key = config.get('secrets', 'openai_api_key')


question_embedding = get_embedding(question)

sim_matrix = cosine_similarity(sent_embs, question_embedding.transpose())

# Get indices of top n most similar sentences 
top_n_idx = np.argsort(-1*sim_matrix.reshape(1,-1))[0,:n]
most_sim_values = sim_matrix[top_n_idx].reshape(1,-1)[0,:]
df_top = pd.DataFrame(np.stack([top_n_idx, most_sim_values]).transpose())
df_top.rename(columns={0: 'sentence_index', 1: 'similarity'}, inplace=True)
df_top['sentence_index'] = df_top['sentence_index'].astype(int)

df_top = df_top.merge(df_sll[['page_level_lookup_index']], left_on=['sentence_index'], right_index=True, how='left')
df_top = df_top.merge(df_pll[['context_segment_text', 'page_url']], left_on=['page_level_lookup_index'], right_index=True, how='left')
df_top['context_segment_text'] = 'URL: ' + df_top['page_url'] + '\n' + df_top['context_segment_text']

df_combined_context = pd.DataFrame(data=['\n'.join(df_top['context_segment_text'])], columns=['context'])
df_combined_context['tokenized'] = df_combined_context['context'].apply(lambda x: enc.encode(x))
df_combined_context['num_tokens'] = df_combined_context['tokenized'].str.len()

df_tokens = df_combined_context[['tokenized']].explode(column=['tokenized'])
df_tokens['token_num'] = df_tokens.groupby(df_tokens.index).cumcount()
df_tokens = df_tokens.loc[df_tokens['token_num'] < 3000 - len(question_enc) - 50] # Include as much context as possible and let ChatGPT deal with finding the answer

df_final_context = df_tokens.groupby([df_tokens.index]).agg({'tokenized': lambda x: x.tolist()})
df_final_context['context'] = df_final_context['tokenized'].apply(lambda x: enc.decode(x))

answer = check_for_answer(df_final_context['context'][0], question)

print(question, '\n', answer)


# Q1: Hur mycket kostar det att sälja på Tradera?
# A1: Hur mycket kostar det att sälja på Tradera? Försäljningsprovisionen på Tradera är 10% av försäljningspriset, med ett minimum på 3 kr och ett max på 200 kr. Det finns också olika inte obligatoriska tillval som kostar extra, och osåltavgift debiteras om du har haft fler än 100 upplagda (sålda och osålda) annonser under en faktureringsperiod. För företag finns det olika provisionsavgifter beroende på varukategori. Närmare information kan hittas på den här sidan: https://info.tradera.com/salja-pa-tradera/.

# Q2: Vad är provisionsavgiften i kategorin Kläder?
# A2: Vad är provisionsavgiften i kategorin Kläder? # Provisionsavgiften för kategorin Kläder är 8% av försäljningspriset, med en lägsta avgift på 2,40 kr och en högsta avgift på 160 kr. URL: https://info.tradera.com/foretag/


# Q3: Hur startar jag en dispyt?
# A3: Om du har valt till köparskydd eller betalat med Paynova och inte mottagit varan eller om varan skiljer sig markant från beskrivningen kan du  starta en tvist genom att klicka på ”Mer”-fliken vid berörd annons och välja ”Anmäl utebliven vara”. Därifrån kan du skapa en tvist. Första steget i en tvist är alltid att du och säljaren får chansen att lösa ärendet tillsammans. Läs mer om hur en tvist fungerar och om förutsättningarna för köparskydd på: https://info.tradera.com/traderabetalning/kopskydd/. Om du har betalat med Klarna eller PayPal följer du istället deras process för tvister på https://www.klarna.com/se/kopa-online/betalningstjanster/koparskydd/ eller https://www.paypal.com/se/webapps/mpp/paypal-buyer-protection.

# Q4: Kan jag sälja en pistol på Tradera?
# A4: No answer found. 

# Q5: Vad är Samfrakt? 
# A5: Samfrakt är en funktion på Tradera som gör det möjligt för köpare att kombinera flera varor från samma säljare i en och samma order för att minska fraktkostnader. Köpare kan begära samfraktpris från säljaren när de har köpt minst två varor. Samfrakt kräver att alla varor har samma fraktalternativ. Läs mer om hur samfrakt fungerar för köpare och säljare på https://info.tradera.com/samfrakt-kopare/.

# Q6: Vad kostar det att skicka ett paket på 1 kg med Schenker i Sverige?
# A6: No answer found. 

# How to improve: 
#   Add page level embeddings as a second check, if the first one doesn't work. 



