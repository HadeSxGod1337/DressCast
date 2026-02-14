"""Generate gRPC Python code from proto files."""

import subprocess  # nosec B404 - build-time protoc invocation, not user input
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR = PROJECT_ROOT / "proto"
OUT_DIR = PROJECT_ROOT / "proto_gen"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    proto_files = sorted(PROTO_DIR.glob("*.proto"))
    if not proto_files:
        print("No .proto files found in", PROTO_DIR)
        return 1
    cmd = [
        sys.executable,
        "-m",
        "grpc_tools.protoc",
        "-I",
        str(PROTO_DIR),
        "--python_out",
        str(OUT_DIR),
        "--grpc_python_out",
        str(OUT_DIR),
    ] + [str(p) for p in proto_files]
    result = subprocess.run(cmd)  # nosec B603 - cmd from project paths only
    if result.returncode != 0:
        return result.returncode
    # Create __init__.py so proto_gen is a package
    (OUT_DIR / "__init__.py").touch()
    print("Generated in", OUT_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
