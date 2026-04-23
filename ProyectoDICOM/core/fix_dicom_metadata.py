import os
import pydicom


def fix_metadata(original_series, new_series):

    print("🧠 Fixing DICOM metadata")

    orig_files = sorted([
        os.path.join(original_series, f)
        for f in os.listdir(original_series)
        if os.path.isfile(os.path.join(original_series, f))
    ])

    new_files = sorted([
        os.path.join(new_series, f)
        for f in os.listdir(new_series)
        if os.path.isfile(os.path.join(new_series, f))
    ])

    if len(orig_files) != len(new_files):
        raise RuntimeError("Mismatch número de slices")

    for o, n in zip(orig_files, new_files):

        ds_orig = pydicom.dcmread(o, stop_before_pixels=True)
        ds_new = pydicom.dcmread(n)

        # =========================
        # COPIAR METADATA CRÍTICA
        # =========================
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

        # opcional: mantener paciente
        ds_new.PatientID = ds_orig.PatientID
        ds_new.PatientName = ds_orig.PatientName

        ds_new.save_as(n)

    print("✔ Metadata corregida")