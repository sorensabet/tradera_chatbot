# Summary of methods:  
3. Semantic lookup tables: 
- Generate embeddings for all sentences in the FAQs and sitemap content, then store embeddings in a lookup table 
- Generate embeddings for the question asked by the user 
- Evaluate cosine similarity between the user question and the sentences in the lookup tables. Identify the 10 closest sentences 
- Recover the full context around the 10 most similar sentences to the user question. Concatenate the context together and keep the first 3000 tokens. 
- Send the narrowed down context and the user question into a gpt-3.5-turbo model, and ask GPT to answer the question if the answer is present in the context, 
  and to say that no answer was found otherwise. 

## How to recreate locally/file descriptions (branch specific):

*process_sitemap_data.py* generates and stores embeddings for all sentences in the FAQs and sitemap content 

*question_lookup_functionality.py* Is responsible for generating embeddings for the user's question, narrowing down the relevant context, and sending the context + question to ChatGPT's ChatCompletion endpoint to see if the answer can be found. 


This method works the best of the 3 that I tried, although it still struggles with some of the questions. 

Note that this method doesn't have a dedicated UI, and you need to interact with the chatbot through the console when running question_lookup_functionality.py 


