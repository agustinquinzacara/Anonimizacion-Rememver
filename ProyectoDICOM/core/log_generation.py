import os
import traceback
from datetime import datetime


# =========================
# ESCRIBIR EN LOG
# =========================
def write_log(log_file, message):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    line = f"[{timestamp}] {message}"

    print(line)

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(line + "\n")


# =========================
# ERROR FATAL
# =========================
def log_fatal_error(log_file, error):

    write_log(
        log_file,
        "===== ERROR FATAL ====="
    )

    write_log(
        log_file,
        str(error)
    )

    with open(
        log_file,
        "a",
        encoding="utf-8"
    ) as f:

        f.write("\n")
        f.write(traceback.format_exc())
        f.write("\n")


# =========================
# GENERAR RESUMEN FINAL
# =========================
def generate_summary(
    root_dir,
    inicio,
    procesados,
    pendientes,
    errores,
    series_procesadas,
    series_error
):

    fin = datetime.now()

    resumen_file = os.path.join(
        root_dir,
        "resumen_pipeline.txt"
    )

    with open(
        resumen_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "===== PIPELINE DICOM =====\n"
        )

        f.write(
            f"Fecha inicio: {inicio}\n"
        )

        f.write(
            f"Fecha fin:    {fin}\n\n"
        )

        f.write(
            f"Sujetos procesados: "
            f"{len(procesados)}\n"
        )

        f.write(
            f"Sujetos pendientes REDCap: "
            f"{len(pendientes)}\n"
        )

        f.write(
            f"Errores generales: "
            f"{len(errores)}\n"
        )

        f.write(
            f"Errores en series: "
            f"{len(series_error)}\n"
        )

        f.write(
            f"Series procesadas: "
            f"{len(series_procesadas)}\n\n"
        )

        # =====================
        # SUJETOS PROCESADOS
        # =====================
        f.write(
            "===== SUJETOS PROCESADOS =====\n"
        )

        for p in procesados:
            f.write(f"- {p}\n")

        # =====================
        # PENDIENTES REDCAP
        # =====================
        f.write(
            "\n===== PENDIENTES REDCAP =====\n"
        )

        for p in pendientes:
            f.write(f"- {p}\n")

        # =====================
        # SERIES PROCESADAS
        # =====================
        f.write(
            "\n===== SERIES PROCESADAS =====\n"
        )

        for s in series_procesadas:
            f.write(f"- {s}\n")

        # =====================
        # ERRORES GENERALES
        # =====================
        f.write(
            "\n===== ERRORES GENERALES =====\n"
        )

        for e in errores:
            f.write(f"- {e}\n")

        # =====================
        # ERRORES EN SERIES
        # =====================
        f.write(
            "\n===== ERRORES EN SERIES =====\n"
        )

        for e in series_error:
            f.write(f"- {e}\n")

    return resumen_file