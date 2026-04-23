Pipeline DICOM → NIfTI → Deface → DICOM

Pipeline automatizado para:

Anonimización de DICOM
Conversión a NIfTI
Defacing (remoción de rostro)
Reconversión a DICOM
Preservación de metadata relevante
Versiones utilizadas
Python: 3.13.13 (Windows)
Ubuntu (WSL): 24.04.4 LTS

Estas versiones fueron probadas y son las recomendadas para evitar incompatibilidades.

Estructura del proyecto
ProyectoDICOM/
│
├── main.py
├── check_env.py
├── install.sh
│
└─ core/
   ├── headers_core.py
   ├── nifti.py
   ├── deface2.py
   ├── nifti_to_dicom_plastimatch.py
   ├── fix_dicom_metadata.py
   └── fix_nifti_dtype.py

Entorno	Uso
PowerShell	instalar WSL
Ubuntu (WSL)	instalar herramientas
CMD / PowerShell	ejecutar pipeline
1. Instalar Python (Windows)

Ejecutar en Windows.

Descargar desde:
https://www.python.org/downloads/

Durante la instalación:

Activar "Add Python to PATH"

Verificar:

python --version

Debe mostrar:

Python 3.13.13
2. Instalar WSL + Ubuntu

Ejecutar en PowerShell (como administrador):

wsl --install

Reiniciar el equipo.

Abrir Ubuntu desde el menú inicio.

Configurar usuario:

username + password

Verificar versión:

wsl -l -v
3. Instalación automática (recomendada)

Ejecutar en Ubuntu (WSL).

Ir a la carpeta del proyecto:

cd /mnt/c/Users/TU_USUARIO/Desktop/ProyectoDICOM

Dar permisos:

chmod +x install.sh

Ejecutar:

./install.sh
Qué instala el script
dcm2niix
plastimatch
FSL
pydeface
nibabel
numpy
pydicom
4. Verificar entorno

Ejecutar en Windows:

python check_env.py

Debe indicar que todas las herramientas están disponibles.

5. Ejecutar pipeline

Ejecutar en Windows:

cd C:\Users\TU_USUARIO\Desktop\ProyectoDICOM
python main.py
