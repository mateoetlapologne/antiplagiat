import os
import re
import requests
from googleapiclient.discovery import build
from googletrans import Translator

# Remplacez 'YOUR_API_KEY' par votre propre clé API
API_KEY = 'AIzaSyBDNanaodW4Snwn5ZBC5r_NUurYuCvUl0k'

# Remplacez 'CHANNEL_ID' par l'ID de la chaîne YouTube
CHANNEL_ID = 'UCTs3XgmNa0MaNBSc0kBa7QQ'  # Par exemple, 'UC_x5XG1OV2P6uZZ5FSM9Ttw'

# Créez un service YouTube Data API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Importez le module Translator de googletrans
from googletrans import Translator

# Fonction pour nettoyer le nom du répertoire
def clean_directory_name(name):
    # Ne gardez que les lettres et chiffres
    name = re.sub(r'[^a-zA-Z0-9]', '', name)

    # Limitez la longueur à 50 caractères
    return name[:50]

# Créez un répertoire pour la chaîne
channel_info = youtube.channels().list(part='snippet', id=CHANNEL_ID).execute()
channel_name = channel_info['items'][0]['snippet']['title']
channel_directory = f'./{clean_directory_name(channel_name)}'

if not os.path.exists(channel_directory):
    os.makedirs(channel_directory)

# Récupérez la liste des vidéos de la chaîne
request = youtube.search().list(
    part='snippet',
    channelId=CHANNEL_ID,
    maxResults=50,
    type='video'
)

videos = []

while request:
    response = request.execute()
    videos.extend(response['items'])
    request = youtube.search().list_next(request, response)

# Téléchargez les vidéos et enregistrez les liens
for video in videos:
    video_id = video['id']['videoId']

    # Obtenez les détails de la vidéo pour récupérer la durée
    video_details = youtube.videos().list(part='contentDetails', id=video_id).execute()
    video_duration = video_details['items'][0]['contentDetails']['duration']

    # Vérifiez si la vidéo est de plus de 2 minutes
    is_long_duration = int(video_duration.replace("PT", "").replace("M", "").split("S")[0]) > 120

    if is_long_duration:
        # Nettoyez le nom du répertoire
        video_title = clean_directory_name(video['snippet']['title'])
        video_directory_name = clean_directory_name(video_title)[:30]  # Limitez la longueur à 30 caractères

        # Créez un répertoire pour chaque vidéo dans le dossier du nom du youtubeur
        video_directory = os.path.join(channel_directory, video_directory_name)

        # Assurez-vous que le répertoire existe en le créant récursivement
        os.makedirs(video_directory, exist_ok=True)

        # Enregistrez le nom original de la vidéo dans le fichier texte et traduisez-le en anglais
        original_video_name = video['snippet']['title']
        translator = Translator()
        translated_title = translator.translate(original_video_name, dest='en').text

        video_url_file_path = os.path.join(video_directory, 'video_url.txt')
        with open(video_url_file_path, 'w', encoding='utf-8') as url_file:
            url_file.write(f"Nom original de la vidéo (FR) : {original_video_name}\n")
            url_file.write(f"Nom original de la vidéo (EN) : {translated_title}\n")
            url_file.write(f"URL de la vidéo : https://www.youtube.com/watch?v={video_id}")

        # Téléchargez la miniature en résolution standard (SD)
        thumbnail_url = video['snippet']['thumbnails']['standard']['url'] if 'standard' in video['snippet']['thumbnails'] else video['snippet']['thumbnails']['high']['url']
        thumbnail_data = requests.get(thumbnail_url).content

        thumbnail_file_path = os.path.join(video_directory, 'thumbnail.jpg')
        with open(thumbnail_file_path, 'wb') as thumbnail_file:
            thumbnail_file.write(thumbnail_data)

        print(f"Enregistrement de la vidéo : {video_title}")

        # Recherchez les vidéos associées au titre traduit en anglais
        related_videos_request = youtube.search().list(
            part='snippet',
            q=translated_title,
            type='video',
            maxResults=5,
            order='viewCount'
        )

        related_videos_response = related_videos_request.execute()

        # Créez un répertoire pour les miniatures traduites
        minia_traduite_directory = os.path.join(video_directory, 'minia_traduite')
        os.makedirs(minia_traduite_directory, exist_ok=True)

        # Enregistrez les liens des 5 vidéos les plus populaires associées au titre traduit
        for related_video in related_videos_response['items']:
            related_video_id = related_video['id']['videoId']
            related_video_thumbnail_url = related_video['snippet']['thumbnails']['medium']['url']

            related_video_thumbnail_data = requests.get(related_video_thumbnail_url).content

            # Enregistrez la miniature dans le répertoire minia_traduite
            related_video_thumbnail_path = os.path.join(minia_traduite_directory, f"{related_video_id}_thumbnail.jpg")
            with open(related_video_thumbnail_path, 'wb') as related_video_thumbnail_file:
                related_video_thumbnail_file.write(related_video_thumbnail_data)

            print(f"Enregistrement de la miniature associée : {related_video_id}")

print("Terminé !")
