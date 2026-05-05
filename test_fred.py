import os
import requests

from dotenv import load_dotenv
load_dotenv()

api_key = os.environ.get("FRED_API_KEY")
series_ids = ["ACMTP10", "DRTSCILM", "SAHMREALTIME", "AWHNONPI", "TEMPHELPS"]

for s in series_ids:
    url = f"https://api.stlouisfed.org/fred/series?series_id={s}&api_key={api_key}&file_type=json"
    res = requests.get(url)
    if res.status_code == 200:
        print(f"FOUND: {s} - {res.json()['seriess'][0]['title']}")
    else:
        print(f"MISSING: {s}")
