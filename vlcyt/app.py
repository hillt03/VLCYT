import argparse
import pafy
import os
import time
import sys
import threading
import random
from vlcyt.command_handler import CommandHandler
from colorama import Fore, Back, Style


class VLCYT:
    """
    Stream YouTube playlist audio in VLC behind the scenes from the command line.
    """

    command_string = f"{Fore.RESET}{Back.RESET}>"

    def __init__(self, playlist_url, song_info_enabled=True):
        self.playlist = pafy.get_playlist2(playlist_url)  # Pafy playlist object
        self.song_index = 0  # Current song index
        self.song_counter = 0  # Stores how many songs have been played, resets if every song has been played.
        self.total_songs = len(self.playlist)  # Amount of songs in the Pafy object
        self.current_song = None  # Stores the current song
        self.vlc_player = vlc.MediaPlayer()  # Stores the VLC object
        self.song_info_enabled = song_info_enabled  # The current song information is printed when the song changes if this is enabled

        self.song_history = []  # Stores indexes of songs that have been played
        self.song_in_history = False  # True if there's a song in song_history

        # User input
        self.cmds = CommandHandler(self)
        self.input_thread_started = False

        # Command helpers
        self.skip_song = False  # Becomes True if the user enters the skip command
        self.exit_program = False  # Becomes True if the user enters the exit command
        self.loop_song = False  # Becomes True if the user enters the loop command
        self.shuffle_playlist = False  # Becomes True if the user enters the shuffle command
        self.back_song = False  # Becomes True if the user enters the back command
        self.back_amount = 1  # Stores how many indexes back will be popped from song_history to get songs in history

    def play_playlist_songs(self):
        """
        Play every song in the passed in playlist.
        """
        while True:
            if (
                not self.loop_song
                and not self.shuffle_playlist
                and not self.back_song
                and not self.skip_song
            ):  # No extra features enabled. Default.
                self._get_next_song()
            elif self.skip_song:  # Song(s) skipped
                self.skip_song = False
                self.back_amount = 0
                self._set_current_song(self.song_index)
                self._add_song_to_history()
            elif self.back_song:  # Back command entered
                self._get_next_song_back()
            elif self.loop_song:  # Looping enabled
                pass  # we don't need to change the value of self.current_song in this case
            elif self.shuffle_playlist:  # Shuffling enabled
                self.back_amount = 0
                self._get_next_song_shuffling()
            self._play_current_song()

    def _set_current_song(self, index):
        """
        Sets the current song to the index that was passed in.
        """
        self.current_song = self.playlist[index]

    def _get_next_song(self):
        """
        Sets the current song to the next song index and adds it to song_history.
        """
        self.back_amount = 0
        self._set_current_song(self.song_index)
        self._add_song_to_history()
        self.song_index += 1

    def _get_next_song_back(self):
        """
        Sets the current song to the last played song.
        Supports multiple back commands and shuffle.
        """
        self.back_amount -= 1
        if len(self.song_history) > abs(self.back_amount):
            self.song_index = self.song_history.pop(self.back_amount - 1)
            self._set_current_song(self.song_index)
            self._add_song_to_history()
        else:
            print("No songs remaining in history.")
        self.back_song = False

    def _get_next_song_shuffling(self):
        """
        Sets the current song to a random unique song in the playlist.
        Even YouTube couldn't write a better shuffling algorithm!
        """
        if self.song_in_history:
            found_unique_random = False
            while not found_unique_random:
                random_int = random.randint(0, self.total_songs - 1)
                if random_int not in self.song_history:
                    self.song_index = random_int
                    self._set_current_song(random_int)
                    self._add_song_to_history()
                    found_unique_random = True
                elif self.song_counter == self.total_songs:
                    self.song_history = [self.song_history[-1]]
        else:
            self.song_index = random.randint(0, self.total_songs)
            self._set_current_song(self.song_index)
            self._add_song_to_history()

    def _print_current_song_information(self):
        """
        Prints the current song's relevant information.
        """
        if self.song_info_enabled:
            os.system("cls||clear")
            print(
                f"""
{Fore.CYAN}======================================
{Fore.GREEN}Title:{Fore.RESET} {self.current_song.title}
{Fore.GREEN}Length:{Fore.RESET} {self.current_song.duration}
{Fore.GREEN}Views:{Fore.RESET} {self.current_song.viewcount:,d}
{Fore.GREEN}Rating:{Fore.RESET} {round(self.current_song.rating, 2)}
{Fore.CYAN}======================================
{self.command_string}""",
                end="",
            )

    def _play_current_song(self):
        """
        Plays the current song stored in self.current_song and adds it to song history.
        """

        self._reset_state()
        # Play song
        song_url = self.current_song.getbestaudio().url
        self.vlc_player.set_mrl(song_url, ":no-video")
        self.vlc_player.play()
        if not self.input_thread_started:
            self.cmds.input_thread.start()
            self.input_thread_started = True
        self._print_current_song_information()

        # Sleep for duration of song
        self._song_timer()

    def _song_timer(self):
        """
        Loop and check for state change from user input while the song plays.
        """
        time.sleep(0.5)
        while self.vlc_player.is_playing() or self.vlc_is_paused():
            if self.skip_song:
                self.vlc_player.stop()
                self.skip_song = False
                break
            if self.exit_program:
                Fore.RESET
                Back.RESET
                sys.exit(0)
            time.sleep(0.5)

    def _reset_state(self):
        """
        Resets the song history to only contain the last song in the history if every song in the playlist has been played.
        """
        self.song_counter += 1
        if len(self.song_history) == self.total_songs:
            self.song_history = [self.song_history[-1]]
            self.song_counter = 0
            return True
        return False

    def _add_song_to_history(self):
        """
        Adds the current song index to song_history.
        """
        self.song_history.append(self.song_index)

    def vlc_is_paused(self):
        """
        Check if the VLC player is paused.
        """
        return True if self.vlc_player.get_state() == vlc.State.Paused else False


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
        help="URL to a YouTube Playlist",
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
    return args.youtube_playlist_URL, args.v


def add_vlc_dir_to_path(vlc_dir):
    """
    Note: The python-vlc module depends on a .dll in the VLC install directory.
    Adds the install directory to the path and imports the vlc module.
    """
    app_dir = os.getcwd()
    os.add_dll_directory(vlc_dir)
    os.chdir(app_dir)
    global vlc
    import vlc


def read_playlist_and_VLC_url_from_file():
    """
    Reads previously stored YouTube playlist URL and VLC directory.
    Output: tuple: playlist url, vlc dir
    """
    url = ""
    vlc_dir = ""
    with open("data/playlist.txt", "r") as playlist_file:
        url = playlist_file.read()
    with open("data/vlc_dir.txt", "r") as vlc_dir_file:
        vlc_dir = vlc_dir_file.read()
    return url, vlc_dir


def write_playlist_url_and_vlc_dir_to_file(playlist_url, vlc_dir):
    """
    Stores the playlist url and vlc dir.
    """
    if not os.path.isdir("./data"):
        os.mkdir("./data")
    with open("./data/playlist.txt", "w+") as playlist_file:
        playlist_file.write(playlist_url)
    with open("./data/vlc_dir.txt", "w+") as vlc_dir_file:
        vlc_dir_file.write(vlc_dir)


def main():
    if len(sys.argv) == 1:
        if os.path.exists("data/playlist.txt") and os.path.exists("data/vlc_dir.txt"):
            youtube_playlist_URL, vlc_dir = read_playlist_and_VLC_url_from_file()
        else:
            print('No YouTube playlist stored. Run "python -m vlcyt -h" for help.')
            sys.exit(0)
    else:
        youtube_playlist_URL, vlc_dir = parse_args()
        write_playlist_url_and_vlc_dir_to_file(youtube_playlist_URL, vlc_dir)

    add_vlc_dir_to_path(vlc_dir)
    vlcyt = VLCYT(youtube_playlist_URL)
    vlcyt.play_playlist_songs()


if __name__ == "__main__":
    main()
