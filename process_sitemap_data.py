# Step 1. Split files into 3000 tokens or less (because of 4096 token constraint in asking questions in chat)
# Step 2. Re-assemble the text using tokenized version 
# Step 3. Split into sentences 
# Step 4. Generate vector embeddings for each sentence, tracking which set of full 3k token context it came from 
# Step 5. At question answer time, identify the sentence most similar to the question asked, retrieve the full context, and pass that into a gpt model. 

import os 
import sys
import math
import openai 
import tiktoken
import configparser
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


batch_size = 256
config = configparser.ConfigParser()
config.read('config.ini')
openai.orgaization='Personal'
openai.api_key = config.get('secrets', 'openai_api_key')


def get_embeddings(texts): 
    embeddings = openai.Embedding.create(
        input=texts, 
        model='text-embedding-ada-002')['data']

    
    results = []
    for i, e in enumerate(embeddings):
        # print(i, e['embeddings'])
        results.append(np.array(e['embedding']))

    vector_array = np.stack(results, axis=1).transpose()

    return vector_array 
    
enc = tiktoken.encoding_for_model('gpt-3.5-turbo')

df_smc = pd.read_csv('data/unprocessed_sitemap_content.csv', index_col=0)

# Simple regex based cleaning of sitemap content that is repeated across many pages and not relevant. 
df_smc['new_page_text'] = df_smc['page_text'].replace(r'\n ', '\n', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r'\n{2,}', '\n\n', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r' {1,}\n', '\n', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r'Facebook\nTwitter\nPinterest\nInstagram\nLinkedIn\n', '', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r'© 2022 Tradera\n\n\n.+\n.+\n.+\n.+\n\n.+\n.+\n\n.+\n\n.+\n\n.+\n\n.+\n\n.+\n\n.+\n\n.+\n\n.+\n\nSpara', '', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r'Köp\n.+\n.+\n.+\n.+\n.+\n\n\n.+\n.+\n.+\n.+\n.+\n.+\n\n\n.+\n.+\n.+\n.+\n.+\n\n\n.+\n.+\n.+\n.+\n.+\nJobb\n', '', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r'Info Tradera\nInspiration\nOm oss\nKontakta oss\n', '', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r'Genvägar\n\n\nFraktkalkylatorn\n.+\n.+\n.+\n.+\n.+\n.+\n.+\n.+\nBudgivning\n', '', regex=True)
df_smc['new_page_text'] = df_smc['new_page_text'].replace(r'\n{2,}', '\n\n', regex=True)


# Import the FAQs from the knowledge base and change format so it is like the info pages 
df_faq = pd.read_csv('data/knowledge_base.csv')
df_faq['new_page_text'] = df_faq['title'] + '\n' + df_faq['content']
df_faq['page_url'] = 'FAQs'

# Combine and 
df_content = pd.concat([df_faq[['page_url', 'new_page_text']], df_smc[['page_url', 'new_page_text']]])
df_content = df_content.loc[df_content['new_page_text'].str.len() > 10]
df_content.reset_index(drop=True, inplace=True)
df_content['tokenized'] = df_content['new_page_text'].apply(lambda x: enc.encode(x))
df_content['num_tokens'] = df_content['tokenized'].str.len()



# Split the content into information that is max len 3000 tokens 
df_tokens = df_content[['tokenized']].explode(column=['tokenized'])
df_tokens['orig_index'] = df_tokens.index
df_tokens['token_num'] = df_tokens.groupby('orig_index').cumcount()
df_tokens['context_segment'] = df_tokens['token_num']//3000
df_tokens = df_tokens[['tokenized', 'orig_index', 'context_segment']]


df_reagg = df_tokens.groupby(['orig_index', 'context_segment']).agg({'tokenized': lambda x: x.tolist()}).reset_index()
df_reagg['context_segment_text'] = df_reagg['tokenized'].apply(lambda x: enc.decode(x))
df_reagg['len_tokenized'] = df_reagg['context_segment_text'].apply(lambda x: len(x))
df_reagg = df_reagg.merge(df_content[['page_url']], left_on=['orig_index'], right_index=True, how='left')

# Now, I need page level lookup and sentence level lookup 
df_pll = df_reagg[['orig_index', 'context_segment', 'context_segment_text', 'page_url']]
df_sll = df_pll.copy()[['context_segment_text']]

# Split the page/context grain sentences into indviduals, then get sentence embeddings for each one. This will allow us to do a lookup after. 
df_sll = pd.DataFrame(df_sll['context_segment_text'].str.split('\n').explode())
df_sll = df_sll.loc[df_sll['context_segment_text'].str.replace('\s', '', regex=True).str.len() > 0]
df_sll['page_level_lookup_index'] = df_sll.index

# Drop duplicates after sentences have been split. Since FAQs are first in the list, we will keep  the first closest match. 
df_sll.drop_duplicates(subset=['context_segment_text'], inplace=True)


# Extra preprocessing on individual questions, to reduce noise in the lookup table 
#df_sll.sort_values(by=['context_segment_text'], inplace=True)
df_sll['context_segment_text'] = df_sll['context_segment_text'].str.replace('\s+', ' ', regex=True)
df_sll = df_sll.loc[~df_sll['context_segment_text'].str.contains('^\s\d{1,4}\sSEK\s', regex=True)] # Remove any lines that are just numbers
df_sll = df_sll.loc[~df_sll['context_segment_text'].str.contains('^\s+\d{1,}\skr\s', regex=True)] # Remove any lines that are just numbers
df_sll.reset_index(drop=True, inplace=True)
df_sll['batch'] = df_sll.index // batch_size 

# Save the numpy array corresponding to the batch number, then stack them all vertically. 
# The indices will correspond to the indices in df_sll. 

batches = df_sll['batch'].unique()
embeddings = []

for b in batches: 
    df_sll_batch = df_sll.loc[df_sll['batch'] == b]
    
    # Okay. So, I send in the batch, get the embeddings, save them to disk, then re-assemble them all together...
    try:
        batch_embeddings = get_embeddings(list(df_sll_batch['context_segment_text']))
        embeddings.append(batch_embeddings)
        np.save('data/cached_sentence_level_embeddings/' + 'batch_' + str(b) + '.npy', batch_embeddings)
        print('Completed %d of %d batches' % (b, len(batches)))
    except Exception as ex: 
        print('Error for batch %d: %s' % (b, ex))


# Now, assemble all the batches together, save them to disk, and save the sentene and page level embeddings to disk as well 
df_sll.to_csv('data/sentence_level_lookup.csv')
df_pll.to_csv('data/page_level_lookup.csv')
sentence_embeddings = np.concatenate(embeddings, axis=0)
np.save('data/all_sentence_level_embeddings.npy', sentence_embeddings)

