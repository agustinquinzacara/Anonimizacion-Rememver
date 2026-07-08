import pydicom
from tkinter import Tk, filedialog
import os

root = Tk()
root.withdraw()

# Seleccionar carpeta
carpeta = filedialog.askdirectory(title="Selecciona la carpeta con los DICOM")

if not carpeta:
    print("No se seleccionó ninguna carpeta.")
    exit()

# Buscar el primer archivo de la carpeta
archivo_dicom = None

for archivo in os.listdir(carpeta):
    ruta = os.path.join(carpeta, archivo)
    if os.path.isfile(ruta):
        try:
            pydicom.dcmread(ruta, stop_before_pixels=True)
            archivo_dicom = ruta
            break
        except:
            pass

if archivo_dicom is None:
    print("No se encontraron archivos DICOM válidos.")
    exit()

# Leer y guardar headers
ds = pydicom.dcmread(archivo_dicom)

archivo_salida = os.path.join(carpeta, "headers_dicom.txt")

with open(archivo_salida, "w", encoding="utf-8") as f:
    f.write(f"Archivo analizado: {archivo_dicom}\n")
    f.write("=" * 80 + "\n\n")
    f.write(str(ds))

print(f"Headers guardados en: {archivo_salida}")
os.startfile(archivo_salida)