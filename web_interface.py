## ChatGPT Q1:  
## A1: Certainly! Here's an example of Python code using the Flask web framework to create a simple web-based user interface where users can enter text into a search box and receive a response:

# First, make sure you have Flask installed (pip install flask). Then, create a new Python file (e.g., app.py) with the following code:

# python
# Copy code
# from flask import Flask, render_template, request

# app = Flask(__name__)

# @app.route('/')
# def home():
#     return render_template('index.html')

# @app.route('/process', methods=['POST'])
# def process():
#     user_input = request.form['user_input']
#     response = 'Thank you'
#     return render_template('index.html', user_input=user_input, response=response)

# if __name__ == '__main__':
#     app.run()
# Next, create a folder called templates in the same directory as app.py and create a new HTML file named index.html inside the templates folder with the following code:

# html
# Copy code
# <!DOCTYPE html>
# <html>
# <head>
#     <title>Simple Chat Interface</title>
# </head>
# <body>
#     <h1>Simple Chat Interface</h1>
    
#     <div>
#         <form action="/process" method="POST">
#             <input type="text" name="user_input" placeholder="Type something..." />
#             <button type="submit">Send</button>
#         </form>
#     </div>
    
#     <div>
#         <h2>User Input:</h2>
#         <p>{{ user_input }}</p>
#     </div>
    
#     <div>
#         <h2>Response:</h2>
#         <p>{{ response }}</p>
#     </div>
# </body>
# </html>
# Now, when you run the app.py script, it will start a Flask web server, and you can access the user interface by opening your browser and visiting http://localhost:5000. The interface will display a text input field where you can type something and click the "Send" button. The entered text will be shown under "User Input," and the response ("Thank you") will be displayed under "Response."

# This is a simple example, and you can expand upon it to incorporate more complex interactions and logic as needed.

# I hope this helps you get started with your web-based user interface!


import os 
import openai 
import configparser
from flask import Flask, render_template, request

config = configparser.ConfigParser()
config.read('config.ini')
openai.orgaization='Personal'
openai.api_key = config.get('secrets', 'openai_api_key')

history = ''

# Change out the model later. 
# I need an intro prompt, a user prompt, and the model to respond. 
# Ideally, I also have a summary of what the rest of the conversation said, so the model can be prompted. 

# First model, trained within 5 hour limit: ada:ft-personal-2023-05-18-15-50-40'
# Second model, trained after generating 10 questions from each page on sitemap: curie:ft-personal-2023-05-20-18-40-42

def prompt_gpt(context, user_prompt, model='curie:ft-personal-2023-05-20-18-40-42'): 
    response = openai.Completion.create(
        model=model, 
        prompt= "CONTEXT: " +  context + '\nUSER MESSAGE: ' + user_prompt + '\n\n###\n\n')
        # messages=[
        #     {"role": "system", "content": "You are an AI powered customer service agent for a Nordic secondhand auction website marketplace called Tradera. Do your best to answer the customer's questions based on the provided CONTEXT and USER MESSAGE"},
        #     {"role": "user", "content": "CONTEXT: " +  context + '\nUSER MESSAGE: ' + user_prompt + '\n\n###\n\n'}], 
    
    print(response)
    return response['choices'][0]['text']

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    global history

    user_input = request.form['user_input']
    response = prompt_gpt(history, user_input)      
    history += '\nUSER: ' + user_input + '\n\n SYSTEM: ' + response
    
    return render_template('index.html', user_input=user_input, response=response, history=history)

if __name__ == '__main__':
    app.run()