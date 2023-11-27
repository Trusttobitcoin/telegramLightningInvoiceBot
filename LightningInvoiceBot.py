import json
import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Welcome! Send /pay to create a Lightning invoice.')

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Please enter the amount for the invoice:')
    context.user_data['awaiting_amount'] = True

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'awaiting_amount' in context.user_data:
        try:
            amount = int(update.message.text)
            if amount <= 0:
                await update.message.reply_text('Please enter a positive number.')
                return
            invoice_info = await generate_invoice_async(amount)
            if 'error' in invoice_info:
                await update.message.reply_text(f"Error generating invoice: {invoice_info['error']}")
            else:
                await update.message.reply_text(f"Please pay this invoice: {invoice_info['invoice']}")
                context.user_data['rhash'] = invoice_info['rhash']
                asyncio.create_task(check_payment_periodically(invoice_info['rhash'], update, context))
        except ValueError:
            await update.message.reply_text('Invalid amount. Please enter a number.')
        finally:
            del context.user_data['awaiting_amount']

async def generate_invoice_async(amount):
    try:
        expiry_time = 120  # Set the expiry time to 120 seconds (2 minutes)
        process = await asyncio.create_subprocess_shell(
            f"/root/go/bin/lncli addinvoice --amt={amount} --expiry={expiry_time}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            return {'error': stderr.decode()}
        
        invoice_data = json.loads(stdout.decode())
        return {'invoice': invoice_data.get('payment_request', ''), 'rhash': invoice_data.get('r_hash')}
    except Exception as e:
        return {'error': str(e)}

async def check_payment_async(rhash):
    try:
        process = await asyncio.create_subprocess_shell(
            f"/root/go/bin/lncli lookupinvoice {rhash}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return {'error': stderr.decode(), 'settled': False}

        invoice_status = json.loads(stdout.decode())
        return {'settled': invoice_status.get('settled', False)}
    except Exception as e:
        return {'error': str(e), 'settled': False}

async def check_payment_periodically(rhash, update, context):
    timeout = 120  # 120 seconds or 2 minutes
    check_interval = 2  # Check every 2 seconds
    elapsed_time = 0

    while elapsed_time < timeout:
        invoice_status = await check_payment_async(rhash)
        if 'error' in invoice_status:
            await update.message.reply_text(f"Error checking payment: {invoice_status['error']}")
            return
        if invoice_status['settled']:
            await update.message.reply_text("Invoice paid.")
            return
        await asyncio.sleep(check_interval)
        elapsed_time += check_interval

    if elapsed_time >= timeout:
        await update.message.reply_text("Invoice payment timed out.")

if __name__ == '__main__':
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("pay", pay))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    application.run_polling()
