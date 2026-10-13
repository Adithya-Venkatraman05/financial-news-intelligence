import json
import datetime

from services.config import PROJECT_ROOT

F = PROJECT_ROOT / "data" / "cache" / "quota.json"
LIMIT = 80  # real cap is 100, keep a buffer


def used_today():
    if not F.exists():
        return 0
    d = json.loads(F.read_text())
    return d["count"] if d.get("date") == str(datetime.date.today()) else 0


def allow():
    today = str(datetime.date.today())
    F.parent.mkdir(parents=True, exist_ok=True)
    count = used_today()
    if count >= LIMIT:
        return False
    F.write_text(json.dumps({"date": today, "count": count + 1}))
    return True