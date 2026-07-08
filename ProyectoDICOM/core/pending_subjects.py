import os
import shutil
from datetime import datetime
import pydicom


# =========================
# OBTENER PRIMER DICOM
# =========================
def get_first_dicom(subject_path):

    for root, _, files in os.walk(subject_path):

        for f in files:

            path = os.path.join(root, f)

            try:
                ds = pydicom.dcmread(
                    path,
                    stop_before_pixels=True
                )

                return ds

            except:
                continue

    return None


# =========================
# CREAR LOG
# =========================
def create_log(
    ds,
    log_path,
    subject_name
):

    with open(
        log_path,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            f"Fecha: "
            f"{datetime.now()}\n\n"
        )

        f.write(
            "Motivo:\n"
            "RUT no encontrado en REDCap\n\n"
        )

        f.write(
            f"Sujeto original:\n"
            f"{subject_name}\n\n"
        )

        tags = [
            "PatientName",
            "PatientID",
            "PatientBirthDate",
            "PatientSex",
            "StudyDate",
            "StudyDescription",
            "InstitutionName",
            "AccessionNumber",
            "Modality"
        ]

        f.write(
            "Headers DICOM:\n"
        )

        for tag in tags:

            value = ds.get(
                tag,
                "No disponible"
            )

            f.write(
                f"{tag}: "
                f"{value}\n"
            )


# =========================
# MOVER A PENDIENTES
# =========================
def move_to_pending(
    subj_path,
    root_dir
):

    subject_name = os.path.basename(
        subj_path
    )

    pending_root = os.path.join(
        root_dir,
        "pendientes_redcap"
    )

    os.makedirs(
        pending_root,
        exist_ok=True
    )

    destination = os.path.join(
        pending_root,
        subject_name
    )

    if os.path.exists(destination):

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        destination += (
            f"_{timestamp}"
        )

    # mover sujeto completo
    shutil.move(
        subj_path,
        destination
    )

    # crear log
    ds = get_first_dicom(
        destination
    )

    if ds:

        log_path = os.path.join(
            destination,
            "log.txt"
        )

        create_log(
            ds,
            log_path,
            subject_name
        )

    print(
        f"⚠ Sujeto movido a "
        f"pendientes_redcap: "
        f"{subject_name}"
    )