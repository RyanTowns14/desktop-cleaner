import time
import os
import shutil
import uuid
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

FILE_TYPES = {
    "Images": [".png", ".jpg", ".gif"],
    "Documents": [".pdf", ".docx", ".txt", ".pptx"],
    "Videos": [".mp4", ".mov"],
    "Archives": [".zip", ".rar"],
    "Audio": [".mp3", ".wav"]
}


def move_file(file_path, folder_path):
    if os.path.isfile(file_path):
        extension = os.path.splitext(file_path)[1].lower()
        if extension:
            subfolder_name = f"{extension[1:].upper()} Files"
            subfolder_path = create_subfolder(folder_path, subfolder_name)
            shutil.move(file_path, subfolder_path)
            print(f"Moved: {file_path} -> {subfolder_path}")


def create_subfolder(folder_path, subfolder_name):
    subfolder_path = os.path.join(folder_path, subfolder_name)
    if not os.path.exists(subfolder_path):
        os.makedirs(subfolder_path)
    return subfolder_path


def safe_move(src, dst_folder):
    base = os.path.basename(src)
    dst = os.path.join(dst_folder, base)

    if os.path.exists(dst):
        name, ext = os.path.splitext(base)
        new_name = f"{name}_{uuid.uuid4().hex[:6]}{ext}"
        dst = os.path.join(dst_folder, new_name)

    shutil.move(src, dst)
    print(f"Moved: {src} -> {dst}")


def clean_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.startswith('.'):
            continue

        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_extension = filename.split('.')[-1].lower()
            if file_extension:
                subfolder_name = f"{file_extension.upper()} Files"
                subfolder_path = create_subfolder(folder_path, subfolder_name)
                safe_move(file_path, subfolder_path)


def start_watching(folder_path):
    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory:
                move_file(event.src_path, folder_path)

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f"Watching {folder_path} for new files...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print("Stopped watching.")


if __name__ == "__main__":
    print("Desktop Cleaner Script")
    folder_path = input("Enter the folder path you want to clean and watch: ").strip()
    if os.path.isdir(folder_path):
        clean_folder(folder_path)
        print("Cleaning complete")

        start_watching(folder_path)
    else:
        print("Invalid folder path. Please ensure path is correct and try again.")
