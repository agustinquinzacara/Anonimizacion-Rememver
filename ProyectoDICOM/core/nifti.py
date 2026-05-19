import subprocess


# =========================
# EJECUTAR COMANDOS EN WSL
# =========================
def run(cmd):

    p = subprocess.run(
        ["wsl", "bash", "-lc", cmd],
        capture_output=True,
        text=True
    )

    # salida estándar
    if p.stdout:
        print("\n🟡 STDOUT:\n")
        print(p.stdout)

    # salida de errores
    if p.stderr:
        print("\n🔴 STDERR:\n")
        print(p.stderr)

    # validar ejecución
    if p.returncode != 0:
        raise RuntimeError("❌ Error en WSL")


# =========================
# DICOM → NIFTI
# =========================
def dicom_to_nifti(
    dicom_dir,
    out_dir
):

    cmd = f'''
    mkdir -p "{out_dir}"

    dcm2niix \
        -z y \
        -x n \
        -o "{out_dir}" \
        "{dicom_dir}"
    '''

    run(cmd)