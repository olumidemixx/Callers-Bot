import asyncio
import os
import re  
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder,Application, CommandHandler, MessageHandler, filters, ContextTypes
import logging  # Import the logging module
nest_asyncio.apply()
from aiohttp import web
from pyngrok import ngrok
import sys
# Define the chat IDs for the groups you want to listen to and forward messages to
LISTEN_GROUP_1 = -4738886886
LISTEN_GROUP_2 = -4719726677
list_of_listen_groups = [LISTEN_GROUP_1,LISTEN_GROUP_2]
list_of_eligible_senders = [6364570277,5279072931]
FORWARD_GROUP_1 = -4630238263
FORWARD_GROUP_2 = -4692625781
list_of_receive_groups = [FORWARD_GROUP_1,FORWARD_GROUP_2]
list_of_receive_groups += list_of_listen_groups
 
solana_patterns = [r'[0-9A-HJ-NP-Za-km-z]{32,44}',r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b']
ethereum_patterns = [r'0x[a-fA-F0-9]{40}', r'\b[a-fA-F0-9]{42}\b']
message = ""
BOT_TOKEN = '7944971005:AAFNmeBPLqc0CKwHau95K4ICvtlx2nNzjm8'

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set the logging level to INFO

# Define the list of administrators
administrators = [6364570277]  # Replace with actual admin user IDs

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logging.info(f"Start command received from {update.effective_user.id}")  # Log when the start command is received
    await update.message.reply_text('Bot started!')

async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    
    if update.effective_chat.id in list_of_listen_groups: 
        if update.effective_user.id in list_of_eligible_senders:
            if any(re.search(pattern, update.message.text) for pattern in solana_patterns + ethereum_patterns):
                # Send messages asynchronously to all groups in the list
                await asyncio.gather(
                    *(context.bot.send_message(chat_id=group_id, text=update.message.text) for group_id in list_of_receive_groups)
                )
            logging.info("not part of eligible messages")
        else:
            logging.info("not part of eligible callers")

    else:
        logging.info("not part of eligible chats")
    message_text = update.message.text
        #message_text = message
        #logging.info(f"Forwarding message from {update.effective_user.id}: {message_text}")  # Log the message being forwarded
        # Forward the message to the other groups
        #await context.bot.send_message(chat_id=FORWARD_GROUP_1, text=message_text)
        #await context.bot.send_message(chat_id=FORWARD_GROUP_2, text=message_text)


async def add_caller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in administrators:  # Check if the user is an administrator
        await update.message.reply_text("You do not have permission to add callers.")
        return  # Exit the function if the user is not an admin

    user_id = context.args[0]  # Get the user ID from the command arguments
    if user_id.isdigit():  # Check if the user ID is a valid number
        user_id = int(user_id)  # Convert to integer
        if user_id not in list_of_eligible_senders:
            list_of_eligible_senders.append(user_id)  # Add the user ID to the list
            await update.message.reply_text(f"User ID {user_id} added to eligible senders.")
        else:
            await update.message.reply_text(f"User ID {user_id} is already in the list.")
    else:
        logging.info(user_id)
        await update.message.reply_text("Please provide a valid user ID.")

async def remove_caller(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in administrators:  # Check if the user is an administrator
        await update.message.reply_text("You do not have permission to add callers.")
        return  # Exit the function if the user is not an admin

    user_id = context.args[0]  # Get the user ID from the command arguments
    if user_id.isdigit():  # Check if the user ID is a valid number
        user_id = int(user_id)  # Convert to integer
        if user_id in list_of_eligible_senders:
            list_of_eligible_senders.remove(user_id)  # Add the user ID to the list
            await update.message.reply_text(f"User ID {user_id} removed from eligible senders.")
        else:
            await update.message.reply_text(f"User ID {user_id} is not in the list.")
    else:
        await update.message.reply_text("Please provide a valid user ID.")


async def add_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in administrators:  # Check if the user is an administrator
        await update.message.reply_text("You do not have permission to add groups.")
        return  # Exit the function if the user is not an admin

    group_id = context.args[0]  # Get the user ID from the command arguments
    if group_id.startswith('-') and group_id[1:].isdigit():  # Check if the user ID is a valid number
        group_id = int(group_id)  # Convert to integer
        if group_id not in list_of_listen_groups:
            list_of_listen_groups.append(group_id)  # Add the user ID to the list
            await update.message.reply_text(f"group ID {group_id} added to eligible groups.")
        else:
            await update.message.reply_text(f"group ID {group_id} is already in the list.")
    else:
        await update.message.reply_text("Please provide a valid group ID.")


async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in administrators:  # Check if the user is an administrator
        await update.message.reply_text("You do not have permission to add groups.")
        return  # Exit the function if the user is not an admin

    group_id = context.args[0]  # Get the user ID from the command arguments
    if group_id.startswith('-') and group_id[1:].isdigit():  # Check if the user ID is a valid number
        group_id = int(group_id)  # Convert to integer
        if group_id in list_of_listen_groups:
            list_of_listen_groups.remove(group_id)  # Add the user ID to the list
            await update.message.reply_text(f"group ID {group_id} removed from eligible groups.")
        else:
            await update.message.reply_text(f"group ID {group_id} is not in the list.")
    else:
        await update.message.reply_text("Please provide a valid group ID.")




async def add_receive_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in administrators:  # Check if the user is an administrator
        await update.message.reply_text("You do not have permission to add groups.")
        return  # Exit the function if the user is not an admin

    group_id = context.args[0]  # Get the user ID from the command arguments
    if group_id.startswith('-') and group_id[1:].isdigit():  # Check if the user ID is a valid number
        group_id = int(group_id)  # Convert to integer
        if group_id not in list_of_receive_groups:
            list_of_receive_groups.append(group_id)  # Add the user ID to the list
            await update.message.reply_text(f"group ID {group_id} added to eligible groups.")
        else:
            await update.message.reply_text(f"groupID {group_id} is already in the list.")
    else:
        await update.message.reply_text("Please provide a valid group ID.")


async def remove_receive_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in administrators:  # Check if the user is an administrator
        await update.message.reply_text("You do not have permission to add groups.")
        return  # Exit the function if the user is not an admin

    group_id = context.args[0]  # Get the user ID from the command arguments
    if group_id.startswith('-') and group_id[1:].isdigit():  # Check if the user ID is a valid number
        group_id = int(group_id)  # Convert to integer
        if group_id in list_of_receive_groups:
            list_of_receive_groups.remove(group_id)  # Add the user ID to the list
            await update.message.reply_text(f"group ID {group_id} removed from eligible groups.")
        else:
            await update.message.reply_text(f"group ID {group_id} is not in the list.")
    else:
        await update.message.reply_text("Please provide a valid group ID.")




async def setup_webhook(application: Application, webhook_url: str):
    """Setup webhook for the bot"""
    webhook_path = f"/{BOT_TOKEN}"
    await application.bot.set_webhook(url=webhook_url + webhook_path)
    return webhook_path

async def handle_webhook(request):
    """Handle incoming webhook requests"""
    try:
        update = Update.de_json(await request.json(), application.bot)
        await application.process_update(update)
        return web.Response(status=200)
    except Exception as e:
        logging.error(f"Error processing update: {e}")
        return web.Response(status=500)

async def on_startup(web_app):
    """Setup webhook on startup"""
    global application
    
    try:
        # Initialize the application
        await application.initialize()
        await application.start()
        
        # Use Render URL from environment variable
        webhook_url = "https://callers-bot.onrender.com"
        if not webhook_url:
            logging.error("RENDER_EXTERNAL_URL environment variable not found")
            await application.shutdown()
            sys.exit(1)
            
        logging.info(f"Using Render URL: {webhook_url}")
        
        # Setup webhook
        webhook_path = await setup_webhook(application, webhook_url)
        
        # Add webhook handler
        web_app.router.add_post(webhook_path, handle_webhook)
        
    except Exception as e:
        logging.error(f"Startup failed: {e}")
        await application.shutdown()
        sys.exit(1)

async def on_shutdown(web_app):
    logging.info("yeahhhhh")
    """Cleanup on shutdown"""
    #global application
    #await application.bot.delete_webhook()
    #await application.stop()
    #await application.shutdown()






async def main() -> None:
    global application
    application = Application.builder().token('7944971005:AAFNmeBPLqc0CKwHau95K4ICvtlx2nNzjm8').build()

    # Listen to messages from the specified groups
    application.add_handler(MessageHandler(filters.ChatType.GROUP, forward_message))
    application.add_handler(CommandHandler("add_caller", add_caller))
    application.add_handler(CommandHandler("remove_caller", remove_caller))
    application.add_handler(CommandHandler("add_call_group", add_group))
    application.add_handler(CommandHandler("remove_call_group", remove_group))
    application.add_handler(CommandHandler("add_receive_group", add_receive_group))
    application.add_handler(CommandHandler("remove_receive_group", remove_receive_group))
    


    logging.info("Bot is starting...")  # Log when the bot starts
    # Start the bot
     # Setup web application
    web_app = web.Application()
    web_app.on_startup.append(on_startup)
    web_app.on_shutdown.append(on_shutdown)

    # Start the web server
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8443))
    
    # Start the web server
    # When running on Render, we need to bind to 0.0.0.0 instead of localhost
    host = '0.0.0.0' if os.environ.get("RENDER_EXTERNAL_URL") else 'localhost'
    web.run_app(web_app, host=host, port=port)

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:  # If there is no current event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Check if the loop is already running
    if loop.is_running():
        asyncio.create_task(main())
    else:
        loop.run_until_complete(main())
