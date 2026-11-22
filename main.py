"""Punto de entrada local del proyecto. Azure se despliega aparte con deploy/azure/Deploy.ps1.

    python main.py pipeline       # pipeline CRISP-DM completo (datos -> modelos -> reportes)
    python main.py predict        # predice las primeras 5 filas del CSV limpio (tras pipeline)
    python main.py train          # reentrena el modelo del servicio (outputs/models/serving)
    python main.py local          # API (8000) + dashboard (8501) sin Docker
    python main.py docker         # API + dashboard con Docker Compose (API expuesta en 8000)
    python main.py docker --down  # detiene los contenedores
    python main.py test           # pruebas
"""
import argparse
import subprocess
import sys

PY = sys.executable
COMPOSE = ["docker", "compose", "-f", "docker-compose.yaml", "-f", "docker-compose.dev.yaml"]


def run(cmd):
    sys.exit(subprocess.call(cmd))


def local():
    api = subprocess.Popen([PY, "-m", "uvicorn", "deploy.web.api.main:app", "--host", "127.0.0.1", "--port", "8000"])
    try:
        # ponytail: el dashboard arranca antes de que la API esté lista; muestra el estado al recargar.
        subprocess.call([PY, "-m", "streamlit", "run", "deploy/web/main.py", "--server.address=127.0.0.1"])
    finally:
        api.terminate()
        api.wait()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pipeline").add_argument("--extras", action="store_true", help="validación cruzada y GridSearchCV")
    predict = sub.add_parser("predict")
    predict.add_argument("--input", default="data/processed/dry_bean_clean.csv")
    predict.add_argument("--n", default="5")
    sub.add_parser("train")
    sub.add_parser("local")
    sub.add_parser("docker").add_argument("--down", action="store_true")
    sub.add_parser("test")
    args = parser.parse_args()

    if args.cmd == "pipeline":
        run([PY, "-m", "src.laboratorio_drybean"] + (["--extras"] if args.extras else []))
    elif args.cmd == "predict":
        run([PY, "-m", "src.predict", "--input", args.input, "--n", args.n])
    elif args.cmd == "train":
        run([PY, "-m", "deploy.web.prepare_serving_model"])
    elif args.cmd == "local":
        local()
    elif args.cmd == "docker":
        run(COMPOSE + (["down"] if args.down else ["up", "--build", "-d", "--wait"]))
    else:
        run([PY, "-m", "pytest", "-q"])


if __name__ == "__main__":
    main()
