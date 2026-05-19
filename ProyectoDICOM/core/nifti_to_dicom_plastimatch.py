import subprocess


# =========================
# NIFTI → DICOM
# =========================
def nifti_to_dicom_plastimatch(
    nifti_file,
    dicom_folder,
    output_dir
):

    # =========================
    # COMANDO PLASTIMATCH
    # =========================
    cmd = f'''
    plastimatch convert \
        --input "{nifti_file}" \
        --output-dicom "{output_dir}" \
        --referenced-ct "{dicom_folder}"
    '''

    # =========================
    # EJECUCIÓN EN WSL
    # =========================
    p = subprocess.run(
        ["wsl", "bash", "-lc", cmd],
        capture_output=True,
        text=True
    )

    # =========================
    # SALIDA ESTÁNDAR
    # =========================
    if p.stdout:
        print("\n🟡 STDOUT:\n")
        print(p.stdout)

    # =========================
    # SALIDA DE ERRORES
    # =========================
    if p.stderr:
        print("\n🔴 STDERR:\n")
        print(p.stderr)

    # =========================
    # VALIDAR EJECUCIÓN
    # =========================
    if p.returncode != 0:
        raise RuntimeError(
            "❌ Plastimatch falló"
        )