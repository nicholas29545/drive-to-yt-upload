from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import time
import logging

def connect_to_youtube(creds: object):
    youtube_service = build('youtube', 'v3', credentials=creds)
    
    existing_ids = set()
    
    try:
        response = youtube_service.channels().list(
            mine=True,
            part='contentDetails'
        ).execute()
        
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        
        next_page_token = None
        while True:
            playlist_response = youtube_service.playlistItems().list(
                playlistId=uploads_playlist_id,
                part='snippet',
                maxResults=50,
                pageToken=next_page_token
            ).execute()
            
            for item in playlist_response['items']:
                vid = item['snippet']['resourceId']['videoId']
                existing_ids.add(vid)
                
            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break
            
        logging.info(f'Number of existing videos: {len(existing_ids)}')
    
    except Exception as e:
        logging.error(f'Error fetching YouTube videos: {e}')
        return set()
    
    return youtube_service

def upload_video(
    title: str,
    description: str,
    tags: list,
    file_path: Path,
    creds: object,
    category_id: str,
    privacy_status: str,
    schedule_time: str,
    thumbnail_path: Path
    ):
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': category_id
        },
        'status': {
            'privacyStatus': privacy_status,
            'publishAt': schedule_time,
            'selfDeclaredMadeForKids': False
        }

    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)

    request = creds.videos().insert(
        part=','.join(body.keys()),
        body=body,
        media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            logging.info(f'Uploaded {int(status.progress() * 100)}%')
           
    video_id = response['id'] 
    logging.info(f'Waiting for thumbnail endpoint to accept video_id "{video_id}"')
    time.sleep(10)
    
    thumbnail_media = MediaFileUpload(str(thumbnail_path), mimetype='image/jpeg')
    
    try:
        creds.thumbnails().set(
            videoId=video_id,
            media_body=thumbnail_media
        ).execute()
        logging.info(f'Thumbnail set for {video_id}')
        
    except Exception as e:
        logging.error(f'Failed to set thumbnail: {e}. Retrying in 5 seconds...')
        time.sleep(10)
        
        creds.thumbnails().set(
            videoId=video_id,
            media_body=thumbnail_media
        ).execute()
        logging.info('Thumbnail set on retry.') 
    
    logging.info(f'Successfully uploaded video "{response['id']}"')