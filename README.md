# Canary
 [![Discord](https://img.shields.io/discord/236668784948019202.svg)](https://discord.gg/HDHvv58)

Canary is a Python3 bot designed for the McGill University Community Discord Server. The bot provides helper functions to users, as well as fun functions, a quote database and custom greeting messages. 

## Build Statuses

| Master |  [![Build Status](https://travis-ci.org/idoneam/Canary.svg?branch=master)](https://travis-ci.org/idoneam/Canary)  |
|--------|---|
| **Dev**    |  [![Build Status](https://travis-ci.org/idoneam/Canary.svg?branch=dev)](https://travis-ci.org/idoneam/Canary) |

## Installation

Dependencies are managed with pipenv which can be installed via pip with:
```bash
python3 -m pip install pipenv
```

Dependencies may be installed using pipenv with the following command:
```bash
pipenv install
```

Development dependencies (YAPF) can be installed alongside all other dependencies with:
```bash
pipenv install --dev
```

You may enter the virtual environment generated by the pipenv installation with:
```bash
pipenv shell
```

Or simply run the bot with:
```bash
pipenv run python3 Main.py
```

In order to run bots on Discord, you need to [create a bot account](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token).

Set your Discord bot token in the `config.ini` file within the `config` directory. Also change your Database file path as well as Greeting and Farewell messages, if desired.

## Running the bot
Run `python3 Main.py` in your shell. Ensure that your Discord token is set in the `config.ini` file within the `config` directory.

## Code Linting
We format our code using Google's [YAPF](https://github.com/google/yapf). Our builds will reject code that do not conform to the standards defined in [`.style.yapf`](https://github.com/idoneam/Canary/blob/master/.style.yapf) . You may format your code using :

```
yapf --recursive --in-place .
```
and ensure your code conforms to our linting with :
```
yapf --diff --recursive .
```
## Contributions
Contributions are welcome, feel free to fork our repository and Open a Pull Request or Open an Issue.
