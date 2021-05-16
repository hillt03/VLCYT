import pafy
import os
import time
import sys
import threading
import random
import re
from vlcyt.command_handler import CommandHandler
from vlcyt.file_helpers import *
from colorama import Fore, Back, Style


class VLCYT:
    """
    Stream YouTube playlist audio in VLC behind the scenes from the command line.
    """

    command_string = f"{Fore.RESET}{Back.RESET}>"

    def __init__(self, youtube_playlist_url, youtube_api_key, song_info_enabled=True):
        pafy.set_api_key(youtube_api_key)
        self.playlist = pafy.get_playlist2(youtube_playlist_url)  # Pafy playlist object
        self.song_index = 0  # Current song index
        self.song_counter = 0  # Stores how many songs have been played, resets if every song has been played.
        self.total_songs = len(self.playlist)  # Amount of songs in the Pafy object
        self.current_song = None  # Stores the current song
        os.environ["VLC_VERBOSE"] = "-1"  # Decrease verbosity of VLC error output, necessary because errors sometimes occur that spam the screen but otherwise have no effect
        self.vlc_player = vlc.MediaPlayer()  # Stores the VLC object
        self.song_info_enabled = song_info_enabled  # The current song information is printed when the song changes if this is enabled
        self.song_history = []  # Stores indexes of songs that have been played

        # User input
        self.cmds = CommandHandler(self)  # Collects user input on another thread


    def play_playlist_songs(self):
        """
        Play every song in the passed in playlist.
        Note: Skip is handled in command_handler and _get_next_song() is executed following a skip.
        """
        while True:
            if (
                not self.cmds.input_features_enabled()
            ):  # No extra features enabled. Default.
                self._get_next_song()
            elif self.cmds.back_song:  # Back command entered
                self._get_next_song_back()
            elif self.cmds.loop_song:  # Looping enabled
                pass  # we don't need to change the value of self.current_song in this case
            elif self.cmds.shuffle_playlist:  # Shuffling enabled
                self.cmds.back_amount = 0
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
        self.cmds.back_amount = 0
        self._set_current_song(self.song_index)
        self._add_song_to_history()
        self.song_index += 1

    def _get_next_song_back(self):
        """
        Sets the current song to the last played song.
        Supports multiple back commands and shuffle.
        """
        self.cmds.back_amount -= 1
        if len(self.song_history) > abs(self.cmds.back_amount):
            self.song_index = self.song_history.pop(self.cmds.back_amount - 1)
            self._set_current_song(self.song_index)
            self._add_song_to_history()
        else:
            print("No songs remaining in history.")
        self.cmds.back_song = False

    def _get_next_song_shuffling(self):
        """
        Sets the current song to a random unique song in the playlist.
        Even YouTube couldn't write a better shuffling algorithm!
        """
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

    def _get_reformatted_song_date(self, date):
        """
        Returns a reformatted published date.
        """
        year, month, day = date.split()[0].split("-")
        return f"{month}/{day}/{year}"

    def _get_reformatted_song_length(self, original_length_string):
        """
        Returns a reformatted song length.
        """
        if original_length_string.startswith("00:00:0"):  # 00:00:05
            return original_length_string[-1] + " seconds"
        elif original_length_string.startswith("00:00"):  # 00:00:55
            return original_length_string[6:] + " seconds"
        elif original_length_string.startswith("00:0"):  # 00:05:55
            return original_length_string[4:]
        elif original_length_string.startswith("00:"):  # 00:55:55
            return original_length_string[3:]
        elif original_length_string.startswith("0"):  # 05:55:55
            return original_length_string[1:]
        else:
            return original_length_string

    def _clean_title(self):
        """
        Cleans the current song's title.
        """
        song_title = self.current_song.title
        removals_regex = [
            "(\s*\((Official|Audio|Video).*\))",
            "(\s*\[(Official|Audio|Video).*\])",
            "\s*-Lyrics\s*",
            "\(.*Lyric.*\)",
            "\[.*Lyric.*\]",
            "\s*Lyrics\s*",
            "\s*Official Music Video\s*",
            "\s*\[NCS Release\]\s*",
        ]
        rename_song = False
        new_song_name = (self.current_song.title, 0)
        searching_for_matches = True
        while searching_for_matches:
            new_song_name = re.subn(
                "|".join(removals_regex), "", new_song_name[0], flags=re.IGNORECASE
            )
            if new_song_name[1] == 0:
                searching_for_matches = False
            else:
                rename_song = True
        return new_song_name[0] if rename_song else song_title

    def _print_current_song_information(self, print_command_string=True):
        """
        Prints the current song's relevant information.
        """
        if self.song_info_enabled:
            os.system("cls||clear")
            print(
f"""{Fore.CYAN}======================================
{Fore.GREEN}Title:{Fore.RESET} {self._clean_title()}
{Fore.GREEN}Length:{Fore.RESET} {self._get_reformatted_song_length(self.current_song.duration)}
{Fore.GREEN}Views:{Fore.RESET} {self.current_song.viewcount:,d}
{Fore.GREEN}Rating:{Fore.RESET} {round(self.current_song.rating, 2)}
{Fore.GREEN}Date:{Fore.RESET} {self._get_reformatted_song_date(self.current_song.published)}
{Fore.CYAN}======================================
{self.command_string if print_command_string else ""}""",
                end="",
            )

    def _play_current_song(self):
        """
        Plays the current song stored in self.current_song and adds it to song history.
        """
        self._reset_state()
        # Play song
        self.vlc_player.set_mrl(self.current_song.getbestaudio().url_https, ":no-video")
        self.vlc_player.play()

        if not self.cmds.input_thread.is_alive():
            self._print_current_song_information(print_command_string=False)
            print(f"{Fore.YELLOW}===Enter ? to view a list of commands==={Fore.RESET}")
            self.cmds.input_thread.start()
        else:
            self._print_current_song_information()

        # Sleep for duration of song
        self._song_timer()

    def _song_timer(self):
        """
        Loop and check for state change from user input while the song plays.
        """
        time.sleep(0.5)
        while self.vlc_player.is_playing() or self.vlc_is_paused():
            if self.cmds.skip_song:
                self.vlc_player.stop()
                self.cmds.skip_song = False
                break
            if self.cmds.exit_program:
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
        return self.vlc_player.get_state() == vlc.State.Paused


def main():
    if len(sys.argv) == 1:
        if files_exist(get_file_list()):
            (
                youtube_playlist_URL,
                api_key,
                vlc_dir,
            ) = read_playlist_url_api_key_and_vlc_dir_from_file()
        else:
            print('No YouTube playlist stored. Run "python -m vlcyt -h" for help.')
            sys.exit(0)
    else:
        youtube_playlist_URL, api_key, vlc_dir = parse_args()
        write_playlist_url_api_key_and_vlc_dir_to_file(
            youtube_playlist_URL, api_key, vlc_dir
        )

    add_vlc_dir_to_path(vlc_dir)
    global vlc
    import vlc

    vlcyt = VLCYT(youtube_playlist_url=youtube_playlist_URL, youtube_api_key=api_key)
    vlcyt.play_playlist_songs()


if __name__ == "__main__":
    main()
