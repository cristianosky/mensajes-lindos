from Frases import frases
from FrasesTarde import frasesTarde
from FrasesNoche import frasesNoche
from datetime import datetime
import random
from twilio.rest import Client
import time

# Tus credenciales de Twilio
account_sid = 'AC1fa1802a549e71e50fa73cc6061dfb1b'
auth_token = '2096226222bc990d30422c526a1bea1c'
client = Client(account_sid, auth_token)

def enviar_mensaje(cuerpo, numero_receptor):
    message = client.messages.create(
        body=cuerpo,
        from_='+17623549703',  # Número de Twilio
        to=numero_receptor       # Número del receptor
    )
    print(f"Mensaje enviado con SID: {message.sid}")

def obtener_frase_morning():
    return random.choice(frases)

def obtener_frase_afternoon():
    return random.choice(frasesTarde)

def obtener_frase_night():
    return random.choice(frasesNoche)

def enviar_mensajes():
    numero_receptor = '+513104403702'  # Número del receptor
    
    # Obtener la hora actual
    ahora = datetime.now()
    hora_actual = ahora.hour
    
    # Determinar el mensaje según la hora
    if 6 <= hora_actual < 12:  # Mañana
        cuerpo = obtener_frase_morning()
    elif 12 <= hora_actual < 18:  # Tarde
        cuerpo = obtener_frase_afternoon()
    elif 18 <= hora_actual < 24:  # Noche
        cuerpo = obtener_frase_night()
    else:  # De madrugada (0-5)
        cuerpo = obtener_frase_night()
    
    enviar_mensaje(cuerpo, numero_receptor)

# Llamar a la función para enviar el mensaje en el momento adecuado
enviar_mensajes()
