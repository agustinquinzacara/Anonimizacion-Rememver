import os
import pydicom
from pydicom.uid import generate_uid


def group_series(input_dir):
    series = {}

    for root, _, files in os.walk(input_dir):
        for f in files:
            path = os.path.join(root, f)

            try:
                ds = pydicom.dcmread(path, stop_before_pixels=True)
            except:
                continue

            uid = ds.SeriesInstanceUID

            if uid not in series:
                series[uid] = []

            series[uid].append(path)

    return series


def anonymize_subject(input_dir, output_dir, patient_name):

    series_dict = group_series(input_dir)

    new_study_uid = generate_uid()

    for series_uid, files in series_dict.items():

        new_series_uid = generate_uid()

        for f in files:
            ds = pydicom.dcmread(f)

            # --- ANON ---
            ds.PatientName = patient_name
            ds.PatientID = patient_name
            ds.PatientBirthDate = ""
            ds.PatientSex = ""

            ds.InstitutionName = ""
            ds.ReferringPhysicianName = ""
            ds.OperatorsName = ""
            ds.PatientAddress = ""
            ds.OtherPatientIDs = ""

            # --- UID ---
            ds.StudyInstanceUID = new_study_uid
            ds.SeriesInstanceUID = new_series_uid
            ds.SOPInstanceUID = generate_uid()

            rel = os.path.relpath(os.path.dirname(f), input_dir)
            save_dir = os.path.join(output_dir, rel)
            os.makedirs(save_dir, exist_ok=True)

            ds.save_as(os.path.join(save_dir, os.path.basename(f)))