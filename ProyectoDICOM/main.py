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
# UI
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
# UTILS
# =========================
def to_wsl(p):
    return p.replace("C:", "/mnt/c").replace("\\", "/")


def safe_rmtree(path):
    """Borrado robusto en Windows"""
    if not os.path.exists(path):
        return

    for i in range(3):
        try:
            shutil.rmtree(path)
            print(f"🗑️ Eliminado: {path}")
            return
        except Exception as e:
            print(f"⚠️ intento {i+1} falló eliminando {path}: {e}")
            time.sleep(1)

    print(f"❌ No se pudo eliminar: {path}")


# =========================
# T1 DETECTION
# =========================
def is_t1(series_path):
    keywords = ["t1", "mprage", "spgr", "bravo", "tfe", "t1w"]

    for root, _, files in os.walk(series_path):
        for f in files:
            try:
                ds = pydicom.dcmread(os.path.join(root, f), stop_before_pixels=True)

                text = " ".join([
                    str(ds.get("SeriesDescription", "")).lower(),
                    str(ds.get("ProtocolName", "")).lower()
                ])

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
        # 1. ANONIMIZACIÓN
        # =========================
        anon_path = os.path.join(root_dir, "anonimizados", patient_name)
        anonymize_subject(subj_path, anon_path, patient_name)

        # =========================
        # 2. PROCESAMIENTO
        # =========================
        output_root = anon_path + "_processed"
        os.makedirs(output_root, exist_ok=True)

        series_list = [
            s for s in os.listdir(anon_path)
            if os.path.isdir(os.path.join(anon_path, s))
        ]

        for series in series_list:

            print(f"\nSERIES: {series}")

            try:
                in_series = os.path.join(anon_path, series)
                out_series = os.path.join(output_root, series)

                if not is_t1(in_series):
                    shutil.copytree(in_series, out_series, dirs_exist_ok=True)
                    print("SKIP (no T1)")
                    continue

                print("T1 PIPELINE")

                tmp_dir = os.path.join(output_root, "_tmp_nifti")
                os.makedirs(tmp_dir, exist_ok=True)

                dicom_to_nifti(to_wsl(in_series), to_wsl(tmp_dir))

                nii_files = [
                    os.path.join(tmp_dir, f)
                    for f in os.listdir(tmp_dir)
                    if f.endswith(".nii.gz") and "_defaced" not in f
                ]

                if not nii_files:
                    raise RuntimeError("No NIfTI generado")

                nii = max(nii_files, key=os.path.getctime)

                fix_dtype(nii)

                defaced = nii.replace(".nii.gz", "_defaced.nii.gz")
                deface_nifti(to_wsl(nii), to_wsl(defaced))

                # borrar nifti original
                try:
                    os.remove(nii)
                except:
                    pass

                nifti_to_dicom_plastimatch(
                    to_wsl(defaced),
                    to_wsl(in_series),
                    to_wsl(out_series)
                )

                fix_metadata(in_series, out_series)

                safe_rmtree(tmp_dir)

                print("OK")

            except Exception as e:
                print("ERROR:", e)

        # =========================
        # 🔥 BORRADO FINAL
        # =========================
        print(f"\n🧹 Limpiando anonimizados sin procesar: {anon_path}")
        safe_rmtree(anon_path)

        counter += 1

    print("\nPIPELINE COMPLETO")