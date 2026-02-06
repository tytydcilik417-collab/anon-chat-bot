import telebot
import os
from telebot import types

# Mengambil token dari Environment Variable
# Di lokal/server, pastikan kamu sudah set variabel bernama 'BOT_TOKEN'
API_TOKEN = os.getenv('BOT_TOKEN')

if not API_TOKEN:
    exit("Error: BOT_TOKEN tidak ditemukan di environment variables!")

bot = telebot.TeleBot(API_TOKEN)

# --- DATABASE SEDERHANA ---
waiting_room = []
active_chats = {}

# --- FUNGSI UI ---
def main_menu_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔍 Cari Partner", callback_data="find"))
    return markup

def stop_chat_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Berhenti / Next", callback_data="stop"))
    return markup

# --- LOGIKA BOT ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "👋 Selamat datang di Anon Chat!\nKlik tombol di bawah untuk mulai.", 
        reply_markup=main_menu_markup()
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.message.chat.id
    if call.data == "find":
        if user_id not in waiting_room and user_id not in active_chats.values():
            waiting_room.append(user_id)
            bot.edit_message_text("🔎 Mencari partner...", user_id, call.message.message_id)
            
            if len(waiting_room) >= 2:
                u1 = waiting_room.pop(0)
                u2 = waiting_room.pop(0)
                active_chats[u1], active_chats[u2] = u2, u1
                
                bot.send_message(u1, "✅ Terhubung!", reply_markup=stop_chat_markup())
                bot.send_message(u2, "✅ Terhubung!", reply_markup=stop_chat_markup())
        else:
            bot.answer_callback_query(call.id, "Kamu sudah dalam antrean atau chat!")

    elif call.data == "stop":
        partner_id = active_chats.pop(user_id, None)
        if partner_id:
            active_chats.pop(partner_id, None)
            bot.send_message(user_id, "Chat berakhir.", reply_markup=main_menu_markup())
            bot.send_message(partner_id, "Partner memutus chat.", reply_markup=main_menu_markup())
        elif user_id in waiting_room:
            waiting_room.remove(user_id)
            bot.edit_message_text("Batal mencari.", user_id, call.message.message_id, reply_markup=main_menu_markup())

@bot.message_handler(content_types=['text', 'photo', 'sticker', 'voice', 'video'])
def relay_message(message):
    partner_id = active_chats.get(message.chat.id)
    if partner_id:
        # Menggunakan copy_message supaya lebih simpel dan support semua tipe media
        bot.copy_message(partner_id, message.chat.id, message.message_id)
    else:
        bot.send_message(message.chat.id, "Kamu belum terhubung. Klik 'Cari Partner'.")

bot.infinity_polling()
