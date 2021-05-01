import os
import appdirs
import argparse

app_dir = appdirs.user_data_dir() + "/VLCYT/"

def is_valid_file(parser, arg):
    """
    Function used to check if a valid VLC path was given.
    """
    if not os.path.exists(arg):
        parser.error(
            f"The filepath {arg} does not exist! Be sure to include quotes around the path, view help for more info."
        )

def parse_args():
    """
    Parses passed in CLI arguments. 
    Output: tuple: YouTube playlist URL string, VLC Install Directory
    """
    parser = argparse.ArgumentParser(description="Streams YouTube Playlist in VLC")
    parser.add_argument(
        "youtube_playlist_URL",
        metavar="YouTube Playlist URL",
        help="URL to a YouTube Playlist. Include quotes around the URL.",
    )
    parser.add_argument(
        "-y",
        metavar="YouTube API Key",
        help="Specify your YouTube API Key. Get a YouTube Data V3 API Key from https://developers.google.com/youtube/v3/getting-started.",
    )
    parser.add_argument(
        "-v",
        metavar="VLC Install Directory",
        type=lambda x: is_valid_file(parser, x),
        help='If you\'re getting a FileNotFound error, use this option to pass in your VLC install directory. Example: "C:\\Program Files\\VideoLAN\VLC" Be sure to include the quotes.',
    )
    args = parser.parse_args()
    if args.v is None:
        args.v = "C:\Program Files\VideoLAN\VLC"
    return args.youtube_playlist_URL, args.y, args.v


def add_vlc_dir_to_path(vlc_dir):
    """
    Note: The python-vlc module depends on a .dll in the VLC install directory.
    Adds the VLC install directory to the path and imports the vlc module.
    """
    os.add_dll_directory(vlc_dir)
    os.chdir(app_dir)
    


def read_playlist_url_api_key_and_vlc_dir_from_file():
    """
    Reads previously stored YouTube playlist URL, API key, and VLC directory.
    Output: tuple: playlist url, vlc dir
    """
    url = ""
    api_key = ""
    vlc_dir = ""
    with open(app_dir + "playlist.txt", "r") as playlist_file:
        url = playlist_file.read()
    with open(app_dir + "api_key.txt", "r") as api_key_file:
        api_key = api_key_file.read()
    with open(app_dir + "vlc_dir.txt", "r") as vlc_dir_file:
        vlc_dir = vlc_dir_file.read()
    return url, api_key, vlc_dir


def write_playlist_url_api_key_and_vlc_dir_to_file(playlist_url, api_key, vlc_dir):
    """
    Stores the playlist url and vlc dir.
    """
    if not os.path.isdir(app_dir):
        os.mkdir(app_dir)
    with open(app_dir + "playlist.txt", "w+") as playlist_file:
        playlist_file.write(playlist_url)
    with open(app_dir + "api_key.txt", "w+") as api_key_file:
        api_key_file.write(api_key)
    with open(app_dir + "vlc_dir.txt", "w+") as vlc_dir_file:
        vlc_dir_file.write(vlc_dir)

def files_exist(file_list):
    return False not in [os.path.isfile(i) for i in file_list]

def get_file_list():
    return [app_dir + "playlist.txt", app_dir + "vlc_dir.txt", app_dir + "api_key.txt"]

def clear_data():
    for file in get_file_list():
        os.remove(file)

def main():
    clear_data()

if __name__ == "__main__":
    main()