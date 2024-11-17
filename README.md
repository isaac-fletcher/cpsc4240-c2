# cpsc4240-c2

## How to set up environment

```bash
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -r ./requirements.txt
```

## Running

For the server, run `server/main.py` with an output directory specified. Any commands, reads and
writes will write output to `/tmp/output-folder/<id>/<index>`.

```bash
(.venv) $ python ./server/main.py /tmp/output-folder 
```

For the client, just run `bot/main.py`

```bash
(.venv) $ python ./bot/main.py
```

## Notes on debugging

For whatever reason, `aioconsole` (the library that provides `asyncio`-compatible
functions for reading from `stdin`) seems to break exception pretty-printing. Exceptions
get printed up until some threshold, at which point they're cut off.

If you just do Ctrl+C to kill the program after seeing one of these, it will print the rest.