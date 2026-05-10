import os, requests, urllib3, json
from pathlib import Path
from dotenv import load_dotenv

urllib3.disable_warnings()
load_dotenv(Path(__file__).parent.parent.parent / ".env")

token = os.environ.get("NOTION_TOKEN")
page_id = os.environ.get("NOTION_PAGE_ID")
headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}

r = requests.get(
    f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100",
    headers=headers, verify=False
)
data = r.json()
blocks = data.get("results", [])
print(f"Total blocks: {len(blocks)}")
for b in blocks:
    btype = b.get("type")
    created = b.get("created_time", "")
    bid = b["id"]
    print(f"\n  type={btype}")
    print(f"  created={created}")
    print(f"  id={bid}")
    print(f"  full content: {json.dumps(b.get(btype, {}), ensure_ascii=False)[:500]}")
