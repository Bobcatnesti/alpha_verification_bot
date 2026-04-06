import tomllib
import aiohttp
import os

LOCAL_PATH = "./pyproject.toml"
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Bobcatnesti/alpha_verification_bot/refs/heads/master/pyproject.toml"


async def get_local_version():
    if not os.path.exists(LOCAL_PATH):
        return None

    with open(LOCAL_PATH, "rb") as f:
        data = tomllib.load(f)

    return data.get("project", {}).get("version")


async def get_remote_version():
    async with aiohttp.ClientSession() as session:
        async with session.get(GITHUB_RAW_URL) as resp:
            if resp.status != 200:
                return None

            text = await resp.text()
            data = tomllib.loads(text)

    return data.get("project", {}).get("version")


async def check_update():
    local = await get_local_version()
    remote = await get_remote_version()

    if not local or not remote:
        return None

    return {
        "update": local != remote,
        "local": local,
        "remote": remote
    }