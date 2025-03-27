# Flask Image Processing API

Cette API permet de tester et comparer différentes méthodes de traitement d'images en ligne de commande à travers une interface REST. Elle est spécialement conçue pour comparer les performances et la qualité entre différentes bibliothèques et outils.

## Fonctionnalités

- Redimensionnement et recadrage centré d'images
- Support pour de multiples outils de traitement d'images
- Format d'entrée : JPEG, PNG, GIF, WebP, BMP, TIFF
- Format de sortie paramétrable

## Outils supportés

1. **ImageMagick** - Outil classique de manipulation d'images
2. **GraphicsMagick** - Fork optimisé d'ImageMagick
3. **FFmpeg** - Outil polyvalent de traitement audio/vidéo/image
4. **VIPS (libvips)** - Traitement d'image avec faible empreinte mémoire
5. **Pillow** - Bibliothèque Python pour le traitement d'images
6. **NConvert** - Outil de ligne de commande de XnView
7. **OpenCV** - Bibliothèque de vision par ordinateur
8. **ImageIO** - Bibliothèque Python pour la lecture/écriture d'images
9. **GIMP** - Programme de manipulation d'images
10. **scikit-image** - Bibliothèque de traitement d'images pour Python
11. **PyVips** - Binding Python pour libvips

## Installation

### Prérequis

- Docker
- Git

### Installation locale

```bash
# Cloner le dépôt
git clone https://github.com/votre-utilisateur/image-processing-api.git
cd image-processing-api

# Construire l'image Docker
docker build -t image-processing-api .

# Lancer le conteneur
docker run -p 5000:5000 image-processing-api
```

## Déploiement avec Coolify

1. Dans Coolify, ajoutez votre dépôt Git
2. Configurez le déploiement en sélectionnant l'option Dockerfile
3. Déployez l'application

## Utilisation de l'API

### Points de terminaison

- `GET /health` : Vérification de l'état de l'API
- `POST /process/<tool>` : Traitement d'image avec l'outil spécifié
- `POST /cleanup` : Nettoyage des fichiers temporaires

### Paramètres pour `/process/<tool>`

| Paramètre | Type | Description |
|-----------|------|-------------|
| `image` | File | Fichier image à traiter |
| `width` | Int | Largeur cible en pixels (défaut: 800) |
| `height` | Int | Hauteur cible en pixels (défaut: 600) |
| `format` | String | Format de sortie (défaut: jpg) |

### Exemples d'utilisation

Voir le fichier `examples.sh` pour des exemples complets avec cURL.

Exemple de base :
```bash
curl -X POST -F "image=@mon_image.jpg" -F "width=800" -F "height=600" -F "format=webp" https://votre-api.coolify.app/process/imagemagick -o resultat.webp
```

## Test de performances

Un script est inclus pour tester les performances des différentes méthodes :

```bash
# Modifier les variables dans le script selon vos besoins
bash test-performance.sh
```

Ce script mesure :
- Le temps d'exécution moyen
- La taille des fichiers générés
- Génère des échantillons pour comparaison visuelle

## Structure du projet

```
/
├── app.py                  # Application Flask principale
├── Dockerfile              # Configuration Docker
├── requirements.txt        # Dépendances Python
├── examples.sh             # Exemples d'utilisation avec cURL
└── test-performance.sh     # Script de test de performance
```

## Limitations connues

- GIMP peut être lent car il doit démarrer pour chaque requête
- Certains outils peuvent ne pas supporter tous les formats d'image
- Les performances peuvent varier considérablement selon la configuration serveur

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

## Licence

MIT