from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os
import pickle
from pathlib import Path

def authenticate(token_file_full_path: Path, credentials_full_path: Path, SCOPES: list):
    creds = None
        
    if os.path.exists(token_file_full_path):
        with open(token_file_full_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_full_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_file_full_path, 'wb') as token:
            pickle.dump(creds, token)
                    
    return creds