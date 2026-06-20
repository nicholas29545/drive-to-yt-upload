from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import logging
import io
from pathlib import Path

def connect_to_drive(creds: object, DRIVE_FOLDER_ID: str):
    try:
        drive_service = build('drive', 'v3', credentials=creds)
        
        results = drive_service.files().list(
            q=f"'{DRIVE_FOLDER_ID}' in parents and trashed=false",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        
        video_files = results.get('files', [])

        if not video_files:
            logging.warning('Successfully connected, but no files found')
        else:
            folder_info = drive_service.files().get(fileId=DRIVE_FOLDER_ID, fields='name').execute()
            folder_name = folder_info.get('name')
            
            logging.info(f'API is connected. Number of video_files in "{folder_name}": {len(video_files)}')
            
            for item in video_files:
                logging.info(f'{item["name"]} ({item["id"]})')
                
            return drive_service
    
    except Exception as e:
        logging.error(f'Error connecting to drive: {e}')

def download_video(service: object, folder_id: str, filename: str, destination: Path, extension: str):
    filename_with_extension = f'{filename}.{extension}'
    
    query = f"name = '{filename_with_extension}' and '{folder_id}' in parents and trashed = false"
    
    results = service.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, mimeType)',
        pageSize=10
    ).execute()
    
    items = results.get('files', [])
    
    if not items:
        logging.error(f'Error: No file named "{filename_with_extension}" found in folder "{folder_id}"')
        return

    if len(items) > 1:
        logging.warning(f'Multiple files named "{filename_with_extension}" found. Downloading first one')
    
    file_id = items[0]['id']
    
    if destination.is_dir():
        full_path = destination / filename_with_extension
    else:
        full_path = destination if destination.name else Path(filename_with_extension)
        
    logging.info(f'Found file ID "{file_id}". Downloading to {full_path}...')
    
    try:
        request = service.files().get_media(fileId=file_id)
        with io.FileIO(str(full_path), 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
                logging.info(f'Download {int(status.progress() * 100)}% complete')
        logging.info('Download successful')
                
        return full_path
        
    except Exception as e:
        logging.error(f'Error downloading video: {e}')
        
        return None