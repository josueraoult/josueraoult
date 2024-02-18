from flask import Flask, request, jsonify
from pymessenger import Bot
import requests
import openai
import os

# Configurez votre token secret pour la vérification
WEBHOOK_VERIFY_TOKEN = 'TOKEN_web'

# Configurez votre clé d'API pour pymessenger
ACCESS_TOKEN = 'ici le acces token de ton page'  # Remplacez par votre propre token

# Configurez votre clé d'API pour OpenAI GPT-3.5-turbo
OPENAI_API_KEY = 'ici le clé api de openai'  # Remplacez par votre propre clé

# Initialisez le client pymessenger
bot = Bot(ACCESS_TOKEN)

# Configurez la clé d'API OpenAI
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Endpoint pour vérifier le token lors de la configuration du webhook
@app.route('/webhook', methods=['GET'])
def verify_token():
    token_sent = request.args.get("hub.verify_token")
    return verify_fb_token(token_sent)

# Endpoint principal pour recevoir les messages du webhook de Messenger
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get('postback'):
                    # Si l'utilisateur clique sur "Get Started"
                    if messaging_event['postback']['payload'] == 'GET_STARTED_PAYLOAD':
                        sender_id = messaging_event['sender']['id']
                        send_welcome_messages(sender_id)
                elif messaging_event.get('message'):
                    gestionnaire_messages(messaging_event)
    return "OK", 200

def verify_fb_token(token_sent):
    if token_sent == WEBHOOK_VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    else:
        return 'Token non valide'

def envoyer_message_texte(sender_id, message):
    bot.send_text_message(sender_id, message)

def obtenir_reponse_openai(texte_utilisateur):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": texte_utilisateur},
        ]
    )
    return response['choices'][0]['message']['content']

def repondre_message(sender_id, message_text):
    reponse_openai = obtenir_reponse_openai(message_text)
    envoyer_message_texte(sender_id, reponse_openai)

def gestionnaire_messages(message):
    sender_id = message['sender']['id']
    message_text = message['message']['text']
    repondre_message(sender_id, message_text)

def set_get_started_button():
    url = f'https://graph.facebook.com/v12.0/me/messenger_profile?access_token={ACCESS_TOKEN}'
    payload = {
        "get_started": {
            "payload": "GET_STARTED_PAYLOAD"
        }
    }
    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

def send_welcome_messages(user_id):
    envoyer_message_texte(user_id, "Bienvenue, je suis Nakama Bot.")
    envoyer_message_texte(user_id, "Veuillez entrer votre question.")

# Utilisez cette fonction pour définir le bouton "Get Started"
set_get_started_button()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
