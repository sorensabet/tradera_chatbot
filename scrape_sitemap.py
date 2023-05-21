## I genereated the following code using the following prompt to chatgpt: 
## Q: Can you generate python code for me to scrape an xml sitemap and save the content?
  
# import requests
# import xml.etree.ElementTree as ET

# def scrape_sitemap(url, save_path):
#     response = requests.get(url)
#     if response.status_code == 200:
#         tree = ET.fromstring(response.content)
        
#         # Iterate over each 'url' element in the sitemap
#         for url_element in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
#             loc_element = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
#             if loc_element is not None and loc_element.text:
#                 # Extract the URL from the 'loc' element
#                 url = loc_element.text
                
#                 # Save the URL to a file
#                 with open(save_path, 'a') as file:
#                     file.write(url + '\n')
                    
#         print("Scraping and saving of the sitemap completed.")
#     else:
#         print("Failed to retrieve the sitemap.")

# # Specify the URL of the XML sitemap
# sitemap_url = 'https://example.com/sitemap.xml'

# # Specify the file path where you want to save the scraped URLs
# save_file_path = 'scraped_urls.txt'

# # Call the function to scrape the sitemap and save the content
# scrape_sitemap(sitemap_url, save_file_path)

# PROMPT: Do youj have the ability to extract text from html?
# A: import requests
# from bs4 import BeautifulSoup

# def extract_text_from_html(url):
#     # Send a GET request to the URL
#     response = requests.get(url)
#     if response.status_code == 200:
#         # Parse the HTML content using BeautifulSoup
#         soup = BeautifulSoup(response.content, 'html.parser')
        
#         # Extract the text from the parsed HTML
#         text = soup.get_text(separator=' ')
#         return text
#     else:
#         print("Failed to retrieve the HTML content.")
#         return None

# # Specify the URL of the webpage containing the HTML
# url = 'https://example.com'

# # Call the function to extract text from the HTML
# result = extract_text_from_html(url)
# if result:
#     print(result)


## Q: Does the presence of blank spaces in a text influence the decision you make when answering questions? 
## A: The presence of blank spaces or extra white spaces in a text generally does not influence the decision I make when answering questions. As an AI language model, I focus more on the content and meaning of the text rather than specific formatting details.
# However, it's important to note that excessive or irregular blank spaces can sometimes introduce ambiguity or affect the clarity of the text. In such cases, it may be helpful to provide well-formatted and structured questions to ensure better understanding and accuracy in the responses.
# If you have any specific concerns or examples where the presence of blank spaces could impact the interpretation of a question, please feel free to provide more details, and I'll be glad to assist you further.


## Q:Please give me Python code to replace all newline characters and multiple spaces with a single space in a text column of a pandas dataframe
## A: df['Text'] = df['Text'].str.replace('\n', ' ').str.replace('\s+', ' ', regex=True)




##  I modified the above answer to scrape the content on the pages 

import sys
import requests
import tiktoken
import regex as re
import pandas as pd 
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

unhelpful_pages = ['https://info.tradera.com/']

sitemap_url = 'https://info.tradera.com/page-sitemap.xml'

response = requests.get(sitemap_url)
if response.status_code != 200:
    sys.exit() 

tree = ET.fromstring(response.content)

results = []
for url_element in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
    loc_element = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    
    if loc_element is not None and loc_element.text: 
        loc_url = loc_element.text      # This is url column 
        page_response = requests.get(loc_url)
        sc = response.status_code 
        page_text = BeautifulSoup(page_response.content, 'html.parser').get_text(separator=' ') if sc==200 else 'Failed to retrieve the html content'
        
        results.append({'page_url': loc_url, 'page_text': page_text})


# Save in pandas dataframe, replace multiple occurences of newlines/blank spaces
df_smc = pd.DataFrame.from_dict(results)
df_smc.to_csv('data/unprocessed_sitemap_content.csv')
df_smc = df_smc.loc[~df_smc['page_url'].isin(unhelpful_pages)]






# Step 1. Split files into 3000 tokens or less (because of 4096 token constraint in asking questions in chat)
# Step 2. Re-assemble the text using tokenized version 
# Step 3. Split into sentences 
# Step 4. Generate vector embeddings for each sentence, tracking which set of full 3k token context it came from 
# Step 5. At question answer time, identify the sentence most similar to the question asked, retrieve the full context, and pass that into a gpt model. 


# df_tokens = df_smc[['tokenized']].explode(column=['tokenized'])
# df_tokens['orig_index'] = df_tokens.index
# df_tokens['new_index'] = range(0, len(df_tokens), 1)
# df_tokens['context_segment'] = df_tokens['new_index']//400
# df_tokens = df_tokens[['tokenized', 'orig_index', 'context_segment']]

    

# # Save sitemap content to txt files for quick visual inspection 
# for row in df_smc.iterrows(): 
    
#     if row[1]['num_tokens'] > 3000:        
#         with open('data/sample_sitemap_content/' + str(row[0]) + '.txt', 'w') as f:
#             f.write(row[1]['new_page_text'])


