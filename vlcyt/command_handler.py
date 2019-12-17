import threading
from colorama import Fore


class CommandHandler:
    """
    Handles user input for VLCYT
    """

    _help_commands = ["?", "help"]
    _volume_commands = ["volume", "v"]
    _skip_commands = ["skip", "s", "next", "n", "forward", "f"]
    _play_commands = ["play", "pause", "p"]
    _repeat_commands = ["repeat", "replay", "r"]
    _back_commands = ["back", "b"]
    _loop_commands = ["loop", "l"]
    _shuffle_commands = ["shuffle"]
    _exit_commands = ["exit", "quit", "q"]

    def __init__(self, vlcyt):
        self.vlcyt = vlcyt
        self.input_thread = threading.Thread(target=self._get_input)
        self.input_thread.daemon = True

    def _get_input(self):
        """
        Gathers user input from the input thread and executes commands.
        """
        print("===Enter ? to view a list of commands===")
        while True:
            command_name, command_value = self._get_command()
            # print(f"-----Command name: {command_name} |---Value: {command_value}")
            if command_name in self._help_commands:
                self.command_help()
            elif command_name in self._volume_commands:
                self.command_set_volume(command_value)
            elif command_name in self._skip_commands:
                self.command_skip_song(command_value)
            elif command_name in self._play_commands:
                self.command_p()
            elif command_name in self._repeat_commands:
                self.command_repeat()
            elif command_name in self._back_commands:
                self.command_back()
            elif command_name in self._loop_commands:
                self.command_loop()
            elif command_name in self._shuffle_commands:
                self.command_shuffle()
            elif command_name in self._exit_commands:
                self.vlcyt.exit_program = True
            else:
                print("Invalid command")

    def _get_command(self):
        """
        Processes a command from the user.
        Output: tuple: command name string, command value string
        """
        command = ""
        while command == "":
            command = input(self.vlcyt.command_string).lower()
        split_command = command.split()
        try:
            command_name = split_command[0]
            command_value = split_command[1]
        except IndexError:
            command_value = None
        return command_name, command_value

    def command_help(self):
        print(
            f"""
{Fore.MAGENTA}======================================
{Fore.YELLOW}NOTE: Most commands have multiple aliases separated by commas, use whichever you prefer.

{Fore.CYAN}VLCYT Commands:

{Fore.GREEN}?, help{Fore.WHITE}
Opens this help menu and shows whether or not looping and shuffling are enabled.

{Fore.GREEN}volume, v{Fore.WHITE}
Adjust the volume (0 - 100).

{Fore.GREEN}skip, s, next, n, forward, f{Fore.WHITE}
Skips song(s).
For example: Entering "skip" will skip one song,
entering "skip 5" will skip 5 songs.

{Fore.GREEN}play, pause, p{Fore.WHITE}
Plays/Pauses the current song.

{Fore.GREEN}repeat, replay, r{Fore.WHITE}
Repeats the current song one time.

{Fore.GREEN}back, b{Fore.WHITE}
Skips to the last song played.

{Fore.GREEN}loop, l{Fore.WHITE}
Enables looping.
The current song will keep playing until looping is disabled.

{Fore.GREEN}shuffle{Fore.WHITE}
Shuffles the playlist without repeating until every song has been played.

{Fore.GREEN}exit, quit, q{Fore.WHITE}
Closes the program.
{Fore.MAGENTA}======================================
{Fore.CYAN}---Settings---{Fore.RESET}
{Fore.GREEN}Looping:{Fore.RESET} {f"{Fore.GREEN}Enabled{Fore.RESET}" if self.vlcyt.loop_song else f"{Fore.RED}Disabled{Fore.RESET}"}
{Fore.GREEN}Shuffling:{Fore.RESET} {f"{Fore.GREEN}Enabled{Fore.RESET}" if self.vlcyt.shuffle_playlist else f"{Fore.RED}Disabled{Fore.RESET}"}
{Fore.CYAN}--------------{Fore.RESET}"""
        )

    def command_set_volume(self, volume):
        """
        Sets VLC volume.
        """
        try:
            volume = int(volume)
        except (TypeError, ValueError):
            print(f"{Fore.RED}Bad input.{Fore.RESET} Enter an integer from 0 - 100.")
            return
        if 0 <= volume <= 100:
            if (
                self.vlcyt.vlc_player.audio_set_volume(volume) == 0
            ):  # Returns 0 if volume was set
                print(f"Volume set to {Fore.GREEN}{volume}{Fore.RESET}")
        else:
            print(f"{Fore.RED}Volume out of range.{Fore.RESET} Range: 0 - 100")

    def command_skip_song(self, amount_to_skip):
        """
        Skips the current song.
        Round robins if it causes the song counter to go over the total amount of songs in the playlist.
        """

        if amount_to_skip is not None:
            try:
                amount_to_skip = int(amount_to_skip)
            except (TypeError, ValueError):
                print(f"{Fore.RED}Bad input.{Fore.RESET} Enter a number.")
                return

        if amount_to_skip in [1, None]:
            self.vlcyt.song_index = (
                self.vlcyt.song_index + 1
                if self.vlcyt.song_index < self.vlcyt.total_songs
                else 0
            )
            self.vlcyt.skip_song = True
        elif amount_to_skip > 1:
            potential_index = self.vlcyt.song_index + amount_to_skip
            if potential_index <= self.vlcyt.total_songs:
                self.vlcyt.song_index += amount_to_skip - 1
                self.vlcyt.skip_song = True
            else:  # Round robin
                total_multiplier = potential_index // self.vlcyt.total_songs
                self.vlcyt.song_index = (
                    potential_index - 1 - self.vlcyt.total_songs * total_multiplier
                )
                self.vlcyt.skip_song = True
        else:
            print(f"{Fore.RED}Bad input.{Fore.RESET} Enter a value greater than 0.")

    def command_repeat(self):
        """
        Repeats the current song.
        """
        self.vlcyt.vlc_player.set_time(0)

    def command_p(self):
        """
        Plays/Pauses the current song.
        """
        self.vlcyt.vlc_player.pause()

    def command_back(self):
        """
        Play last song in history.
        """
        if self.vlcyt.song_history:
            self.vlcyt.back_song = True
            self.vlcyt.skip_song = True
        else:
            print(f"{Fore.RED}No songs in history{Fore.RESET}")

    def command_loop(self):
        """
        Enables/Disables looping the current song.
        """
        if self.vlcyt.loop_song == False:
            self.vlcyt.loop_song = True
            print(f"Looping {Fore.GREEN}enabled.{Fore.RESET}")
        else:
            self.vlcyt.loop_song = False
            print(f"Looping {Fore.RED}disabled.{Fore.RESET}")

    def command_shuffle(self):
        if self.vlcyt.shuffle_playlist == False:
            self.vlcyt.shuffle_playlist = True
            print(f"Shuffle {Fore.GREEN}enabled.{Fore.RESET}")
        else:
            self.vlcyt.shuffle_playlist = False
            print(f"Shuffle {Fore.RED}disabled.{Fore.RESET}")
