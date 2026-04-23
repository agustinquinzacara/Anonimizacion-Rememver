import subprocess


def nifti_to_dicom_plastimatch(nifti_file, dicom_folder, output_dir):

    cmd = f'''
    plastimatch convert \
        --input "{nifti_file}" \
        --output-dicom "{output_dir}" \
        --referenced-ct "{dicom_folder}"
    '''

    p = subprocess.run(
        ["wsl", "bash", "-lc", cmd],
        capture_output=True,
        text=True
    )

    print("\n🟡 STDOUT:\n", p.stdout)
    print("\n🔴 STDERR:\n", p.stderr)

    if p.returncode != 0:
        raise RuntimeError("❌ plastimatch falló")