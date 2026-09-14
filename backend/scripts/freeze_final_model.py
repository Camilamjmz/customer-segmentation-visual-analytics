from pathlib import Path
import sys

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.services.final_model import save_final_artifacts

if __name__ == "__main__":
    csv_path, json_path = save_final_artifacts()
    print(f"Saved {csv_path}")
    print(f"Saved {json_path}")
