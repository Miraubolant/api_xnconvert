import os

def generate_curl_commands(image_path, width, height, format="jpg", api_base_url="https://xnconvert.miraubolant.com", output_dir=None):
    """
    Génère les commandes cURL pour chaque outil de traitement d'image
    et les écrit dans un fichier texte 'curl.txt'.
    
    Args:
        image_path (str): Chemin vers l'image à traiter
        width (int): Largeur cible de l'image
        height (int): Hauteur cible de l'image
        format (str, optional): Format de sortie. Par défaut "jpg".
        api_base_url (str, optional): URL de base de l'API. Par défaut "https://xnconvert.miraubolant.com".
        output_dir (str, optional): Dossier de sortie pour les images traitées. Par défaut, utilise le bureau.
    """
    # Normaliser le chemin de l'image (remplacer / par \\ pour Windows)
    image_path = image_path.replace('/', '\\')
    
    # Si aucun dossier de sortie n'est spécifié, utiliser le bureau
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    
    # Liste des outils disponibles
    tools = [
        "imagemagick", 
        "graphicsmagick", 
        "ffmpeg", 
        "vips", 
        "pillow", 
        "nconvert", 
        "opencv", 
        "imageio", 
        "gimp", 
        "skimage", 
        "pyvips"
    ]
    
    # Préparer les commandes cURL
    curl_commands = []
    
    # Générer une commande cURL pour chaque outil
    for tool in tools:
        output_file = os.path.join(output_dir, f"{tool}_result.{format}")
        command = (
            f'curl -X POST '
            f'-F "image=@{image_path}" '
            f'-F "width={width}" '
            f'-F "height={height}" '
            f'-F "format={format}" '
            f'{api_base_url}/process/{tool} '
            f'-o {output_file}'
        )
        curl_commands.append(command)
    
    # Ajouter les commandes d'utilitaire
    curl_commands.append(f'curl {api_base_url}/health')
    curl_commands.append(f'curl -X POST {api_base_url}/cleanup')
    
    # Écrire les commandes dans un fichier
    with open('curl.txt', 'w') as f:
        f.write('\n\n'.join(curl_commands))
    
    print(f"Les commandes cURL ont été générées dans le fichier 'curl.txt'")
    print(f"Nombre de commandes : {len(curl_commands)}")
    return curl_commands

if __name__ == "__main__":
    # Exemple d'utilisation interactif
    print("Générateur de commandes cURL pour l'API de traitement d'images")
    print("------------------------------------------------------------")
    
    image_path = input("Chemin de l'image (ex: C:\\Utilisateurs\\nom\\Images\\photo.jpg): ")
    width = int(input("Largeur cible (pixels): "))
    height = int(input("Hauteur cible (pixels): "))
    format = input("Format de sortie [jpg]: ") or "jpg"
    
    # Pour personnaliser l'URL de l'API et le dossier de sortie (optionnel)
    custom_api = input("URL de l'API [https://xnconvert.miraubolant.com]: ") or "https://xnconvert.miraubolant.com"
    output_dir = input("Dossier de sortie [Bureau]: ") or None
    
    # Générer les commandes cURL
    generate_curl_commands(image_path, width, height, format, custom_api, output_dir)