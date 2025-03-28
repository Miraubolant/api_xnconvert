import os

def generate_curl_commands(image_path, width=1000, height=1500, format="jpg", api_base_url="https://xnconvert.miraubolant.com", output_dir=None, 
                          resize_mode="fit", keep_ratio=True, resampling="hanning", crop_position="center", bg_color="white", bg_alpha=255):
    """
    Génère les commandes cURL pour chaque outil de traitement d'image
    et les écrit dans un fichier texte 'curl.txt'.
    
    Args:
        image_path (str): Chemin vers l'image à traiter
        width (int): Largeur cible de l'image (défaut: 1000)
        height (int): Hauteur cible de l'image (défaut: 1500)
        format (str): Format de sortie (défaut: "jpg")
        api_base_url (str): URL de base de l'API (défaut: "https://xnconvert.miraubolant.com")
        output_dir (str): Dossier de sortie pour les images traitées (défaut: Bureau)
        resize_mode (str): Mode de redimensionnement - "fit", "fill", "stretch" (défaut: "fit")
        keep_ratio (bool): Conserver le ratio d'aspect (défaut: True)
        resampling (str): Méthode de ré-échantillonnage (défaut: "hanning")
        crop_position (str): Position du recadrage (défaut: "center")
        bg_color (str): Couleur de fond (défaut: "white")
        bg_alpha (int): Alpha pour la couleur de fond (défaut: 255)
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
    
    # Convertir keep_ratio en string pour la requête
    keep_ratio_str = "true" if keep_ratio else "false"
    
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
            f'-F "resize_mode={resize_mode}" '
            f'-F "keep_ratio={keep_ratio_str}" '
            f'-F "resampling={resampling}" '
            f'-F "crop_position={crop_position}" '
            f'-F "bg_color={bg_color}" '
            f'-F "bg_alpha={bg_alpha}" '
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

def create_batch_file(curl_commands, output_file="run_curl_commands.bat"):
    """
    Crée un fichier batch Windows pour exécuter les commandes cURL
    
    Args:
        curl_commands (list): Liste des commandes cURL
        output_file (str): Nom du fichier batch à créer
    """
    with open(output_file, 'w') as f:
        f.write("@echo off\n")
        f.write("echo Exécution des commandes cURL pour le traitement d'images\n")
        f.write("echo ===================================================\n\n")
        
        for i, command in enumerate(curl_commands, 1):
            tool = command.split('/process/')[1].split(' ')[0] if '/process/' in command else "utility"
            f.write(f"echo Traitement {i}/{len(curl_commands)}: {tool}\n")
            f.write(f"{command}\n")
            f.write("echo.\n\n")
        
        f.write("echo Toutes les commandes ont été exécutées.\n")
        f.write("pause\n")
    
    print(f"Fichier batch créé : {output_file}")

if __name__ == "__main__":
    # Exemple d'utilisation interactif
    print("Générateur de commandes cURL pour l'API de traitement d'images")
    print("------------------------------------------------------------")
    
    image_path = input("Chemin de l'image (ex: C:\\Utilisateurs\\nom\\Images\\photo.jpg): ")
    width = input("Largeur cible (pixels) [1000]: ") or "1000"
    height = input("Hauteur cible (pixels) [1500]: ") or "1500"
    format = input("Format de sortie [jpg]: ") or "jpg"
    
    # Pour personnaliser l'URL de l'API et le dossier de sortie (optionnel)
    custom_api = input("URL de l'API [https://xnconvert.miraubolant.com]: ") or "https://xnconvert.miraubolant.com"
    output_dir = input("Dossier de sortie [Bureau]: ") or None
    
    # Options avancées
    print("\nOptions avancées (appuyez sur Entrée pour utiliser les valeurs par défaut):")
    resize_mode = input("Mode de redimensionnement [fit/fill/stretch] [fit]: ") or "fit"
    keep_ratio_input = input("Conserver le ratio [true/false] [true]: ").lower() or "true"
    keep_ratio = keep_ratio_input == "true"
    resampling = input("Méthode de ré-échantillonnage [nearest/bilinear/bicubic/lanczos/hanning] [hanning]: ") or "hanning"
    crop_position = input("Position du recadrage [center/top/bottom/left/right] [center]: ") or "center"
    bg_color = input("Couleur de fond [white]: ") or "white"
    bg_alpha = input("Alpha pour la couleur de fond [255]: ") or "255"
    
    # Conversion des types
    width = int(width)
    height = int(height)
    bg_alpha = int(bg_alpha)
    
    # Générer les commandes cURL
    curl_commands = generate_curl_commands(
        image_path, width, height, format, custom_api, output_dir,
        resize_mode, keep_ratio, resampling, crop_position, bg_color, bg_alpha
    )
    
    # Créer un fichier batch pour exécution facile
    create_batch = input("\nCréer un fichier batch pour exécuter les commandes facilement? [y/n]: ").lower()
    if create_batch == 'y' or create_batch == 'yes':
        create_batch_file(curl_commands)