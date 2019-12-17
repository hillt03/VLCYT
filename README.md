# VLCYT

Stream your YouTube playlist in VLC behind the scenes from the command line.

## Check It Out
https://streamable.com/z94tg

## Requirements

64-bit VLC Media Player  
64-bit Python 3.8  

### Note
This project has only been tested on Windows 10  

## Installation
#### Download the requirements in requirements.txt  
`pip install -r requirements.txt`  

#### Download VLCYT  
`pip install vlcyt`

## Usage

Be sure to include quotes around positional arguments.

`python -m vlcyt "<youtube_playlist_url>" [-v "<VLC Install directory>"]`

If you have VLC installed and get a FileNotFound Error, use the -v switch to include the path to your VLC install directory. Otherwise, don't forget to install VLC (64-bit).