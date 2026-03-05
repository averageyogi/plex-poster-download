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
from typing import Optional, Union

from dotenv import load_dotenv
from plexapi.library import LibrarySection
from plexapi.video import Show, Movie
from plexapi.audio import Artist, Album
from tqdm import tqdm

from plex_connection import PlexConnection


load_dotenv(override=True)  # Take environment variables from .env

def create_save_path(
    save_path: Optional[Path], library: tuple[str, LibrarySection], name: str
) -> Path:
    """
    Create save directory and unique path.

    Args:
        save_path (Optional[Path]): Path to save posters
        library (LibrarySection): Plex library
        name (str): Media's name for poster

    Returns:
        Path: Unique save path
    """
    if save_path is not None:
        save_dir_path = save_path.joinpath(library[0])
    else:
        # Create path for library posters inside current directory
        save_dir_path = Path.cwd().joinpath(f"Posters/{library[0]}")
    os.makedirs(save_dir_path, exist_ok=True)
    image_path = save_dir_path.joinpath(f"{name}.png")

    # Check if file already exists and append index if so
    if image_path.exists():
        i = 1
        while image_path.with_stem(f"{name}_{i}").exists():
            i += 1
        image_path = image_path.with_stem(f"{name}_{i}")

    return image_path

def grab_url(
    lib_item: Union[Album, Movie, Show], plex: PlexConnection, video_lib: bool
) -> tuple[str, str]:
    """
    Clean item name and get plex library URL of poster.

    Args:
        lib_item (Union[Album, Movie, Show]): Particular plex library item
        plex (PlexConnection): Plex connection
        video_lib (bool): whether or not item is from a video library, for naming convention

    Returns:
        tuple[str,str]: (new filename, poster URL)
    """
    # Clean names of special characters
    name = re.sub('\\W+', ' ', lib_item.title)
    if video_lib:  # Add (year) to name
        name = f"{name} ({lib_item.year})"
    # Pull URL for poster
    thumb_url = (
        # f'{os.environ["PLEX_SERVER_PUBLIC_IP"]}{lib_item.images[0].url}'
        f'{plex.plex_pub_ip if not plex.using_public_ip else plex.plex_ip}{lib_item.images[0].url}'
        f'?X-Plex-Token={os.environ["PLEX_TOKEN"]}'
    )
    return name, thumb_url

def main(save_path: Optional[Path] = None):
    """
    Saves the posters of items in Plex libraries.

    Args:
        save_path (Path, optional): Path to save posters. Defaults to None.
    """
    print("Loading Plex config...")
    plex = PlexConnection(edit_collections=False)
    plex_libraries = plex.get_libraries()

    save_dir_path = ""
    for library in plex_libraries.items():
        if library[1].type == "photo":
            print("This function does not handle photo libraries.")
            continue
        if library[1].type in ["movie", "show"]:
            lib_type = "video"
        elif library[1].type == "artist":
            lib_type = "audio"
        else:
            print("Unknown library type.")
            continue

        if lib_type == "audio":
            artist: Artist
            for artist in tqdm(
                library[1].all(),
                total=library[1].totalSize,
                ascii=" ░▒█",
                ncols=100,
                desc=library[0],
                unit=library[1].type
            ):
                # Audio libraries have multiple layers in the API
                album: Album
                for album in artist.albums():
                    if album.thumb is None:
                        continue
                    name, thumb_url = grab_url(album, plex, video_lib=False)
                    image_path = create_save_path(save_path, library, name)
                    urllib.request.urlretrieve(thumb_url, image_path)
                    save_dir_path = image_path.parent

        else:  # lib_type = "video"
            video: Union[Movie, Show]
            for video in tqdm(
                library[1].all(),
                total=library[1].totalSize,
                ascii=" ░▒█",
                ncols=100,
                desc=library[0],
                unit=library[1].type
            ):
                if video.thumb is None:
                    continue
                name, thumb_url = grab_url(video, plex, video_lib=True)
                image_path = create_save_path(save_path, library, name)
                urllib.request.urlretrieve(thumb_url, image_path)
                save_dir_path = image_path.parent
    print(f"Saved to {save_dir_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "save_path", nargs='?', type=Path, default=None, help="Path to save posters at, optional, default is cwd",
    )
    args = parser.parse_args()

    main(args.save_path)
