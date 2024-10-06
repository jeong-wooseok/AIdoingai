import os
import shutil
from datetime import datetime
import logging

# 로깅 설정
log_file = os.path.join(os.path.expanduser("~"), "Documents", "file_move_log.txt")
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def setup_folders():
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    temp_folder = os.path.join(desktop_path, "temp")
    today_folder = os.path.join(temp_folder, datetime.now().strftime("%Y%m%d"))
    
    os.makedirs(temp_folder, exist_ok=True)
    os.makedirs(today_folder, exist_ok=True)
    
    logging.info(f"Desktop Path: {desktop_path}")
    logging.info(f"Temp Folder: {temp_folder}")
    logging.info(f"Today's Folder: {today_folder}")
    
    return desktop_path, today_folder

def move_files(source_dir, destination_dir):
    extensions = ['.xlsx', '.xls', '.pptx', '.ppt', '.docx', '.doc', '.zip', '.csv', '.py', '.txt', '.pdf','.ipynb']
    moved_files = 0
    
    for filename in os.listdir(source_dir):
        if any(filename.lower().endswith(ext) for ext in extensions):
            source_path = os.path.join(source_dir, filename)
            dest_path = os.path.join(destination_dir, filename)
            try:
                shutil.move(source_path, dest_path)
                logging.info(f"Moved file: {filename} to {dest_path}")
                moved_files += 1
            except Exception as e:
                logging.error(f"Error moving file {filename}: {str(e)}")
    
    return moved_files

def main():
    logging.info("Script started")
    
    desktop_path, today_folder = setup_folders()
    moved_files = move_files(desktop_path, today_folder)
    
    logging.info(f"Total files moved: {moved_files}")
    logging.info("File collection process complete.")

if __name__ == "__main__":
    main()
