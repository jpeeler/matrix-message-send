#!/usr/local/bin/python3

import asyncio
import json
import os
import sys
import time

import click
import requests
from nio import AsyncClient, LoginResponse, RoomSendResponse
from requests.api import request

CONFIG_FILE = "config.json"


@click.group()
def cli():
    pass


def write_details_to_disk(
    resp: LoginResponse, homeserver, full_path, roomid, endpoint
) -> None:
    """Writes the required login details to disk so we can log in later without
    using a password.

    Arguments:
        resp {LoginResponse} -- the successful client login response.
        homeserver -- URL of homeserver, e.g. "https://matrix.example.org"
    """
    # open the config file in write-mode
    with open(full_path, "w") as f:
        # write the login details to disk
        to_write = {
            "homeserver": homeserver,  # e.g. "https://matrix.example.org"
            "user_id": resp.user_id,  # e.g. "@user:example.org"
            "device_id": resp.device_id,  # device ID, 10 uppercase letters
            "access_token": resp.access_token,  # cryptogr. access token
        }
        if roomid:
            to_write["room_id"] = roomid
        if endpoint:
            to_write["endpoint"] = endpoint
        json.dump(
            to_write,
            f,
        )


@cli.command()
@click.option("--homeserver", required=True, help="Matrix homeserver")
@click.option("--userid", required=True, help="User ID for message to originate")
@click.option(
    "--device-name",
    default="matrix-nio-messenger",
    help="Device name associated with user",
)
@click.option(
    "--password", prompt=True, hide_input=True, help="Password associated with user"
)
@click.option("--path", default=".", help="Path to credentials")
@click.option("--roomid", help="Store room ID for later use")
@click.option("--endpoint", help="Store health endpoint for later use")
@click.option(
    "--force/--no-force", default=False, help="Overwrite existing configuration details"
)
def init(*args, **kwargs) -> None:
    asyncio.get_event_loop().run_until_complete(do_init(*args, **kwargs))


async def do_init(
    homeserver, userid, device_name, password, path, roomid, endpoint, force
) -> None:
    full_path = os.path.join(path, CONFIG_FILE)
    if os.path.exists(full_path):
        if not force:
            print("Config file already exists, requires --force")
            return
        os.remove(full_path)

    if not (homeserver.startswith("https://") or homeserver.startswith("http://")):
        homeserver = "https://" + homeserver

    client = AsyncClient(homeserver, userid)
    resp = await client.login(password, device_name=device_name)

    # check that we logged in succesfully
    if isinstance(resp, LoginResponse):
        write_details_to_disk(resp, homeserver, full_path, roomid, endpoint)
    else:
        print(f'homeserver = "{homeserver}"; user = "{userid}"')
        print(f"Failed to log in: {resp}")
        sys.exit(1)

    print(
        "Logged in using a password. Credentials were stored.",
    )
    await client.close()


@cli.command()
@click.option("--roomid", help="Room ID to deliver message")
@click.option("--message", required=True, help="Message to deliver")
@click.option(
    "--path", default=".", help="Path to credentials"
)  # should match init option
@click.option("--endpoint", help="health check endpoint to wait to report success")
def sendmsg(*args, **kwargs):
    asyncio.get_event_loop().run_until_complete(do_sendmsg(*args, **kwargs))


async def do_sendmsg(roomid, message, path, endpoint) -> None:
    full_path = os.path.join(path, CONFIG_FILE)
    if not os.path.exists(full_path):
        print(f"Didn't find {full_path}, perhaps you should run init first")
        return

    # open the file in read-only mode
    with open(full_path, "r") as f:
        config = json.load(f)
        client = AsyncClient(config["homeserver"])
        client.access_token = config["access_token"]
        client.user_id = config["user_id"]
        client.device_id = config["device_id"]

        if not roomid:
            try:
                roomid = config["room_id"]
            except KeyError:
                print("Must either specify roomid or put it config file")
                raise

        if endpoint:
            do_check_health(endpoint, 10)
        else:
            try:
                endpoint = config["endpoint"]
            except KeyError:
                pass
            else:
                do_check_health(endpoint, 10)

        resp = await client.room_send(
            roomid,
            message_type="m.room.message",
            content={
                "msgtype": "m.text",
                "body": message,
            },
        )

    if isinstance(resp, RoomSendResponse):
        print("Logged in using stored credentials. Sent message.")
    else:
        print(f"Bad response: {resp}")
    await client.close()


@cli.command()
@click.option(
    "--endpoint",
    default="http://localhost:8008/health",
    help="Health endpoint to query",
)
@click.option("--attempts", default=10, help="Number of health check attempts")
def check_health(*args, **kwargs) -> bool:
    do_check_health(*args, **kwargs)


def do_check_health(endpoint, attempts) -> bool:
    for x in range(1, attempts + 1):
        try:
            r = requests.get(endpoint, timeout=5)
        except (requests.Timeout, requests.ConnectionError) as e:
            print(f"Unable to connect to {endpoint}... attempt {x}/{attempts}")
            pass
        else:
            if r.ok:
                print("Health OK")
                return True
            else:
                r.raise_for_status()
        time.sleep(2)
    else:
        sys.exit(1)


if __name__ == "__main__":
    cli()