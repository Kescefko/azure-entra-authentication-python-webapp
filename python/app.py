import os
import requests
from flask import Flask, redirect, url_for, session, request
import msal

# Initialize Flask app
app = Flask(__name__)

# Configurations (replace with your actual details)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = ["User.Read"]
redirect_uri = "http://localhost:5000/getAToken"

# MSAL client app
def _build_msal_app():
    return msal.ConfidentialClientApplication(
        client_id,
        client_credential=client_secret,
        authority=authority
    )

# Start page
@app.route('/')
def index():
    if not session.get('access_token'):
        return redirect(url_for('login'))
    
    # After login, the page will display user info
    access_token = session['access_token']
    headers = {'Authorization': 'Bearer ' + access_token}
    user_info = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers).json()
    
    return f"Welcome {user_info['displayName']}!<br><br>User Info: {user_info}"

# Login page
@app.route('/login')
def login():
    msal_app = _build_msal_app()
    auth_url = msal_app.get_authorization_request_url(scope, redirect_uri=redirect_uri)
    return redirect(auth_url)

# Callback page where MSAL redirects after login
@app.route('/getAToken')
def get_a_token():
    msal_app = _build_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        request.args['code'], # TODO
        redirect_uri=redirect_uri, 
        scopes=scope
    )

    if "access_token" in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('index'))
    else:
        return "Error: " + result.get("error_description")

if __name__ == '__main__':
    app.secret_key = os.urandom(24)  # Secret key for Flask session
    app.run(debug=True)
