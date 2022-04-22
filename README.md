# Telegraminology - A Telegram Terminology Bot

A simple Telegram chat bot, that replies to messages containing (only) a [SNOMED-CT](https://www.snomed.org/) concept id
or an [ICD-10](https://www.who.int/standards/classifications/classification-of-diseases) code.

# Usage

1. Clone the repository: `git clone https://github.com/haemka/termbot.git`
2. Copy `example.ini` to `config.ini` and configure as needed:
   1. Get a Telegram bot API access: https://core.telegram.org/bots#3-how-do-i-create-a-bot
   2. Get a WHO ICD API access: https://icd.who.int/icdapi
3. Run via docker with `docker run -v $(pwd)/config.ini:/app/config.ini .` or docker-composei with `docker compose up`.
4. Invite the bot into any channel you like or messsge it directly and send a message containing a single SNOMED-CT 
   concept ID or a single ICD-10 code.

# Function

The bot (currently) needs admin access to a chat in order to read all messsages and reply by itself. Invocation by
special commands (and thus making the admin permission for auto replies optional) is planned.
