#!/bin/bash

echo "======================================"
echo "🧠 Instalador Pipeline Neuroimagen"
echo "======================================"

# =========================
# UPDATE
# =========================
echo "🔄 Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# =========================
# DEPENDENCIAS
# =========================
echo "📦 Instalando dependencias..."

sudo apt install -y \
    python3 \
    python3-pip \
    dcm2niix \
    plastimatch \
    pigz \
    wget

# =========================
# FSL INSTALL
# =========================
echo "🧠 Instalando FSL..."

cd ~
wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py

python3 fslinstaller.py

# =========================
# CONFIG FSL
# =========================
echo "⚙️ Configurando FSL..."

echo 'export FSLDIR=/usr/local/fsl' >> ~/.bashrc
echo 'source $FSLDIR/etc/fslconf/fsl.sh' >> ~/.bashrc
echo 'export PATH=$FSLDIR/bin:$PATH' >> ~/.bashrc

source ~/.bashrc

# =========================
# PYTHON LIBS
# =========================
echo "🐍 Instalando librerías Python..."

pip3 install --user \
    pydeface \
    nibabel \
    numpy \
    pydicom

# =========================
# CHECK
# =========================
echo "🔍 Verificando instalación..."

echo "dcm2niix:"
which dcm2niix

echo "plastimatch:"
which plastimatch

echo "FSL:"
which fslreorient2std

echo "pydeface:"
which pydeface

echo "======================================"
echo "✅ INSTALACIÓN COMPLETA"
echo "======================================"