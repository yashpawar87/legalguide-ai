import requests
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def get_firebase_api_key():
    return os.environ.get("FIREBASE_WEB_API_KEY", "")

def sign_in_with_email_and_password(email: str, password: str):
    """
    Calls the Firebase Auth REST API to sign in a user.
    Returns the user's ID token if successful.
    """
    api_key = get_firebase_api_key()
    if not api_key:
        return {"error": "FIREBASE_WEB_API_KEY is not configured in the environment."}
        
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        if "error" in data:
            return {"error": data["error"].get("message", "Authentication failed.")}
            
        return {
            "idToken": data["idToken"],
            "email": data["email"],
            "localId": data["localId"]
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to connect to authentication server: {e}"}
