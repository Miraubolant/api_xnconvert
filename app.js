// app.js
const express = require('express');
const multer = require('multer');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const port = process.env.PORT || 3000;
const upload = multer({ dest: 'uploads/' });

// Assurez-vous que les dossiers existent
const uploadsDir = path.join(__dirname, 'uploads');
const outputsDir = path.join(__dirname, 'outputs');

if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir);
}

if (!fs.existsSync(outputsDir)) {
  fs.mkdirSync(outputsDir);
}

app.get('/', (req, res) => {
  res.send('API XnConvert est en ligne!');
});

// Route pour convertir une image
app.post('/convert', upload.single('image'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'Aucun fichier n\'a été envoyé' });
  }

  const inputPath = req.file.path;
  const filename = path.parse(req.file.originalname).name;
  const outputPath = path.join(outputsDir, `${filename}_converted.jpg`);
  
  // Options de conversion par défaut selon la configuration demandée
  // Le "center" est déjà inclus dans les options de canvas pour centrer l'image
  const options = req.body.options || '-ratio -rtype hanning -resize 1000 1500 -canvas 1000 1500 center -bgcolor 255 255 255 -out jpeg -q 80';

  // Commande XnConvert avec Xvfb pour exécuter dans un environnement sans affichage
  const command = `xvfb-run -a xnconvert -input "${inputPath}" -output "${outputPath}" ${options} -overwrite`;

  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Erreur d'exécution: ${error}`);
      return res.status(500).json({ error: 'Erreur lors de la conversion', details: error.message });
    }
    
    // Vérifier si le fichier de sortie existe
    if (!fs.existsSync(outputPath)) {
      return res.status(500).json({ error: 'Le fichier de sortie n\'a pas été créé' });
    }
    
    // Envoi du fichier converti
    res.sendFile(outputPath, (err) => {
      if (err) {
        console.error('Erreur lors de l\'envoi du fichier:', err);
        res.status(500).send('Erreur lors de l\'envoi du fichier');
      }
      
      // Nettoyage des fichiers temporaires
      fs.unlinkSync(inputPath);
      fs.unlinkSync(outputPath);
    });
  });
});

app.listen(port, () => {
  console.log(`API XnConvert démarrée sur le port ${port}`);
});