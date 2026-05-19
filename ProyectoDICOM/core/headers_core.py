import os
import pydicom
from pydicom.uid import generate_uid


# =========================
# AGRUPAR SERIES DICOM
# =========================
def group_series(input_dir):

    series = {}

    for root, _, files in os.walk(input_dir):

        for f in files:

            path = os.path.join(root, f)

            try:
                ds = pydicom.dcmread(
                    path,
                    stop_before_pixels=True
                )

            except:
                continue

            # =========================
            # OBTENER SERIES INSTANCE UID
            # =========================
            uid = ds.get("SeriesInstanceUID", None)

            # fallback si no existe UID
            if uid is None:
                uid = f"NO_UID_{root}"

            if uid not in series:
                series[uid] = []

            series[uid].append(path)

    return series


# =========================
# ANONIMIZACIÓN DICOM
# =========================
def anonymize_subject(
    input_dir,
    output_dir,
    patient_name
):

    series_dict = group_series(input_dir)

    # UID único para el estudio completo
    new_study_uid = generate_uid()

    for series_uid, files in series_dict.items():

        # UID único por serie
        new_series_uid = generate_uid()

        for f in files:

            ds = pydicom.dcmread(f)

            # =========================
            # ANONIMIZACIÓN PACIENTE
            # =========================
            ds.PatientName = patient_name
            ds.PatientID = patient_name

            ds.PatientBirthDate = ""
            ds.PatientSex = ""

            ds.InstitutionName = ""
            ds.ReferringPhysicianName = ""
            ds.OperatorsName = ""
            ds.PatientAddress = ""
            ds.OtherPatientIDs = ""

            # =========================
            # REEMPLAZO DE UID
            # =========================
            ds.StudyInstanceUID = new_study_uid
            ds.SeriesInstanceUID = new_series_uid
            ds.SOPInstanceUID = generate_uid()

            # =========================
            # NOMBRE DE LA SERIE
            # =========================
            series_name = str(
                ds.get(
                    "SeriesDescription",
                    "SERIE"
                )
            )

            # limpiar caracteres inválidos
            series_name = "".join(
                c if c.isalnum() or c in " _-"
                else "_"
                for c in series_name
            )

            # =========================
            # CREAR DIRECTORIO
            # =========================
            save_dir = os.path.join(
                output_dir,
                series_name
            )

            os.makedirs(
                save_dir,
                exist_ok=True
            )

            # =========================
            # GUARDAR DICOM
            # =========================
            ds.save_as(
                os.path.join(
                    save_dir,
                    os.path.basename(f)
                )
            )