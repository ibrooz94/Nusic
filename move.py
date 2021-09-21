import shutil
import os

directory = "./"
files_in_directory = os.listdir(directory)
filtered_files = [file for file in files_in_directory if file.endswith(".mp3")]
destination = "../"
delete_files = ["cover.jpg", "spotify_results.json", "YT_results.json"]


for file in filtered_files:
    path_to_file = os.path.join(directory, file)
    shutil.move(path_to_file, destination)


for file in delete_files:
    if os.path.exists(file):
        os.remove(file)

