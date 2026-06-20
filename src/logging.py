from pathlib import Path
import logging

def setup_logging():
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent.parent 
    
    data_dir = project_root / 'data'
    log_dir = data_dir / 'logging'
    
    log_dir.mkdir(parents=True, exist_ok=True)
    
    full_logging_path = log_dir / 'app.log'
    
    logging.basicConfig(
        filename=str(full_logging_path),
        filemode='a',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
    )