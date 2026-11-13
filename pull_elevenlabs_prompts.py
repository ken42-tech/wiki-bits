"""Read-only: pull every ElevenLabs agent's prompt into ./prompts/*.md (GET requests only)."""
import os, re, json, urllib.request
from dotenv import load_dotenv

load_dotenv()
KEY = os.environ["ELEVENLABS_API_KEY"]
BASE = "https://api.elevenlabs.io/v1/convai"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prompts")
os.makedirs(OUT, exist_ok=True)


def get(path):
    req = urllib.request.Request(BASE + path, headers={"xi-api-key": KEY})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


agents, cursor = [], None
while True:
    d = get("/agents?page_size=100" + (f"&cursor={cursor}" if cursor else ""))
    agents += d.get("agents", [])
    if not d.get("has_more"):
        break
    cursor = d.get("next_cursor")

print(f"{len(agents)} agents")
for a in agents:
    full = get(f"/agents/{a['agent_id']}")
    cfg = full.get("conversation_config", {}).get("agent", {})
    p = cfg.get("prompt", {})
    name = full.get("name") or a["agent_id"]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "-", name).strip("-") or a["agent_id"]
    fn = os.path.join(OUT, f"{slug}.md")
    if os.path.exists(fn):
        fn = os.path.join(OUT, f"{slug}-{a['agent_id'][-6:]}.md")
    with open(fn, "w", encoding="utf-8") as f:
        f.write(p.get("prompt") or "")
    print(os.path.basename(fn), "|", p.get("llm"), "| first_message:", bool(cfg.get("first_message")))
