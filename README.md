
# telegramLightningInvoiceBot

## Description
The `telegramLightningInvoiceBot` is a Telegram bot developed to generate and monitor Bitcoin Lightning Network invoices. It enables Telegram users to create payment requests and track their status efficiently.

## Prerequisites
- Python 3.x
- `python-telegram-bot` library
- A configured and operational Bitcoin Lightning Node
- Access to `lncli` tool

## Features
- `/start`: Initiates interaction with the bot, providing information on its usage.
- `/pay`: Generates a Lightning invoice for a user-specified amount and tracks its payment status.



## Running the Bot
To run the `telegramLightningInvoiceBot`, follow these steps:

1. Navigate to the project directory:
   ```bash
   cd telegramLightningInvoiceBot
   ```

2. Run the bot using Python:
   ```bash
   python3 LightningInvoiceBot.py
   ```

Make sure your Bitcoin Lightning Node is operational and `lncli` is accessible from the environment where you're running the bot.

The bot should now be active and can be interacted with through Telegram.


## Disclaimer
This bot is provided as-is without any warranty and is intended for educational purposes only. Use it at your own risk. The author is not responsible for any financial losses or other damages caused by the use of this bot. Users should exercise caution, as dealing with the Lightning Network involves inherent risks.
