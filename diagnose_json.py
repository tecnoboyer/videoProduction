"""Diagnose JSON files in project."""
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

PROJECT_ID = "volcanes_040b3700"
PROJECT_DIR = Path("projects") / PROJECT_ID

files_to_check = [
    "script/output/dialogue.json",
    "script/output/output.json",
    "audio/output/tts_manifest.json",
    "audio/output/assembly.json",
    "alignment/output/alignment.json",
]

print(f"Checking project: {PROJECT_ID}\n")

for rel_path in files_to_check:
    full_path = PROJECT_DIR / rel_path
    print(f"\n{rel_path}:")
    if not full_path.exists():
        print("  [NOT FOUND]")
        continue
    content = full_path.read_text(encoding="utf-8").strip()
    print(f"  Size: {len(content)} chars")
    try:
        data = json.loads(content)
        if isinstance(data, list):
            print(f"  [OK] JSON array with {len(data)} items")
        elif isinstance(data, dict):
            print(f"  [OK] JSON object with keys: {list(data.keys())}")
        else:
            print(f"  [OK] JSON {type(data).__name__}")
    except json.JSONDecodeError as e:
        print(f"  [BROKEN] {e}")
        print(f"  Preview: {content[:100]!r}")
