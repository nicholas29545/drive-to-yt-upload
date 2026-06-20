from pathlib import Path
import zipfile
import logging

def extract_zipfile(full_path: Path, unzipped_dir: Path, extension: str):
    logging.info(f'Extracting .{extension} file from "{full_path}"...')
    
    if not zipfile.is_zipfile(full_path):
        raise FileNotFoundError(f'{full_path} is invalid')
    
    with zipfile.ZipFile(full_path, 'r') as zip_file:
        zip_file.extractall(unzipped_dir)
        
    unzipped_full_path = unzipped_dir / f'{full_path.stem}.{extension}'
    
    if not unzipped_full_path.is_file():
        raise FileNotFoundError(f'{unzipped_full_path} not found')
    
    return unzipped_full_path