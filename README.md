# plex-poster-download

Pull Movie and TV Show poster images from your Plex libraries.

Saves poster images from Movie, TV Show, and Music libraries to script's working
directory.

## Setup

<details>
<summary>Virtual environment</summary>

### Create/activate a virtual environment

```bash
# Virtualenv modules installation (Linux/Mac based systems)
python3 -m venv env
source env/bin/activate

# Virtualenv modules installation (Windows based systems)
python -m venv env
.\env\Scripts\activate

# Virtualenv modules installation (Windows based systems if using bash)
python -m venv env
source ./env/Scripts/activate
```

</details>

---
Install dependencies

```bash
pip install -r requirements.txt
```

Create .env file from [.env.example](./.env.example) with Plex credentials
(server IP address, api token, and library names).

Public IP is optional if you will only run script locally to the Plex server.

Your Plex token can be found
**[here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)**

From the XML information of a library item (the same place the Plex token was found) you can find the Plex GUID of
that specific library item to use for accurate identification. Otherwise, you can use the provided library dumping
command to get a list of the names and GUIDs for all items in the provided libraries.

Create a config.yml file from [config.template.yml](./config.template.yml) with the names of your Plex Libraries.

## Usage

Simply run the script. By default, the posters will be saved in a folder in the current directory. You can also provide a new directory to save them at.

```bash
python plex_poster_download.py <save_path>
```

Examples:

```bash
python plex_poster_download.py
```

```bash
python plex_poster_download.py "./Poster Downloads"
```
