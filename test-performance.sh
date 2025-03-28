#!/bin/bash
# Script pour tester les performances de différentes méthodes de traitement d'images

# Configuration
API_URL="https://xnconvert.miraubolant.com"
IMAGE_PATH="C:\Users\victo\Pictures\Vetement\product_image_26.jpg"
WIDTH=800
HEIGHT=600
FORMAT="jpg"
REPEAT=5  # Nombre de tests pour chaque outil

# Outils à tester
TOOLS=("imagemagick" "graphicsmagick" "ffmpeg" "vips" "pillow" "nconvert" "opencv" "imageio" "gimp" "skimage" "pyvips")

# Créer le dossier de résultats
mkdir -p test_results

echo "=== Test de performance des outils de traitement d'images ==="
echo "Date: $(date)"
echo "Image: $IMAGE_PATH"
echo "Dimensions: ${WIDTH}x${HEIGHT}"
echo "Format de sortie: $FORMAT"
echo "Répétitions: $REPEAT"
echo

# Tableaux pour stocker les résultats
declare -A TIMES
declare -A SIZES

for TOOL in "${TOOLS[@]}"; do
    echo "Testing $TOOL..."
    TOTAL_TIME=0
    
    for (( i=1; i<=$REPEAT; i++ )); do
        echo "  Run $i..."
        OUTPUT_FILE="test_results/${TOOL}_${i}.${FORMAT}"
        
        # Mesurer le temps d'exécution
        START_TIME=$(date +%s.%N)
        curl -s -X POST -F "image=@$IMAGE_PATH" -F "width=$WIDTH" -F "height=$HEIGHT" -F "format=$FORMAT" "$API_URL/process/$TOOL" -o "$OUTPUT_FILE"
        END_TIME=$(date +%s.%N)
        
        # Calculer le temps écoulé
        ELAPSED=$(echo "$END_TIME - $START_TIME" | bc)
        TOTAL_TIME=$(echo "$TOTAL_TIME + $ELAPSED" | bc)
        
        # Obtenir la taille du fichier
        if [ $i -eq 1 ]; then
            SIZES[$TOOL]=$(du -h "$OUTPUT_FILE" | cut -f1)
        fi
    done
    
    # Calculer la moyenne
    AVG_TIME=$(echo "scale=3; $TOTAL_TIME / $REPEAT" | bc)
    TIMES[$TOOL]=$AVG_TIME
    
    echo "  Temps moyen: ${TIMES[$TOOL]} secondes"
    echo "  Taille du fichier: ${SIZES[$TOOL]}"
    echo
done

# Afficher le résumé
echo "=== Résumé des performances ==="
echo "Outil | Temps moyen (s) | Taille du fichier"
echo "-----|-----------------|----------------"
for TOOL in "${TOOLS[@]}"; do
    printf "%-15s | %-15s | %-15s\n" "$TOOL" "${TIMES[$TOOL]}" "${SIZES[$TOOL]}"
done

echo
echo "Tous les fichiers de sortie sont dans le dossier 'test_results'"