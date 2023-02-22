import json
import logging
import os
import sys
from typing import Any

import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cda_dl.downloader import Downloader
from cda_dl.main import parse_args
from cda_dl.utils import is_folder, is_video

LOGGER = logging.getLogger(__name__)


directory = os.path.abspath(os.path.dirname(__file__))
VIDEO_DATA = json.load(open(os.path.join(directory, "video_data.json"), "r"))[
    "videos"
]
FOLDER_DATA = json.load(
    open(os.path.join(directory, "folder_data.json"), "r")
)["folders"]


def test_is_video() -> None:
    for video in VIDEO_DATA:
        assert is_video(video["url"]) is True

    for folder in FOLDER_DATA:
        assert is_video(folder["url"]) is False


def test_is_folder() -> None:
    for video in VIDEO_DATA:
        assert is_folder(video["url"]) is False

    for folder in FOLDER_DATA:
        assert is_folder(folder["url"]) is True


def test_list_resolutions_and_exit_folder(caplog: Any) -> None:
    for folder in FOLDER_DATA:
        args = parse_args(["-R", folder["url"]])
        with pytest.raises(SystemExit, match=""):
            Downloader(args)
            assert (
                "Flaga -R jest dostępna tylko dla filmów."
                f" {folder['url']} jest folderem!"
                in caplog.text
            )


def test_list_resolutions_and_exit_video(caplog: Any) -> None:
    for video in VIDEO_DATA:
        if not video["resolutions"]:
            continue
        args = parse_args(["-R", video["url"]])
        with pytest.raises(SystemExit, match=""):
            Downloader(args)
            assert (
                f"Dostępne rozdzielczości dla {video['url']}:" in caplog.text
            )


def test_list_resolutions_and_exit_unknown(caplog: Any) -> None:
    url = "https://www.google.com"
    args = parse_args(["-R", url])
    with pytest.raises(SystemExit, match=""):
        Downloader(args)
        assert f"Nie rozpoznano adresu url: {url}" in caplog.text


def test_handle_r_flag_folder(caplog: Any) -> None:
    for folder in FOLDER_DATA:
        res = "720p"
        args = parse_args(["-r", res, folder["url"]])
        Downloader(args)
        assert (
            f"Flaga -r jest dostępna tylko dla filmów. {folder['url']} jest"
            " folderem!"
            in caplog.text
        )


def test_handle_r_flag_video(caplog: Any) -> None:
    for video in VIDEO_DATA:
        if not video["resolutions"]:
            continue
        for res in video["invalid_resolutions"]:
            args = parse_args(["-r", res, video["url"]])
            Downloader(args)
            assert (
                f"{res} rozdzielczość nie jest dostępna dla {video['url']}"
                in caplog.text
            )


def test_handle_r_flag_unknown(caplog: Any) -> None:
    url = "https://www.google.com"
    res = "720p"
    args = parse_args(["-r", res, url])
    Downloader(args)
    assert f"Nie rozpoznano adresu url: {url}" in caplog.text
