import os
import re
import requests
from googleapiclient.discovery import build

# Remplacez 'YOUR_API_KEY' par votre propre clé API
API_KEY = 'API_KEY'

# Remplacez 'CHANNEL_ID' par l'ID de la chaîne YouTube
CHANNEL_ID = 'CHANNEL_ID'  # Par exemple, 'UC_x5XG1OV2P6uZZ5FSM9Ttw'

# Créez un service YouTube Data API
youtube = build('youtube', 'v3', developerKey=API_KEY)

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

        # Enregistrez le nom original de la vidéo dans le fichier texte
        original_video_name = video['snippet']['title']
        video_url_file_path = os.path.join(video_directory, 'video_url.txt')

        with open(video_url_file_path, 'w', encoding='utf-8') as url_file:
            url_file.write(f"Nom original de la vidéo : {original_video_name}\n")
            url_file.write(f"URL de la vidéo : https://www.youtube.com/watch?v={video_id}")

        # Téléchargez la miniature en résolution standard (SD)
        thumbnail_url = video['snippet']['thumbnails']['standard']['url'] if 'standard' in video['snippet']['thumbnails'] else video['snippet']['thumbnails']['high']['url']
        thumbnail_data = requests.get(thumbnail_url).content

        thumbnail_file_path = os.path.join(video_directory, 'thumbnail.jpg')
        with open(thumbnail_file_path, 'wb') as thumbnail_file:
            thumbnail_file.write(thumbnail_data)

        print(f"Enregistrement de la vidéo : {video_title}")

print("Terminé !")
