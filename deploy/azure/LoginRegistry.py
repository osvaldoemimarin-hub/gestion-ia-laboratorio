"""Entrega el token de ACR a Docker por stdin sin convertirlo en PowerShell."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def login(azure_cli: str, registry: str) -> int:
    azure_cli = str(Path(azure_cli).resolve())
    auth = subprocess.run(
        [azure_cli, "acr", "login", "--name", registry, "--expose-token", "--output", "json", "--only-show-errors"],
        capture_output=True, text=True,
    )
    if auth.returncode:
        print("Azure CLI no pudo obtener la credencial del registro.", file=sys.stderr)
        return auth.returncode
    record = json.loads(auth.stdout)
    result = subprocess.run(
        ["docker", "login", record["loginServer"], "--username", "00000000-0000-0000-0000-000000000000", "--password-stdin"],
        input=record["accessToken"].strip().encode("utf-8"), capture_output=True,
    )
    record.clear()
    if result.returncode:
        print(result.stderr.decode("utf-8", errors="replace"), file=sys.stderr)
    else:
        print("Autenticación de Docker en ACR completada.")
    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--azure-cli", required=True)
    parser.add_argument("--registry", required=True)
    parameters = parser.parse_args()
    raise SystemExit(login(parameters.azure_cli, parameters.registry))
