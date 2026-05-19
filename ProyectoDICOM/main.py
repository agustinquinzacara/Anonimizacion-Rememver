import os
import shutil
import time
import pydicom
from tkinter import Tk, filedialog, simpledialog

from core.headers_core import anonymize_subject
from core.nifti import dicom_to_nifti
from core.deface2 import deface_nifti
from core.nifti_to_dicom_plastimatch import nifti_to_dicom_plastimatch
from core.fix_dicom_metadata import fix_metadata
from core.fix_nifti_dtype import fix_dtype


# =========================
# INTERFAZ
# =========================
def select_root():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    return filedialog.askdirectory(title="Selecciona carpeta con sujetos")


def ask_prefix():
    root = Tk()
    root.withdraw()
    prefix = simpledialog.askstring("Prefijo", "Ej: SUB, PAC, CTRL")
    start = simpledialog.askinteger("Inicio", "Número inicial", initialvalue=1)
    return prefix, start


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
                    "dose",
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
                if modality == "CT":
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

    root_dir = select_root()

    if not root_dir:
        exit()

    prefix, counter = ask_prefix()

    print("\nROOT:", root_dir)

    subjects = [
        d for d in os.listdir(root_dir)
        if os.path.isdir(os.path.join(root_dir, d))
        and not d.endswith("_processed")
        and d != "anonimizados"
    ]

    for subj in sorted(subjects):

        subj_path = os.path.join(root_dir, subj)
        patient_name = f"{prefix}-{counter:03d}"

        print(f"\nSUBJECT: {subj} → {patient_name}")

        # =========================
        # 1. ANONIMIZACIÓN DICOM
        # =========================
        anon_path = os.path.join(root_dir, "anonimizados", patient_name)

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

            print(f"\nSERIES: {series_name}")

            try:
                relative = os.path.relpath(in_series, anon_path)

                out_series = os.path.join(output_root, relative)

                # =====================
                # VALIDAR SI ES ESTRUCTURAL
                # =====================
                if not is_structural(in_series):

                    shutil.copytree(
                        in_series,
                        out_series,
                        dirs_exist_ok=True
                    )

                    print("SKIP (no estructural)")
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
                fix_dtype(nii)

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

                print("✔ Procesamiento completado")

            except Exception as e:
                print("❌ ERROR:", e)

        # =========================
        # 3. LIMPIEZA FINAL
        # =========================
        print(f"\n🧹 Eliminando anonimizados temporales: {anon_path}")

        safe_rmtree(anon_path)

        counter += 1

    print("\n✅ PIPELINE COMPLETO")