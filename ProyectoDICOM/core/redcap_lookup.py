import os
import csv
import pydicom
from tkinter import Tk, filedialog


# =========================
# SELECCIONAR CSV REDCAP
# =========================
def select_redcap_csv(root_dir):

    csv_files = []

    for f in os.listdir(root_dir):

        path = os.path.join(root_dir, f)

        if (
            os.path.isfile(path)
            and f.lower().endswith(".csv")
        ):
            csv_files.append(path)

    # Un único CSV
    if len(csv_files) == 1:

        print(
            f"✔ CSV REDCap encontrado: "
            f"{os.path.basename(csv_files[0])}"
        )

        return csv_files[0]

    # Varios CSV
    elif len(csv_files) > 1:

        print("\nSe encontraron varios CSV:\n")

        for i, f in enumerate(csv_files):
            print(
                f"[{i+1}] "
                f"{os.path.basename(f)}"
            )

        opcion = int(
            input(
                "\nSeleccione un CSV: "
            )
        ) - 1

        return csv_files[opcion]

    # Ningún CSV
    print(
        "⚠ No se encontró un CSV "
        "en la carpeta seleccionada."
    )

    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    return filedialog.askopenfilename(
        title="Seleccionar CSV REDCap",
        filetypes=[("CSV", "*.csv")]
    )


# =========================
# OBTENER PATIENT ID
# =========================
def get_patient_id(subject_path):

    for root, _, files in os.walk(subject_path):

        for f in files:

            path = os.path.join(root, f)

            try:
                ds = pydicom.dcmread(
                    path,
                    stop_before_pixels=True
                )

                patient_id = str(
                    ds.get("PatientID", "")
                ).strip()

                if patient_id:
                    return patient_id

            except:
                pass

    return None


# =========================
# BUSCAR ID REDCAP
# =========================
import re


def normalize_rut(rut):

    return (
        str(rut)
        .replace(".", "")
        .replace(" ", "")
        .upper()
        .strip()
    )


def find_redcap_id(csv_file, rut):

    rut = normalize_rut(rut)

    with open(
        csv_file,
        encoding="utf-8-sig"
    ) as f:

        next(f, None)  # saltar encabezado

        for line in f:

            line = line.strip()

            if not line:
                continue

            line = line.replace('"', '')
            parts = line.split(",")

            if len(parts) < 5:
                continue

            redcap_id = parts[0].replace('"', '').strip()
            csv_rut = parts[-1].replace('"', '').strip()

#Recordar Borrar esta parte
#            print(f"Buscando RUT : {rut}")
#            print(f"CSV RUT      : {csv_rut}")
#            print(f"REDCap ID    : {redcap_id}")
#            print("-------------------")
# Hasta aqui

            if normalize_rut(csv_rut) == rut:

                match = re.search(r"\d+", redcap_id)

                if match:
                    return match.group(0)

                return redcap_id

    return None


# =========================
# GENERAR ID FINAL
# =========================
def generate_subject_id(
    csv_file,
    rut,
    prefix
):

    redcap_id = find_redcap_id(
        csv_file,
        rut
    )

    if redcap_id:

        patient_name = (
            f"{prefix}-{redcap_id}"
        )

        print(
            f"✔ ID REDCap encontrado: "
            f"{patient_name}"
        )

        return patient_name

    digits = rut.split("-")[0]

    if len(digits) >= 4:
        suffix = digits[-4:]
    else:
        suffix = digits

    patient_name = (
        f"{prefix}-NID-{suffix}"
    )

    print(
        f"⚠ RUT no encontrado en REDCap: {rut}"
    )

    print(
        f"⚠ Se utilizará: {patient_name}"
    )

    return patient_name