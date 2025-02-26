import os
import requests
from flask import Flask, redirect, url_for, session, request, jsonify
import msal
import jwt

# Initialize Flask app
app = Flask(__name__)

# Configurations (replace with your actual details)
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
tenant_id = os.getenv("TENANT_ID")
authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = ["User.Read"]
redirect_uri = "http://localhost:5000/getAToken"

# Define scopes (including custom API scope)
custom_scope = f"api://{client_id}/api.access"
scope = ["User.Read", custom_scope]

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
    
     # Get user info from Microsoft Graph API
    graph_response = requests.get('https://graph.microsoft.com/v1.0/me', headers=headers)
    user_info = graph_response.json()

    # Decode token to check scope
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})
    scopes = decoded_token.get("scp", "")

    if "api.access" in scopes:
        return f"✅ Custom API scope verified!<br>Welcome {user_info.get('displayName', 'Unknown')}!<br>User Info: {user_info}"
    else:
        return f"❌ Missing required scope: api.access!<br><br>User Info: {user_info}"

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
        return f"Error: {result.get('error_description', 'Unknown error')}"

# Protected API route (requires 'api.access' scope)
@app.route('/protected')
def protected():
    if not session.get('access_token'):
        return jsonify({"error": "Unauthorized"}), 401
    
    access_token = session['access_token']
    decoded_token = jwt.decode(access_token, options={"verify_signature": False})
    scopes = decoded_token.get("scp", "")

    if "api.access" in scopes:
        return jsonify({"message": "✅ You have access to this protected API!"})
    else:
        return jsonify({"error": "❌ Forbidden: Missing 'api.access' scope!"}), 403

if __name__ == '__main__':
    app.secret_key = os.urandom(24)  # Secret key for Flask session
    app.run(debug=True)
