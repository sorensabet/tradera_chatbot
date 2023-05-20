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
import pandas as pd 
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup



sitemap_url = 'https://info.tradera.com/page-sitemap.xml'
save_file_path = 'scraped_urls.txt'

response = requests.get(sitemap_url)
if response.status_code != 200:
    sys.exit() 

tree = ET.fromstring(response.content)

results = []

# url_counter = 0
for url_element in tree.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
    loc_element = url_element.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
    
    if loc_element is not None and loc_element.text: 
        loc_url = loc_element.text      # This is url column 
        page_response = requests.get(loc_url)
        sc = response.status_code 
        page_text = BeautifulSoup(page_response.content, 'html.parser').get_text(separator=' ') if sc==200 else 'Failed to retrieve the html content'
        
        results.append({'page_url': loc_url, 'page_text': page_text})

    ## Limit number of requests for testing 
    # url_counter += 1 
    # if url_counter >3:
    #     break

# Save in pandas dataframe, replace multiple occurences of newlines/blank spaces with single space
# based on ChatGPT's feedback that excessive/irregular blank spaces can cause problems. 

df_urls = pd.DataFrame.from_dict(results)
df_urls['page_text'] = df_urls['page_text'].str.replace('\n', ' ').str.replace('\s+', ' ', regex=True)

# Save the text data locally. 
df_urls.to_csv('data/info_page_content.csv')

