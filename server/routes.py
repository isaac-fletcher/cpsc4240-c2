# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from aiohttp import web
from aiohttp.web import Response
from aiohttp.web_request import Request
from context import Command, GlobalContext
from json import loads


def init(request: Request) -> Response:
    ctx: GlobalContext = request.app["ctx"]
    id = ctx.create_bot()

    print(f"Bot {id} registered!")

    return web.json_response({"id": id})

async def result(request: Request) -> Response:
    result = await request.json()

    if result is None:
        return web.Response(status=400)

    print(result)

    return web.Response(status=200)

def check(request: Request) -> Response:
    id = request.match_info.get("id")

    if id is None:
        return web.Response(status=400)

    ctx: GlobalContext = request.app["ctx"]
    commands = ctx.extract_commands(id)

    if commands is None:
        return web.Response(status=400)

    return web.json_response([command.as_dict() for command in commands])


ALL_ROUTES = [
    web.get('/init', init),
    web.get("/check/{id}", check),
    web.post("/result/", result)
]
