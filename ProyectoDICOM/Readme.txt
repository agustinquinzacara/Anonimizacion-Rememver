Requisitos
Sistema
Windows 10/11
WSL2
Ubuntu 24.04.4 LTS
Python (Windows)
Python (Windows)
Instalar desde:

https://www.python.org/downloads/

Versión requerida:

Python 3.13.13

Durante instalación:

☑ Add Python to PATH

Verificar Python

En CMD o PowerShell:

py --version

o

python --version
Instalar dependencias Python

En CMD o PowerShell:

py -m pip install pydicom nibabel numpy

o

python -m pip install pydicom nibabel numpy
Instalación WSL
Instalar WSL

En PowerShell (Administrador):

wsl --install

Reiniciar.

Instalar Ubuntu

Desde Microsoft Store:

Ubuntu 24.04 LTS
Verificar en Ubuntu (WSL)

Abrir Ubuntu terminal:

lsb_release -a

Debe mostrar:

Description: Ubuntu 24.04.4 LTS
Instalación automática (RECOMENDADO)
IMPORTANTE: rutas en WSL

Si el proyecto está en Windows:

Ejemplo:

C:\Users\TU_USUARIO\Desktop\ProyectoDICOM

En WSL será:

/mnt/c/Users/TU_USUARIO/Desktop/ProyectoDICOM
Ejecutar script

Colocar install.sh dentro del proyecto.

Luego en Ubuntu (WSL):

cd /mnt/c/Users/TU_USUARIO/Desktop/ProyectoDICOM

Convertir formato (si es necesario):

dos2unix install.sh

Si no tienes:

sudo apt install dos2unix
dos2unix install.sh

Dar permisos:

chmod +x install.sh

Ejecutar:

./install.sh
Qué instala el script
dcm2niix
plastimatch
pigz
FSL
Python tools base
🔥 INSTALACIÓN PYDEFACE (IMPORTANTE)

⚠️ Después del install.sh

En Ubuntu (WSL):

pydeface --help
❓ Si funciona

✔ No hacer nada más
✔ Continuar pipeline

❌ Si NO funciona

Ejecutar:

pip install setuptools --break-system-packages
pip install pydeface --break-system-packages
🧪 Verificación
pydeface --help
⚠️ Error común

Si aparece:

ModuleNotFoundError: No module named 'pkg_resources'

Arreglar con:

pip install setuptools --break-system-packages
Instalación manual (alternativa)

Si NO usas install.sh:

En Ubuntu (WSL):

sudo apt update
sudo apt install -y \
    dcm2niix \
    plastimatch \
    pigz \
    python3-pip \
    git
Instalar FSL

En Ubuntu:

wget https://fsl.fmrib.ox.ac.uk/fsldownloads/fslinstaller.py
python3 fslinstaller.py

Luego:

echo 'export FSLDIR=/usr/local/fsl' >> ~/.bashrc
echo 'source $FSLDIR/etc/fslconf/fsl.sh' >> ~/.bashrc
echo 'export PATH=$FSLDIR/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
Verificación del entorno

Crear archivo:

nano check_env.sh

Contenido:

#!/bin/bash

echo "===== CHECK ENTORNO ====="

echo "Python Windows:"
cmd.exe /c "py --version"

echo ""
echo "Ubuntu:"
lsb_release -a

echo ""
echo "dcm2niix:"
which dcm2niix

echo ""
echo "plastimatch:"
which plastimatch

echo ""
echo "FSL:"
which fslreorient2std

echo ""
echo "pydeface:"
which pydeface

echo ""
echo "===== FIN ====="

Ejecutar:

chmod +x check_env.sh
./check_env.sh
Uso del pipeline

En CMD o PowerShell (Windows):

py main.py

o

python main.py
Estructura del proyecto
ProyectoDICOM/
│
├── main.py
├── install.sh
│
├── core/
│   ├── headers_core.py
│   ├── nifti.py
│   ├── deface2.py
│   ├── nifti_to_dicom_plastimatch.py
│   ├── fix_dicom_metadata.py
│   ├── fix_nifti_dtype.py
│
└── check_env.sh
