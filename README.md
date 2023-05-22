# tradera_chatbot
This repo stores my code for the Tradera technical interview challenge to build a chatbot using OpenAI APIs. 

Note that you may need to fine-tune models and update the references in code to recreate locally. 

## Branches

Each branch contains the code for the different approaches that I tried. 
 - The **main** branch contains code that was written **within the 5h constraint**. 
 - The **post_5h_attempt_1** branch contains code for the second method described below.
 - The **post_5h_semantic_lookup** branch contains code for the third method described below.

## Summary of methods: 
1. Fine tuning a model using only the information provided in the FAQs, then directly sending user questions to the model 

2. Fine tuning a model using the FAQs as well as Question-Answer pairs generated from the content in the sitemap, then directly sending user questions to the 
   model. 

3. Semantic lookup tables: 
- Generate embeddings for all sentences in the FAQs and sitemap content, then store embeddings in a lookup table 
- Generate embeddings for the question asked by the user 
- Evaluate cosine similarity between the user question and the sentences in the lookup tables. Identify the 10 closest sentences 
- Recover the full context around the 10 most similar sentences to the user question. Concatenate the context together and keep the first 3000 tokens. 
- Send the narrowed down context and the user question into a gpt-3.5-turbo model, and ask GPT to answer the question if the answer is present in the context, 
  and to say that no answer was found otherwise. 

## How to recreate locally/file descriptions (branch specific):

1. Update the *config.ini* file in the directory with your own API key: 
'''openai_api_key''' = YOUR_API_KEY'''

2. Run *scrape_sitemap.py* to webscrape the information from the sitemap. 

3. Run *process_sitemap_data.py* to clean the sitemap data. The following operations are done: 
 - Tokenize the sitemap content 
 - Split tokenized sitemap content into smaller chunks, so it is easier for a GPT model to process
 - Reassemble smaller tokenized chunks back into natural text 
 - Use the ChatCompletion endpoint to generate 10 question/answer pairs from each piece of context for fine-tuning 
 - Save the generated questions and answers (~13K) to disk 
 
4. Run *clean_data_for_fine_tuning.py* to combine the information from the knowledge base and generated QAs 
   into a single dataframe and format & save in the way expected by the OpenAPI command line tool 
   
5. Run the openAPI command line tool, pointing to the output of the previous step: 

'''openai tools fine_tunes.prepare_data -f <LOCAL_FILE>'''

6. Using the openAI command line tool, fine-tune your model using the output of the previous step :

'''openai api fine_tunes.create -t <TRAIN_FILE_ID_OR_PATH> -m <BASE_MODEL>'''


7. Edit *web_interface.py* and update the model argument in the '''prompt_gpt''' function definition to point to the model that was fine-tuned in the previous step. 

8. Run *web_interface.py* and navigate to the URL shown to access a basic UI to interact with ChatGPT. You can type your messages for the chatbot here. 

NOTE: This approach runs, but does not produce usable results. See approach 3 on branch **post_5h_semantic_lookup** for a working chatbot prototype. 

