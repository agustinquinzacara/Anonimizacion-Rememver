import os
import pydicom


# =========================
# CORRECCIÓN DE METADATOS
# =========================
def fix_metadata(
    original_series,
    new_series
):

    print("🧠 Corrigiendo metadata DICOM")

    # =========================
    # ARCHIVOS ORIGINALES
    # =========================
    orig_files = sorted([
        os.path.join(original_series, f)
        for f in os.listdir(original_series)
        if os.path.isfile(os.path.join(original_series, f))
    ])

    # =========================
    # ARCHIVOS GENERADOS
    # =========================
    new_files = sorted([
        os.path.join(new_series, f)
        for f in os.listdir(new_series)
        if os.path.isfile(os.path.join(new_series, f))
    ])

    # =========================
    # VALIDAR NÚMERO DE SLICES
    # =========================
    if len(orig_files) != len(new_files):
        raise RuntimeError(
            "Mismatch en número de slices"
        )

    # =========================
    # COPIA DE METADATOS
    # =========================
    for o, n in zip(orig_files, new_files):

        ds_orig = pydicom.dcmread(
            o,
            stop_before_pixels=True
        )

        ds_new = pydicom.dcmread(n)

        # =====================
        # TAGS GEOMÉTRICOS
        # =====================
        tags = [
            "PixelSpacing",
            "SliceThickness",
            "SpacingBetweenSlices",
            "ImageOrientationPatient",
            "ImagePositionPatient",
            "FrameOfReferenceUID"
        ]

        for t in tags:

            if t in ds_orig:
                ds_new[t] = ds_orig[t]

        # =====================
        # INFORMACIÓN PACIENTE
        # =====================
        ds_new.PatientID = ds_orig.PatientID
        ds_new.PatientName = ds_orig.PatientName

        # =====================
        # GUARDAR DICOM
        # =====================
        ds_new.save_as(n)

    print("✔ Metadata corregida")