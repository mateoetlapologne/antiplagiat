import os
import requests
from googletrans import Translator
from pytube import YouTube, Channel

def get_user_input():
    api_key = input("Veuillez entrer votre clé API YouTube : ")
    channel_id = input("Veuillez entrer l'ID de la chaîne YouTube : ")
    return api_key, channel_id

def get_channel_name(channel_url):
    channel_id = channel_url.split("/c/")[-1]
    return channel_id

def confirm_channel_name(channel_name):
    confirmation = input(f"Le nom de la chaîne est {channel_name}. Est-ce correct? (y/n): ").lower()
    return confirmation == 'y'

def clean_directory_name(name):
    # Supprimer les caractères spéciaux, remplacer les espaces par des underscores
    # et garder uniquement les caractères ASCII
    name = "".join(c if c.isalnum() or c.isspace() else "_" for c in name)
    name = name.replace(" ", "_").lower()
    return name

def translate_title(title):
    translator = Translator()
    translation = translator.translate(title, dest='en')
    return translation.text

def main():
    # Demander à l'utilisateur la clé API et l'ID de la chaîne
    api_key, channel_id = get_user_input()

    # Récupérer le nom de la chaîne à partir de l'ID (cela peut être ajusté en fonction de vos besoins)
    channel_url = f"https://www.youtube.com/c/{channel_id}"
    channel_name = get_channel_name(channel_url)

    # Confirmer le nom de la chaîne avec l'utilisateur
    if not confirm_channel_name(channel_name):
        print("Nom de chaîne incorrect. Script annulé.")
        return

    # Créer un dossier pour la chaîne
    channel_directory = f"./{clean_directory_name(channel_name)}"
    os.makedirs(channel_directory, exist_ok=True)

    # Exécuter le reste du script
    print("Exécution du reste du script...")

    # ... le reste de votre script ici

if __name__ == "__main__":
    main()
