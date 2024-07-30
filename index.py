import telebot
from datetime import datetime
import random
import time
import threading
import mysql.connector

# Importa tus frases motivadoras
from Frases import frases
from FrasesTarde import frasesTarde
from FrasesNoche import frasesNoche

# Conexión con nuestro BOT
TOKEN = '7241414439:AAHTOJU7DAdPrvctyUi7dMT5V12qGR7Aa-Q'
bot = telebot.TeleBot(TOKEN)

# Credenciales de la base de datos MySQL
DB_HOST = "bczsetqiyg8ogjwsob7o-mysql.services.clever-cloud.com"
DB_PORT = 3306
DB_USER = "uj4m6mgrf8jfp0ua"
DB_PASSWORD = "Hea0AnzvUs7cR1DzH6yS"  # Reemplaza con tu contraseña real
DB_NAME = "bczsetqiyg8ogjwsob7o"

# Variable de control para detener el envío de mensajes
enviando_mensajes = False


def obtener_conexion():
    return mysql.connector.connect(host=DB_HOST,
                                   port=DB_PORT,
                                   user=DB_USER,
                                   password=DB_PASSWORD,
                                   database=DB_NAME)


def init_db():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (chat_id BIGINT PRIMARY KEY)''')
    conn.commit()
    cursor.close()
    conn.close()


def add_user(chat_id):
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("INSERT IGNORE INTO users (chat_id) VALUES (%s)",
                   (chat_id, ))
    conn.commit()
    cursor.close()
    conn.close()


def get_all_users():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return [user[0] for user in users]


def establecer_comandos():
    comandos = [
        telebot.types.BotCommand(
            "start", "Inicia el bot y empieza a enviar frases motivadoras"),
        telebot.types.BotCommand("stop",
                                 "Detiene el envío de frases motivadoras"),
        telebot.types.BotCommand("restart",
                                 "Reinicia el envío de frases motivadoras"),
        telebot.types.BotCommand("motivar",
                                 "Envía una frase motivadora al instante"),
        telebot.types.BotCommand("help", "Muestra la ayuda"),
        telebot.types.BotCommand(
            "broadcast", "Envía un mensaje de difusión a todos los usuarios")
    ]
    bot.set_my_commands(comandos)


def obtener_frase_morning():
    return random.choice(frases)


def obtener_frase_afternoon():
    return random.choice(frasesTarde)


def obtener_frase_night():
    return random.choice(frasesNoche)


def obtener_frase():
    hora_actual = datetime.now().hour

    if 6 <= hora_actual < 12:  # Mañana
        return obtener_frase_morning()
    elif 12 <= hora_actual < 18:  # Tarde
        return obtener_frase_afternoon()
    elif 18 <= hora_actual < 24:  # Noche
        return obtener_frase_night()
    else:  # De madrugada (0-5)
        return obtener_frase_night()


def enviar_frases_periodicamente(chat_id):
    global enviando_mensajes
    while enviando_mensajes:
        bot.send_message(chat_id, obtener_frase())
        for _ in range(60):
            if not enviando_mensajes:
                break
            time.sleep(1)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    global enviando_mensajes
    enviando_mensajes = True
    add_user(message.chat.id)
    bot.reply_to(message,
                 '¡Bienvenido! Te enviaré frases motivadoras cada minuto.')
    thread = threading.Thread(target=enviar_frases_periodicamente,
                              args=(message.chat.id, ))
    thread.start()


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(
        message,
        'Puedes interactuar conmigo usando comandos. Por ahora, solo respondo a /start, /help, /motivar, /stop y /restart.'
    )


@bot.message_handler(commands=['stop'])
def stop_bot(message):
    global enviando_mensajes
    enviando_mensajes = False
    bot.reply_to(
        message,
        'El envío de mensajes ha sido detenido. Usa /start para reiniciar.')


@bot.message_handler(commands=['restart'])
def restart_messages(message):
    global enviando_mensajes
    enviando_mensajes = False
    bot.reply_to(message, 'Reiniciando el envío de mensajes...')
    time.sleep(2)  # Espera 2 segundos antes de reiniciar
    enviando_mensajes = True
    bot.reply_to(
        message,
        'Envío de mensajes reiniciado. Enviando frases motivadoras cada minuto.'
    )
    thread = threading.Thread(target=enviar_frases_periodicamente,
                              args=(message.chat.id, ))
    thread.start()


@bot.message_handler(commands=['motivar'])
def enviar_mensaje_motivador(message):
    bot.reply_to(message, obtener_frase())


@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.chat.id == "777098427":  # Reemplaza con tu chat ID de administrador
        users = get_all_users()
        for user in users:
            bot.send_message(user, 'Frases actualizadas por favor ejecutar el comando de /start')


if __name__ == "__main__":
    init_db()
    establecer_comandos()
    bot.polling(none_stop=True)
