import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from stl import mesh
import threading

processed_files = set()

class STLFileHandler(FileSystemEventHandler):
    def __init__(self, scale_factor):
        self.scale_factor = scale_factor
        self.known_files = set()

    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith('.stl') and not event.src_path.endswith(' .stl'):
            if event.src_path not in processed_files:
                processed_files.add(event.src_path)
                self.scale_stl(event.src_path)
        else:
            self.known_files.add(event.src_path)
            threading.Timer(10, self.check_for_new_stl).start()

    def on_modified(self, event):
        if not event.is_directory:
            if event.src_path in self.known_files:
                pass
            elif event.src_path.endswith('.stl') and not event.src_path.endswith(' .stl') and event.src_path not in processed_files:
                processed_files.add(event.src_path)
                self.scale_stl(event.src_path)

    def check_for_new_stl(self):
        for temp_file in list(self.known_files):
            stl_file = temp_file.replace('.tmp', '.stl')
            if os.path.exists(stl_file) and stl_file not in processed_files and not stl_file.endswith(' .stl'):
                processed_files.add(stl_file)
                self.scale_stl(stl_file)
                self.known_files.remove(temp_file)

    def scale_stl(self, input_file):
        try:
            your_mesh = mesh.Mesh.from_file(input_file)
            your_mesh.vectors *= self.scale_factor
            output_file = input_file.replace('.stl', ' .stl')
            your_mesh.save(output_file)
            os.remove(input_file)
            self.known_files.discard(input_file)
        except Exception:
            pass

    def on_deleted(self, event):
        if event.src_path in self.known_files:
            self.known_files.discard(event.src_path)
        if event.src_path in processed_files:
            processed_files.discard(event.src_path)

def start_watching(directory_to_watch, scale_factor):
    event_handler = STLFileHandler(scale_factor)
    observer = Observer()
    observer.schedule(event_handler, directory_to_watch, recursive=False)
    observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
    scale_factor = 0.9

    if os.path.exists(downloads_folder):
        start_watching(downloads_folder, scale_factor)
