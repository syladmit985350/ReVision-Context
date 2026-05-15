from __future__ import annotations

import json
import platform
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    required_paths = [
        repo_root / "revision_context",
        repo_root / "data" / "synthetic",
        repo_root / "outputs",
        repo_root / "third_party",
        repo_root / "tests",
    ]

    report = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "repo_root": str(repo_root),
        "paths_present": {str(path.relative_to(repo_root)): path.exists() for path in required_paths},
    }

    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
