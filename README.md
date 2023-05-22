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

See main branch for description of files. 

The main difference in this branch is that I completed fine-tuning a model using both the content
provided in the knowledge base, as well as all question-answer pairs generated programatically 
using GPT. However, even after fine-tuning on ~13k examples, the model was still not usable as a chatbot. 

