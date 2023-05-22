# tradera_chatbot
This repo stores my code for the Tradera technical interview challenge to build a chatbot using OpenAI APIs. 

To run the code locally on your machine, paste the following into the 'config.ini' file. 
[secrets]
openai_api_key = YOUR_API_KEY

Note that you will need to retrain the fine-tuned models and update the model references in code (see further instructions below). 

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

## Detailed Description of Methods and Files: 
