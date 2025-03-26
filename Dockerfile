FROM node:18-slim

# Installation de XnConvert et dépendances
RUN apt-get update && apt-get install -y \
    wget \
    libglib2.0-0 \
    libfontconfig1 \
    libx11-6 \
    libxext6 \
    libgl1-mesa-glx \
    libglu1-mesa \
    libc6 \
    xdg-utils \
    unzip \
    libkrb5-3 \
    libk5crypto3 \
    libgssapi-krb5-2 \
    libqt5core5a \
    libqt5gui5 \
    libqt5widgets5 \
    libqt5network5 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-randr0 \
    libxcb-xinerama0 \
    libxcb-shape0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    xvfb \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Téléchargement et installation de XnConvert
WORKDIR /tmp
RUN wget --no-check-certificate https://download.xnview.com/XnConvert-linux-x64.deb
RUN dpkg -i XnConvert-linux-x64.deb || true
RUN apt-get -f install -y
RUN rm XnConvert-linux-x64.deb

# Configuration des variables d'environnement Qt pour utiliser le plugin xcb
ENV QT_QPA_PLATFORM=xcb
ENV DISPLAY=:0
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Création des répertoires nécessaires
RUN mkdir -p uploads outputs
RUN chmod 777 uploads outputs

EXPOSE 3000
CMD ["node", "app.js"]