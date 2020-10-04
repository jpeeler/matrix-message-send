# Matrix Send Message

## Purpose

This provides a dockerized Python script that utilizes [python-nio](https://github.com/poljar/matrix-nio) for sending a Matrix message on the CLI. The intended use case is for me to message myself whenever an autoupgrade has occurred. The secondary goal is to make it generic enough for quick usage in other scenarios as well.

## Usage

### Create configuration file

```console
$ podman run --rm -it ghcr.io/jpeeler/matrix-message-send init --help
Usage: send-message.py init [OPTIONS]

Options:
  --homeserver TEXT     Matrix homeserver  [required]
  --userid TEXT         User ID for message to originate  [required]
  --device-name TEXT    Device name associated with user
  --password TEXT       Password associated with user
  --path TEXT           Path to credentials
  --roomid TEXT         Store room ID for later use
  --endpoint TEXT       Store health endpoint for later use
  --force / --no-force  Overwrite existing configuration details
  --help                Show this message and exit.
```

In element, you can find the internal room ID in the advanced room settings. The format looks like `!SZvgrAMTizkKULviVl:<homeserver URL>`.

Example (password is prompted for and masked when not specified):

`podman run -v ./vol:/conf:Z --rm -it ghcr.io/jpeeler/matrix-message-send init --homeserver <homeserver URL> --userid <user to send message> --path /conf --roomid <internal room ID> --endpoint <homeserver /health>`

### Send message

```console
$ podman run --rm -it ghcr.io/jpeeler/matrix-message-send sendmsg --help
Usage: send-message.py sendmsg [OPTIONS]

Options:
  --roomid TEXT    Room ID to deliver message
  --message TEXT   Message to deliver  [required]
  --path TEXT      Path to credentials
  --endpoint TEXT  health check endpoint to wait to report success
  --help           Show this message and exit.
```

Example:

`podman run -v ./vol:/conf:Z --rm -it ghcr.io/jpeeler/matrix-message-send sendmsg --path /conf --message "Yay it works"`

In the above example, some options are aren't specified that would normally be required. But in this case, the values have been stored in the configuration file.

### Health check

```console
$ podman run --rm -it ghcr.io/jpeeler/matrix-message-send check-health --help
Usage: send-message.py check-health [OPTIONS]

Options:
  --endpoint TEXT     Health endpoint to query
  --attempts INTEGER  Number of health check attempts
  --help              Show this message and exit.
```

Example:

`podman run --rm -it ghcr.io/jpeeler/matrix-message-send check-health --endpoint 'https://<homeserver URL>/health'`

This command is written to be utilized standalone, but note that as shown above if the endpoint is specified with sendmsg, the message won't be sent until after the health check passes.

## Project status

Although Github provides a lot of insight into the health of a project, I like to be explicit. I do not plan on investing any more work into this project, but if I should be so lucky as to receive any contributions I'll be sure to give feedback and merge when appropriate. (I realize that in this case the use of the word "project" is a bit of a stretch.)
