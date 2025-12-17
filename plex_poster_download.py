#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Pull Movie and TV Show poster images from Plex.

Saves poster images from Movie, TV Show, and Music libraries to script's working
directory.

Original Author: Blacktwin
Revised: averageyogi
Requires: plexapi, dotenv, tqdm

 Example:
    python plex_poster_download.py <save_path>

"""

import os
import re
import argparse
import urllib.request
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm

from plex_connection import PlexConnection


load_dotenv(override=True)  # Take environment variables from .env

def create_save_path(save_path: str, library, name: str) -> Path:
    """
    Create save directory and unique path.

    Args:
        save_path (str): Path to save posters
        library (LibrarySection): Plex library
        name (str): Media's name for poster

    Returns:
        Path: _description_
    """
    # Create paths for Movies and TV Shows inside current directory
    if save_path is not None:
        save_dir_path = Path(save_path).joinpath(library[0])
    else:
        save_dir_path = Path.cwd().joinpath(f"Posters/{library[0]}")
    os.makedirs(save_dir_path, exist_ok=True)
    image_path = save_dir_path.joinpath(f"{name}.png")

    # Check if file already exists and save
    if image_path.exists():
        i = 1
        while image_path.with_stem(f"{name}_{i}").exists():
            i += 1
        image_path = image_path.with_stem(f"{name}_{i}")

    return image_path

def download_images(save_path: str, library, name: str, thumb_url: str) -> Path:
    """
    Pull posters from URL.

    Args:
        save_path (str): Path to save posters
        library (LibrarySection): Plex library
        name (str): Media's name for poster
        thumb_url (str): Plex URL where poster can be accessed

    Returns:
        Path: Path of save directory
    """
    image_path = create_save_path(save_path, library, name)
    urllib.request.urlretrieve(thumb_url, image_path)
    return image_path.parent

def main(save_path: str = None):
    """
    Saves the posters of items in Plex libraries.

    Args:
        save_path (str, optional): Path to save posters. Defaults to None.
    """
    print("Loading Plex config...")
    plex = PlexConnection(edit_collections=False)
    plex_libraries = plex.get_libraries()

    save_dir_path = ""
    # Get all movies or shows from LIBRARY_NAME
    for library in plex_libraries.items():
        if library[1].type == "photo":
            print("This function does not handle photo libraries.")
            continue
        if library[1].type in ['movie', 'show']:
            lib_type = "video"
        elif library[1].type == "artist":
            lib_type = "audio"
        else:
            print("Unknown library type.")
            continue

        for child in tqdm(
            library[1].all(),
            total=library[1].totalSize,
            ascii=" ░▒█",
            ncols=100,
            desc=library[0],
            unit=library[1].type
        ):
            if lib_type == "audio":
                # Audio libraries have multiple layers in the API
                for album in child.albums():
                    # Clean names of special characters
                    name = re.sub('\\W+', ' ', album.title)
                    # Pull URL for poster
                    if album.thumb is None:
                        continue
                    thumb_url = (
                        f'{os.environ["PLEX_SERVER_PUBLIC_IP"]}{album.images[0].url}'
                        f'?X-Plex-Token={os.environ["PLEX_TOKEN"]}'
                    )
                    save_dir_path = download_images(
                        save_path=save_path,
                        library=library,
                        name=name,
                        thumb_url=thumb_url
                    )
            else:  # lib_type = "video"
                # Clean names of special characters
                name = re.sub('\\W+', ' ', child.title)
                # Add (year) to name
                name = f"{name} ({child.year})"
                # Pull URL for poster
                if child.thumb is None:
                    continue
                thumb_url = (
                    f'{os.environ["PLEX_SERVER_PUBLIC_IP"]}{child.images[0].url}'
                    f'?X-Plex-Token={os.environ["PLEX_TOKEN"]}'
                )
                save_dir_path = download_images(
                    save_path=save_path,
                    library=library,
                    name=name,
                    thumb_url=thumb_url
                )
    print(f"Saved to {save_dir_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "save_path", nargs='?', default=None, help="Path to save posters at, optional, default is cwd",
    )
    args = parser.parse_args()

    main(args.save_path)
