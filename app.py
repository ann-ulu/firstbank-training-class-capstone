from dash import Dash, html, dcc, callback, Output, Input, State
import plotly.express as px
import pandas as pd
import requests
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import time

app = Dash(__name__)

def generate_image_from_prompt(prompt):
    try:
        # Get Azure OpenAI Service settings
        load_dotenv()
        api_base = os.getenv("AZURE_OAI_ENDPOINT")
        api_key = os.getenv("AZURE_OAI_KEY")
        api_version = '2023-06-01-preview'

        # Make the initial call to start the job
        url = "{}openai/images/generations:submit?api-version={}".format(api_base, api_version)
        headers= { "api-key": api_key, "Content-Type": "application/json" }
        body = {
            "prompt": prompt,
            "n": 2,
            "size": "512x512"
        }
        submission = requests.post(url, headers=headers, json=body)

        # Get the operation-location URL for the callback
        operation_location = submission.headers['Operation-Location']

        # Poll the callback URL until the job has succeeded
        status = ""
        while (status != "succeeded"):
            time.sleep(3) # wait 3 seconds to avoid rate limit
            response = requests.get(operation_location, headers=headers)
            status = response.json()['status']

        # Get the results
        image_url = response.json()['result']['data'][0]['url']

        # Return the URL for the generated image
        return image_url

    except Exception as ex:
        print(ex)

def generate_prompt(value):
    load_dotenv()
    azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
    azure_oai_key = os.getenv("AZURE_OAI_KEY")
    azure_oai_model = os.getenv("AZURE_OAI_MODEL")

    client = AzureOpenAI(
        azure_endpoint = azure_oai_endpoint, 
        api_key=azure_oai_key,  
        api_version="2023-05-15"
    )

    response = client.chat.completions.create(
        model=azure_oai_model,
        temperature=0.7,
        max_tokens=120,
        messages=[
            {"role": "system", "content": "You are an expert at generating DallE prompts"},
            {"role": "user", "content": value}
        ]
    )

    print(response.choices[0].message.content)

    prompt = response.choices[0].message.content

    image_url = generate_image_from_prompt(prompt)

    return prompt, image_url

app.layout = html.Div([
    # Logo added here
    html.Img(src="assets/logo.png", style={'position': 'fixed', 'top': '20px', 'left': '20px', 'height': '80px', 'width': 'auto'}),
    
    html.H1(children='Iconic Image Generation App', style={'textAlign':'center', 'padding-top':'5px', 'font-size':'45px', 'color':'#2D1866', 'text-shadow': '0 0 5px #A8D2EA, 0 0 10px #A8D2EA, 0 0 15px #A8D2EA, 0 0 20px #A8D2EA, 0 0 30px #A8D2EA, 0 0 40px #A8D2EA, 0 0 55px #A8D2EA, 0 0 75px #A8D2EA'}),
    html.H3(children=['Experience the power of our cutting-edge AI generator, allowing you to effortlessly transform your ideas into stunning visuals.',      html.Br(), 'Bring your creativity to life!'],style={'textAlign':'center','font-size':'17px', 'color':'#2D1866'}),
    
    html.Div([
        html.Div([
            dcc.Input(
                id="basic-prompt-input",
                type="text",
                placeholder="Describe what you want to see",
                size="90",
                style={
                    "padding-top":"13px",
                    "padding-bottom":"13px",
                    "height": "50px",
                    "margin-right": "5px",  # Reduce the right margin to eliminate space
                    "border-radius": "25px",
                    "font-size": "18px",
                    "font-weight": "bold",
                    "text-align": "center",
                    "background-color": "#BAD5DE",
                    "border": "none",
                    "color": "black",
                    "box-shadow": "2px 2px 5px rgba(0, 0, 0, 0.3)"
                }
            ),
            html.Button('Submit', id='submit-button', n_clicks=0, style={
                "border": "none",  # Remove border
                "border-radius": "15px",
                "background-color": "#b4d6e0",
                "color": "#2D1866",
                "font-size": "16px",
                "font-weight": "bold",
                "padding": "20px 33px",
                "box-shadow": "0px 8px 15px rgba(0, 0, 0, 0.1)",  # Add realistic shadow
            })
        ], style={"display": "flex", "justify-content": "center", "align-items": "center"}),  # Align items to center

        html.Div(id="prompt-output", children='', style={'display': 'flex', 'justify-content': 'center', 'width':'30%', 'margin-left':'535px', 'height':'50px', 'margin-top':'10px'}),  # Center align the prompt text box
        
        html.Div(id="image-generation-output", children=''),
    ], style={'margin-top': '20px'}),  # Margin top added here
    
    html.Div([
        dcc.Loading(
            id="loading-image",
            type="default",
            children=html.Img(id="generated-image", style={'width': '500px', 'height': '350px', 'display': 'block', 'margin': 'auto', 'border-radius': '20px', 'margin-top':'30px'}), style={'background-image': 'url("https://image.shutterstock.com/image-photo/colorful-nebula-galaxy-spiral-deep-260nw-595633797.jpg")'}
            #children=html.Img(id="generated-image", style={'width': '500px', 'height': '350px', 'display': 'block', 'margin': 'auto', 'border-radius': '20px', 'margin-top':'30px'})
        ),
    ]),
    
    html.Footer(children="this image geneartor app was developed by the iconic team", style={'textAlign': 'center', 'padding': '20px', 'position': 'fixed', 'bottom': '0', 'width': '100%', 'font-style': 'italic', 'font-size': '18px'})  # Set the font style to italic
], style={
    'position': 'fixed',  # Ensures the element is fixed in the viewport
    'top': 0,  # Aligns the element to the top of the viewport
    'left': 0,  # Aligns the element to the left of the viewport
    'height': '100vh',
    'width': '100vw',
    'margin': 0,  # Remove any inherited margins
    'padding': 0,  # Remove any padding
    'background-image': 'url(https://images.unsplash.com/photo-1618005198919-d3d4b5a92ead?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)',
    'background-size': 'cover',
    'background-repeat': 'no-repeat',
})

@app.callback(
    [Output('generated-image', 'src'), Output('prompt-output', 'children')],
    Input('submit-button', 'n_clicks'),
    State('basic-prompt-input', 'value'),
    prevent_initial_call=True
)
def generate_image(n_clicks, value):
    prompt, image_url = generate_prompt(value)
    # Limit the prompt to 25 words
    truncated_prompt = ' '.join(prompt.split()[:25])
    return image_url, html.Textarea(f"Regenerated Prompt: {truncated_prompt}", style={'width': '90%', 'height': '100px', 'resize': 'none', 'background-color': 'transparent', 'border':'none', 'font-size':'14px', 'font-style': 'italic'})
if __name__ == '__main__':
    app.run(debug=True)
