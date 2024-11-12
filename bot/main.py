# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from aiohttp import ClientSession
from time import sleep
import asyncio


def parse_command(command: dict) -> None:
    try:
        if command['action'] == 'execute':
            bash_cmd = command['path'] + ' ' + ' '.join(command['payload'])
            print(bash_cmd)
        elif command['action'] == 'read':
            # handle read
            pass
        elif command['action'] == 'write':
            # handle write
            pass
        else:
            print(f"Unknown action: {command['action']}")
    except Exception as e:
        print(f'Exception in parsing command: {e}')

async def obtain_id() -> dict:
    async with ClientSession() as session:
        url = 'http://localhost:8080/init'
        method = 'GET'
        async with session.request(method, url) as response:
            json_reply = await response.json()
            return json_reply['id']


async def main():
    id = await obtain_id()
    cmd_queue = []
    while True:
        async with ClientSession() as session:
            url = f'http://localhost:8080/check/{id}'
            method = 'GET'
            async with session.request(method, url) as response:
                returned_cmds = await response.json()
                for cmd in returned_cmds:
                    cmd_queue.append(cmd)
        if len(cmd_queue) > 0:
            parse_command(cmd_queue.pop(0))
        sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
