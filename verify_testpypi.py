"""Fetch a TestPyPI wheel plus provenance and verify both with pypi-attestations.

This script does not install or execute the downloaded wheel.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import urlopen


def fetch(url: str) -> bytes:
    with urlopen(url, timeout=30) as response:
        return response.read()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project")
    parser.add_argument("--version", default="0.0.1")
    parser.add_argument("--repository", required=True)
    parser.add_argument("--tamper", action="store_true",
                        help="Append a byte to demonstrate a failing digest check.")
    args = parser.parse_args()
    project, version = quote(args.project, safe=""), quote(args.version, safe="")
    metadata = json.loads(fetch(f"https://test.pypi.org/pypi/{project}/{version}/json"))
    wheels = [file for file in metadata["urls"] if file["packagetype"] == "bdist_wheel"]
    if len(wheels) != 1:
        raise SystemExit("Diese Minimaldemo erwartet genau ein Wheel pro Version.")
    item = wheels[0]
    filename = item["filename"]
    if Path(filename).name != filename or not filename.endswith(".whl"):
        raise SystemExit("Unerwarteter Dateiname in den Registry-Metadaten.")
    origin = urlparse(item["url"])
    if origin.scheme != "https" or not (origin.hostname or "").endswith(".pythonhosted.org"):
        raise SystemExit("Unerwarteter Download-Host in den Registry-Metadaten.")
    provenance_url = (
        f"https://test.pypi.org/integrity/{project}/{version}/"
        f"{quote(filename, safe='')}/provenance"
    )
    with tempfile.TemporaryDirectory(prefix="tp-verification-") as temporary:
        wheel = Path(temporary) / filename
        provenance = Path(temporary) / "provenance.json"
        wheel.write_bytes(fetch(item["url"]))
        provenance.write_bytes(fetch(provenance_url))
        if args.tamper:
            with wheel.open("ab") as output:
                output.write(b"\n")
        command = [sys.executable, "-m", "pypi_attestations", "verify", "pypi",
                   "--repository", args.repository, "--provenance-file", str(provenance),
                   str(wheel)]
        return subprocess.run(command, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
