from __future__ import annotations

from pathlib import Path

import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from visualization.typology_snapshot import write_typology_dashboard_snapshot  # noqa: E402


def build_snapshot(*, root: Path = ROOT, source_root: Path = ROOT) -> Path:
    output_path = Path(root) / "outputs" / "final" / "typology_dashboard_snapshot.html"
    return write_typology_dashboard_snapshot(root=source_root, output_path=output_path)


def main() -> None:
    output_path = build_snapshot()
    print(f"Wrote typology dashboard snapshot -> {output_path}")


if __name__ == "__main__":
    main()
