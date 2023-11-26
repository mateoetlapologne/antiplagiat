import os
import requests
from googleapiclient.discovery import build

# Remplacez 'YOUR_API_KEY' par votre propre clé API
API_KEY = ''

# Remplacez 'CHANNEL_ID' par l'ID de la chaîne YouTube
CHANNEL_ID = ''  # 

# Créez un service YouTube Data API
youtube = build('youtube', 'v3', developerKey=API_KEY)

# Obtenez les informations de la chaîne
channel_info = youtube.channels().list(part='snippet', id=CHANNEL_ID).execute()
channel_name = channel_info['items'][0]['snippet']['title']

# Fonction pour nettoyer le nom du répertoire
def clean_directory_name(name):
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', '\n', '\r', '\t']
    for char in illegal_chars:
        name = name.replace(char, '')
    name = name.replace(' ', '_')  # Remplacez les espaces par des underscores
    name = name.replace('&', 'and')  # Remplacez le caractère '&' par 'and'
    return name[:50]  # Limitez la longueur à 50 caractères

# Créez un répertoire pour la chaîne
channel_directory = f'./{clean_directory_name(channel_name)}'
if not os.path.exists(channel_directory):
    os.makedirs(channel_directory)

# Récupérez la liste des vidéos de la chaîne
request = youtube.search().list(
    part='snippet',
    channelId=CHANNEL_ID,
    maxResults=50  # Augmentez si nécessaire
)

videos = []

while request:
    response = request.execute()
    videos.extend(response['items'])
    request = youtube.search().list_next(request, response)

# Créez le répertoire 'videos' s'il n'existe pas
videos_directory = os.path.join(channel_directory, 'videos')
if not os.path.exists(videos_directory):
    os.makedirs(videos_directory)

# Créez le répertoire 'shorts' s'il n'existe pas
shorts_directory = os.path.join(channel_directory, 'shorts')
if not os.path.exists(shorts_directory):
    os.makedirs(shorts_directory)

# Téléchargez les vidéos et enregistrez les liens
for video in videos:
    video_title = clean_directory_name(video['snippet']['title'])

    # Vérifiez si la vidéo est un short (en fonction du titre)
    is_short = "#Shorts" in video_title

    # Nettoyez le nom du répertoire
    video_directory_name = clean_directory_name(video_title)

    # Créez un répertoire pour chaque vidéo/short
    video_directory = os.path.join(shorts_directory if is_short else videos_directory, video_directory_name)
    if not os.path.exists(video_directory):
        os.makedirs(video_directory)

    # Enregistrez le lien de la vidéo dans un fichier texte
    video_id = video['id'].get('videoId', '')  # Utilisation de 'get' pour gérer les cas où il n'y a pas d'ID de vidéo
    video_url = f'https://www.youtube.com/watch?v={video_id}'

    video_url_file_path = os.path.join(video_directory, 'video_url.txt')
    with open(video_url_file_path, 'w') as url_file:
        url_file.write(video_url)

    # Téléchargez la miniature en résolution standard (SD)
    thumbnail_url = video['snippet']['thumbnails']['standard']['url'] if 'standard' in video['snippet']['thumbnails'] else video['snippet']['thumbnails']['high']['url']
    thumbnail_data = requests.get(thumbnail_url).content

    thumbnail_file_path = os.path.join(video_directory, 'thumbnail.jpg')
    with open(thumbnail_file_path, 'wb') as thumbnail_file:
        thumbnail_file.write(thumbnail_data)

    print(f"Enregistrement de la vidéo/short : {video_title}")

print("Terminé !")
