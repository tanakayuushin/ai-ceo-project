import os, requests, urllib3, json
from pathlib import Path
from dotenv import load_dotenv

urllib3.disable_warnings()
load_dotenv(Path(__file__).parent.parent.parent / ".env")

token = os.environ.get("NOTION_TOKEN")
page_id = os.environ.get("NOTION_PAGE_ID")
headers = {"Authorization": f"Bearer {token}", "Notion-Version": "2022-06-28"}

def get_children(pid, indent=0):
    r = requests.get(
        f"https://api.notion.com/v1/blocks/{pid}/children?page_size=100",
        headers=headers, verify=False
    )
    if r.status_code != 200:
        print(f"{'  '*indent}[ERROR] {r.status_code}: {r.text[:100]}")
        return
    data = r.json()
    blocks = data.get("results", [])
    print(f"{'  '*indent}-> {len(blocks)} blocks inside")
    for b in blocks:
        btype = b.get("type")
        bid = b["id"]
        content = b.get(btype, {})
        print(f"{'  '*indent}  type={btype}  id={bid}")
        print(f"{'  '*indent}  content: {json.dumps(content, ensure_ascii=False)[:400]}")

# Top-level blocks
r = requests.get(
    f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100",
    headers=headers, verify=False
)
data = r.json()
blocks = data.get("results", [])
print(f"Top-level blocks: {len(blocks)}")

for b in blocks:
    btype = b.get("type")
    bid = b["id"]
    title = b.get(btype, {}).get("title", "")
    print(f"\n[{btype}] title={title}  id={bid}")
    if btype == "child_page":
        get_children(bid, indent=1)
