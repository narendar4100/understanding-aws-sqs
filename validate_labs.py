import json
import re
from pathlib import Path

root = Path("frontend")
for path in sorted(root.rglob("*.html")):
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script id="lab-data" type="application/json">(.*?)</script>',
        text,
        re.S,
    )
    brand = "nav" if "AWS Architecture Lab" in text else "OLD"
    if not match:
        print(f"{path.as_posix()} no-lab {brand}")
        continue
    data = json.loads(match.group(1))
    for case in data:
        if not 0 <= case["answer"] < len(case["options"]):
            raise SystemExit(f"bad answer in {path}")
    missing = [token for token in ("id=\"live-lab\"", "id=\"lab-choices\"", "lab.js") if token not in text]
    print(f"{path.as_posix()} {len(data)} cases {brand} missing={missing}")
