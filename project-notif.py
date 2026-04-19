"""
This module provides functionality to compare the version of a project defined in a local `pyproject.toml` file 
with the version hosted on GitHub. It uses asynchronous HTTP requests to fetch the remote version and checks 
if there is an update available.
"""

import tomllib
import aiohttp
import os

LOCAL_PATH = "./pyproject.toml"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Bobcatnesti/alpha_verification_bot/refs/heads/master/pyproject.toml"


async def get_local_version():
    """
    Asynchronously retrieves the version of the project from the local `pyproject.toml` file.
    
    Returns:
        str or None: The version string if the file exists and is readable, otherwise None.
    """
    if not os.path.exists(LOCAL_PATH):
        return None

    with open(LOCAL_PATH, "rb") as f:
        data = tomllib.load(f)

    return data.get("project", {}).get("version")


async def get_remote_version():
    """
    Asynchronously retrieves the version of the project from the remote `pyproject.toml` file hosted on GitHub.
    
    Returns:
        str or None: The version string if the HTTP request is successful and the file content is valid, otherwise None.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(GITHUB_RAW_URL) as resp:
            if resp.status != 200:
                return None

            text = await resp.text()
            data = tomllib.loads(text)

    return data.get("project", {}).get("version")


async def check_update():
    """
    Asynchronously checks for updates by comparing the local and remote versions of the project.
    
    Returns:
        dict or None: A dictionary containing information about whether an update is available, 
                     along with the local and remote version strings. Returns None if either version cannot be retrieved.
    """
    local = await get_local_version()
    remote = await get_remote_version()

    if not local or not remote:
        return None

    return {
        "update": local != remote,
        "local": local,
        "remote": remote
    }