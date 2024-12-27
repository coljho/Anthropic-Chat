# Anthropic-Chat
Simple Streamlit App to Chat with Sonnet 3.5 using a developer key to avoid those pesky anthropic usage limits

## Installation
To install simply clone this repo and create a new python virtual environment 
`python -m venv .venv`
Then activate that virtual environment and run `pip install -r requirements.txt`
Finally, store your anthropic developer key somewhere on your system where it can be retrieved and point to it by changing the path in line 9 of app.py.
Once this is all complete, you can launch the app using `streamlit run app.py`. Be aware of token usage, I generally recommend only purchasing tokens up from with no automated purchasing behavior to manage resource limits carefully.
