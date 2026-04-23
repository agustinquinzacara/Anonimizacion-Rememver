import subprocess


def run(cmd):
    p = subprocess.run(
        ["wsl", "bash", "-lc", cmd],
        capture_output=True,
        text=True
    )

    print(p.stdout)
    print(p.stderr)

    if p.returncode != 0:
        raise RuntimeError("Error en WSL")


# =========================
# FUNCTION FOR MAIN
# =========================
def dicom_to_nifti(dicom_dir, out_dir):

    cmd = f'''
    mkdir -p "{out_dir}"
    dcm2niix -z y -o "{out_dir}" "{dicom_dir}"
    '''

    run(cmd)