import os
import shutil
import time
import pydicom

from tkinter import Tk, filedialog, simpledialog, Toplevel, Label, Button, StringVar
from tkinter.ttk import Combobox

from core.headers_core import anonymize_subject
from core.nifti import dicom_to_nifti
from core.deface2 import deface_nifti
from core.nifti_to_dicom_plastimatch import nifti_to_dicom_plastimatch
from core.fix_dicom_metadata import fix_metadata
from core.fix_nifti_dtype import fix_dtype
from core.redcap_lookup import (select_redcap_csv, get_patient_id, find_redcap_id)
from core.pending_subjects import move_to_pending
from datetime import datetime
from core.log_generation import (write_log, generate_summary, log_fatal_error)




# =========================
# INTERFAZ
# =========================
def select_root():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return filedialog.askdirectory(title="Selecciona carpeta con sujetos")


# =========================
# SELECCIONAR CENTRO
# =========================
def ask_prefix():

    centros = {

        "Hospital Guillermo Grant Benavente": "HGGB",
        "Hospital Salvador": "HDS",
        "Hospital Clínico San Borja Arriarán": "HCSBA",
        "Hospital San José": "HSJ",
        "Hospital Base Valdivia": "HBV",
        "Hospital Hernán Henriquez Aravena": "HHHA",
        "Otro Centro": "OTR",
        "Pruebas": "TEST"

    }

    root = Tk()
    root.withdraw()

    ventana = Toplevel()
    ventana.title("Seleccionar centro")
    ventana.geometry("500x150")
    ventana.attributes("-topmost", True)

    Label(
        ventana,
        text="Seleccione el centro:",
        font=("Arial", 10, "bold")
    ).pack(pady=10)

    seleccion = StringVar()

    combo = Combobox(
        ventana,
        textvariable=seleccion,
        width=60,
        state="readonly"
    )

    combo["values"] = [
        f"{nombre} ({prefijo})"
        for nombre, prefijo in centros.items()
    ]

    combo.current(0)
    combo.pack(pady=5)

    resultado = {"prefijo": None}

    def aceptar():

        texto = seleccion.get()

        for nombre, prefijo in centros.items():

            if texto.startswith(nombre):

                resultado["prefijo"] = prefijo
                break

        ventana.destroy()

    Button(
        ventana,
        text="Aceptar",
        command=aceptar
    ).pack(pady=15)

    ventana.grab_set()
    ventana.wait_window()

    return resultado["prefijo"]


# =========================
# BÚSQUEDA DE SERIES DICOM
# =========================
def find_dicom_series(root_dir):

    series = []

    for root, _, files in os.walk(root_dir):

        dicom_found = False

        for f in files:

            path = os.path.join(root, f)

            try:
                pydicom.dcmread(path, stop_before_pixels=True)
                dicom_found = True
                break

            except:
                pass

        if dicom_found:
            series.append(root)

    return sorted(series)

# =========================
# CONTAR DICOM
# =========================
def count_dicoms(series_path):

    n = 0

    for root, _, files in os.walk(series_path):

        for f in files:

            path = os.path.join(root, f)

            try:
                pydicom.dcmread(
                    path,
                    stop_before_pixels=True
                )

                n += 1

            except:
                pass

    return n

# =========================
# UTILIDADES
# =========================
def to_wsl(p):
    return p.replace("C:", "/mnt/c").replace("\\", "/")


def safe_rmtree(path):
    """Eliminación robusta de carpetas en Windows"""

    if not os.path.exists(path):
        return

    for i in range(3):

        try:
            shutil.rmtree(path)
            print(f"🗑️ Eliminado: {path}")
            return

        except Exception as e:
            print(f"⚠️ Intento {i+1} falló eliminando {path}: {e}")
            time.sleep(1)

    print(f"❌ No se pudo eliminar: {path}")


# =========================
# DETECCIÓN DE SERIES
# =========================
def is_structural(series_path):

    keywords = [

        # Resonancia magnética T1
        "t1",
        "mprage",
        "spgr",
        "bravo",
        "tfe",
        "t1w",

        # Resonancia magnética T2
        "t2",
        "t2w",
        "flair",
        "space",
        "cube"
    ]

    for root, _, files in os.walk(series_path):

        for f in files:

            path = os.path.join(root, f)

            try:
                ds = pydicom.dcmread(path, stop_before_pixels=True)

                modality = str(ds.get("Modality", "")).upper()

                text = " ".join([
                    str(ds.get("SeriesDescription", "")).lower(),
                    str(ds.get("ProtocolName", "")).lower(),
                    str(ds.get("StudyDescription", "")).lower()
                ])

                # =====================
                # IGNORAR INFORMES SR
                # =====================
                if modality == "SR":
                    continue

                # =====================
                # IGNORAR SERIES AUXILIARES
                # =====================
                exclude_keywords = [
                    "localizer",
                    "scout",
                    "topogram",
                    "topo",
                    "survey",
                    "smartprep",
                    "locator",
                    "pilot",
                    "reformat",
                    "mip",
                    "3plane",
                    "reference",
                    "monitor",
                    "screen save"
                ]

                if any(k in text for k in exclude_keywords):
                    continue

                # =====================
                # TOMOGRAFÍA COMPUTADA
                # =====================

                print(f"\nSerie: {text}")
                print(f"Modalidad: {modality}")

                if modality == "CT":

                    ct_keywords = [
                        "angio",
                        "partes blandas",
                        "retorno",
                        "cortical",
                        "coronal",
                        "axial"
                    ]

                    if any(k in text for k in ct_keywords):
                        return True

                    return True

                # =====================
                # RESONANCIA MAGNÉTICA
                # =====================
                if any(k in text for k in keywords):
                    return True

            except:
                continue

    return False



# =========================
# MAIN
# =========================
if __name__ == "__main__":

    # =========================
    # SELECCIÓN DE CARPETA RAÍZ
    # =========================
    root_dir = select_root()

    if not root_dir:
        exit()

    # =========================
    # INICIALIZACIÓN DE LOGS
    # =========================

    # Fecha de inicio del pipeline
    fecha_inicio = datetime.now()

    # Carpeta donde se almacenarán los logs
    log_dir = os.path.join(
        os.path.dirname(__file__),
        "logs"
    )

    os.makedirs(log_dir, exist_ok=True)

    # Timestamp para nombres únicos
    timestamp = fecha_inicio.strftime(
        "%Y%m%d_%H%M%S"
    )

    # Log completo de ejecución
    log_file = os.path.join(
        log_dir,
        f"pipeline_{timestamp}.log"
    )


    write_log(log_file, "===== INICIO PIPELINE =====")

    write_log(log_file, f"Carpeta raíz: {root_dir}")


    # =========================
    # VARIABLES PARA RESUMEN
    # =========================

    procesados = []
    pendientes = []
    errores = []
    series_procesadas = []
    series_error = []

    # =========================
    # CONFIGURACIÓN DEL ESTUDIO
    # =========================
    prefix = ask_prefix()

    csv_file = select_redcap_csv(root_dir)

    if not csv_file:
        print("❌ No se seleccionó CSV REDCap")
        exit()

    print("\nROOT:", root_dir)

    # =========================
    # BÚSQUEDA DE SUJETOS
    # =========================
    subjects = [
        d for d in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, d))
        and not d.endswith("_processed")
        and d != "anonimizados"
    ]

    # =========================
    # PROCESAMIENTO DE SUJETOS
    # =========================
    for subj in sorted(subjects):

        subj_path = os.path.join(root_dir, subj)

        write_log(log_file, f"===== INICIO SUJETO: {subj} =====")

        # Obtener RUT desde el header DICOM
        rut = get_patient_id(subj_path)

        write_log(log_file, f"RUT encontrado: {rut}")

        if not rut:

            write_log(log_file, f"ERROR: no se encontró PatientID para {subj}")

            errores.append(
                f"{subj} (sin PatientID)"
            )

            continue

        # =========================
        # BÚSQUEDA EN REDCAP
        # =========================
        redcap_id = find_redcap_id(
            csv_file,
            rut
        )

        # sujeto no encontrado
        if redcap_id is None:

            print(
                f"⚠ RUT no encontrado en REDCap: {rut}"
            )

            move_to_pending(
                subj_path,
                root_dir
            )

            pendientes.append(f"{subj} (RUT: {rut})")
            write_log(log_file, f"Sujeto movido a pendientes REDCap: {subj} | RUT: {rut}")

            continue

        # generar identificador final
        patient_name = (
            f"{prefix}-{redcap_id}"
        )

        print(
            f"✔ ID REDCap encontrado: "
            f"{patient_name}"
        )

        print(f"\nSUBJECT: {subj} → {patient_name}")

        # =========================
        # 1. ANONIMIZACIÓN DICOM
        # =========================
        anon_path = os.path.join(root_dir, "anonimizados", patient_name)

        write_log(log_file, "Iniciando anonimización DICOM")

        anonymize_subject(
            subj_path,
            anon_path,
            patient_name
        )

        # =========================
        # 2. PROCESAMIENTO
        # =========================
        output_root = anon_path + "_processed"

        os.makedirs(output_root, exist_ok=True)

        series_list = find_dicom_series(anon_path)

        for in_series in series_list:

            series_name = os.path.basename(in_series)

            write_log(log_file, f"Procesando serie: {series_name}")

            try:
                relative = os.path.relpath(in_series, anon_path)

                out_series = os.path.join(output_root, relative)

                # =====================
                # EVITAR SERIES MUY PEQUEÑAS
                # =====================
                n_dicoms = count_dicoms(in_series)

                if n_dicoms < 5:

                    shutil.copytree(
                        in_series,
                        out_series,
                        dirs_exist_ok=True
                    )

                    print(
                        f"SKIP ({n_dicoms} cortes)"
                    )

                    write_log(
                        log_file,
                        f"Serie omitida (<5 cortes): {series_name}"
                    )

                    continue


                # =====================
                # VALIDAR SI ES ESTRUCTURAL
                # =====================
                if not is_structural(in_series):

                    shutil.copytree(
                        in_series,
                        out_series,
                        dirs_exist_ok=True
                    )

                    write_log(log_file, f"Serie omitida (no estructural): {series_name}")

                    continue

                print(f"PIPELINE ESTRUCTURAL ({series_name})")

                # =====================
                # DIRECTORIO TEMPORAL
                # =====================
                tmp_dir = os.path.join(
                    output_root,
                    "_tmp_nifti"
                )

                os.makedirs(tmp_dir, exist_ok=True)

                # =====================
                # DICOM → NIFTI
                # =====================
                dicom_to_nifti(
                    to_wsl(in_series),
                    to_wsl(tmp_dir)
                )

                nii_files = [
                    os.path.join(tmp_dir, f)
                    for f in os.listdir(tmp_dir)
                    if f.endswith(".nii.gz")
                    and "_defaced" not in f
                ]

                if not nii_files:
                    raise RuntimeError("No se generó NIfTI")

                nii = max(
                    nii_files,
                    key=os.path.getctime
                )

                # =====================
                # CORRECCIÓN DE DTYPE
                # =====================
                #  fix_dtype(nii)

                # =====================
                # DEFACING
                # =====================
                defaced = nii.replace(
                    ".nii.gz",
                    "_defaced.nii.gz"
                )

                deface_nifti(
                    to_wsl(nii),
                    to_wsl(defaced)
                )

                # =====================
                # ELIMINAR NIFTI ORIGINAL
                # =====================
                try:
                    os.remove(nii)

                except:
                    pass

                # =====================
                # NIFTI → DICOM
                # =====================
                nifti_to_dicom_plastimatch(
                    to_wsl(defaced),
                    to_wsl(in_series),
                    to_wsl(out_series)
                )

                # =====================
                # CORRECCIÓN DE METADATOS
                # =====================
                # fix_metadata(in_series, out_series)

                # =====================
                # LIMPIEZA TEMPORAL
                # =====================
                safe_rmtree(tmp_dir)

                write_log(log_file, f"Serie procesada correctamente: {series_name}")

                print("✔ Procesamiento completado")

                series_procesadas.append(f"{patient_name} | {series_name}")

            except Exception as e:

                series_error.append(f"{patient_name} | {series_name} | {str(e)}")
                write_log(log_file, f"ERROR | Sujeto: {subj} | Serie: {series_name} | {str(e)}")

        # =========================
        # 3. LIMPIEZA FINAL
        # =========================
        print(f"\n🧹 Eliminando anonimizados temporales: {anon_path}")

        write_log(log_file, f"===== FIN SUJETO: {patient_name} =====")

        safe_rmtree(anon_path)

        procesados.append(patient_name)

    generate_summary(
        root_dir,
        fecha_inicio,
        procesados,
        pendientes,
        errores,
        series_procesadas,
        series_error
    )

    write_log(log_file, "===== FIN PIPELINE =====")

    print("\n✅ PIPELINE COMPLETO")
	    