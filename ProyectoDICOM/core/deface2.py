import subprocess


# =========================
# EJECUTAR COMANDOS EN WSL
# =========================
def run_wsl(cmd):

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
        raise RuntimeError("❌ Error en WSL")


# =========================
# DEFACING NIFTI
# =========================
def deface_nifti(
    nifti_file,
    out_file
):

    cmd = f'''
    pydeface \
        "{nifti_file}" \
        --outfile "{out_file}" \
        --force
    '''

    run_wsl(cmd)