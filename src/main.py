from pathlib import Path
import os
import json
import logging
from .authenticate_credentials import authenticate
from .drive import *
from .youtube import *
from .models import VideoMetadata
from .file_processor import *

def main():
    CREDENTIALS_FULL_PATH = Path('data/credentials/client_secrets.json')
    TOKEN_FILE_FULL_PATH = Path('data/credentials/token.pickle')
    METADATA_FULL_PATH = Path('data/json_files/video_metadata.json')
    LOCAL_DESTINATION = Path('data/videos/zipfiles')
    UNZIPPED_DIR = Path('data/videos/unzipped')
    
    if not LOCAL_DESTINATION.exists():
        os.makedirs(LOCAL_DESTINATION, exist_ok=True)
        
    if not UNZIPPED_DIR.exists():
        os.makedirs(UNZIPPED_DIR, exist_ok=True)
    
    with open(METADATA_FULL_PATH, 'r', encoding='utf-8') as file:
        metadata = json.load(file)
    
    SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/youtube.upload'
    ]
    
    DRIVE_FOLDER_ID = '1qKfZ62Gp_OrMQq4M5umjMo-BLjBwZutc'

    creds = authenticate(TOKEN_FILE_FULL_PATH, CREDENTIALS_FULL_PATH, SCOPES)
    
    drive_service = connect_to_drive(creds, DRIVE_FOLDER_ID)
    youtube_service = connect_to_youtube(creds)
        
    for item in metadata:
        data = VideoMetadata(
            id=item['id'],
            title=item['title'],
            description=item['description'],
            tags=item['tags'],
            thumbnail_path=Path(item['thumbnail_path']),
            schedule_time=item['schedule_time'],
            category_id=item['category_id'],
            privacy_status=item['privacy_status'],
            is_downloaded=item['is_downloaded'],
            is_uploaded=item['is_uploaded']
        )
        
        if not data.is_downloaded:
            zipped_full_path = download_video(service=drive_service, folder_id=DRIVE_FOLDER_ID, filename=item['id'], destination=LOCAL_DESTINATION, extension='zip')
            
            if zipped_full_path:
                data.is_downloaded = True
                
                with open(METADATA_FULL_PATH, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=4)
                
                logging.info(f'Updated metadata for "{data.id}" - "{data.title}"')
                
                unzipped_full_path = extract_zipfile(full_path=zipped_full_path, unzipped_dir=UNZIPPED_DIR, extension='mp4')
        
                upload_video(
                    title=data.title,
                    description=data.description,
                    tags=data.tags,
                    file_path=unzipped_full_path,
                    creds=youtube_service,
                    category_id=data.category_id,
                    privacy_status=data.privacy_status,
                    schedule_time=data.schedule_time,
                    thumbnail_path=data.thumbnail_path
                )
                
                data.is_uploaded = True
                
                os.remove(zipped_full_path)
                os.remove(unzipped_full_path)
                logging.info(f'Deleted zipped and unzipped files for "{data.id}" - "{data.title}"')