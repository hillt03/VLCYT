# VLCYT

Stream your YouTube playlist in VLC behind the scenes from the command line.

## Check It Out
https://streamable.com/z94tg

## Requirements

[64-bit VLC Media Player](https://get.videolan.org/vlc/3.0.8/win64/vlc-3.0.8-win64.exe)  
[64-bit Python 3.8](https://www.python.org/ftp/python/3.8.0/python-3.8.0-amd64.exe)  

### Note
This project has only been tested on Windows 10.  

## Installation

`pip install git+https://github.com/hillt03/VLCYT`

## Usage

Be sure to include quotes around arguments.

`python -m vlcyt ["<youtube_playlist_url>" -v "<VLC Install directory>"]`


If you have VLC installed and get a FileNotFound Error, use the -v switch to include the path to your VLC install directory. Otherwise, don't forget to install VLC (64-bit).

After running for the first time, you can then simply enter `python -m vlcyt` and the last playlist you passed in will begin playing.

### Example

`python -m vlcyt "https://www.youtube.com/watch?v=8jrN6Kz2XbU&list=PLPVigFOpn3YjTdJ3-hIILmeP3jsjXntOU&index=1" -v "C:\Program Files\VideoLAN\VLC"`

After this initial command, do the following to load your stored settings:
`python -m vlcyt`

## Commands

**NOTE:** Most commands have multiple aliases separated by commas, use whichever you prefer.

### ?, help  
Opens the help menu and shows whether or not looping and shuffling are enabled.

### volume, v  
Adjust the volume (0 - 100).

### skip, s, next, n, forward, f  
Skips song(s).  
For example: Entering "skip" will skip one song,
entering "skip 5" will skip 5 songs.

### play, pause, p  
Plays/Pauses the current song.

### repeat, replay, r  
Repeats the current song one time.

### back, b  
Skips to the last song played.

### loop, l  
Enables looping.
The current song will keep playing until looping is disabled.

### shuffle  
Shuffles the playlist without repeating until every song has been played.

### exit, quit, q  
Closes the program.

## Links

[GitHub](https://github.com/hillt03/VLCYT)  
[PyPI](https://pypi.org/project/VLCYT/)