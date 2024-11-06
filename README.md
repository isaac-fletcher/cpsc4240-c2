# cpsc4240-c2

## How to set up environment

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r ./requirements.txt
```

## Notes on debugging

For whatever reason, `aioconsole` (the library that provides `asyncio`-compatible
functions for reading from `stdin`) seems to break exception pretty-printing. Exceptions
get printed up until some threshold, at which point they're cut off.

If you just do Ctrl+C to kill the program after seeing one of these, it will print the rest.