import subprocess


def run_wsl(cmd):
    p = subprocess.run(
        ["wsl", "bash", "-lc", cmd],
        capture_output=True,
        text=True
    )

    print(p.stdout)
    print(p.stderr)

    if p.returncode != 0:
        raise RuntimeError("WSL error")


# =========================
# FUNCTION FOR MAIN
# =========================
def deface_nifti(nifti_file, out_file):

    cmd = f'''
    pydeface "{nifti_file}" --outfile "{out_file}" --force
    '''

    run_wsl(cmd)