# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from aiohttp import ClientSession
import asyncio

async def obtain_id() -> dict:
    async with ClientSession() as session:
        url = 'http://localhost:8080/init'
        method = 'GET'
        async with session.request(method, url) as response:
            json_reply = await response.json()
            return json_reply['id']


def main():
    id = asyncio.run(obtain_id())
    print(id)
 

if __name__ == "__main__":
    main()
