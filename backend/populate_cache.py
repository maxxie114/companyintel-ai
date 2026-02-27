#!/usr/bin/env python3
"""
Manually populate Redis cache from Yutori research + browsing results.

Steps:
  1. Re-parse existing research cache (OpenAI, Stripe) to extract structured fields
  2. Start Yutori browsing tasks for OpenAI, Stripe, Tesla in parallel
  3. Poll until complete, then cache browsing results
"""

import asyncio
import json
import re
import hashlib
import sys
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

YUTORI_KEY = os.environ["YUTORI_API_KEY"]
YUTORI_BASE = "https://api.yutori.com/v1"
HEADERS = {"X-API-Key": YUTORI_KEY}

COMPANIES = [
    {"name": "OpenAI",  "website": "https://openai.com",  "docs_url": "https://platform.openai.com/docs"},
    {"name": "Stripe",  "website": "https://stripe.com",  "docs_url": "https://docs.stripe.com"},
    {"name": "Tesla",   "website": "https://tesla.com",   "docs_url": "https://developer.tesla.com"},
]

# ── Redis helpers ──────────────────────────────────────────────────────────────

import redis.asyncio as aioredis

REDIS_URL = os.environ["REDIS_URL"]

async def redis_get(client, key):
    val = await client.get(key)
    return json.loads(val) if val else None

async def redis_set(client, key, value, ttl=86400 * 7):
    await client.setex(key, ttl, json.dumps(value, default=str))
    print(f"  ✓ Cached → {key}")

def research_key(name):
    h = hashlib.md5(name.lower().encode()).hexdigest()
    return f"yutori:research:{h}:{name.lower().replace(' ', '_')}"

def browsing_key(url):
    h = hashlib.md5(url.lower().encode()).hexdigest()
    clean = url.replace("https://","").replace("http://","")[:50]
    return f"yutori:browsing:{h}:{clean}"

# ── HTML parsing helpers ───────────────────────────────────────────────────────

def strip_tags(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html).strip()

def extract_bold_field(html: str, label: str) -> str:
    """Extract value after <b>Label:</b> in HTML"""
    pattern = rf"<b>{re.escape(label)}[:\s]*</b>\s*(.*?)(?:<|$)"
    m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
    if m:
        return strip_tags(m.group(1)).strip(" .\n\t—-")
    return ""

def parse_employee_count(text: str) -> str:
    text = text.strip()
    # Grab first meaningful phrase before comma/period/bracket
    text = re.split(r"[,\(\[]", text)[0].strip()
    return text[:80] if text else ""

def parse_year(text: str):
    m = re.search(r"\b(19|20)\d{2}\b", text)
    return int(m.group()) if m else None

def reparse_research(company_name: str, raw: dict) -> dict:
    """Re-extract structured fields from Yutori HTML raw_content."""
    html = raw.get("raw_content") or raw.get("description") or ""

    founded_text  = extract_bold_field(html, "Founding year") or extract_bold_field(html, "Founded")
    hq_text       = extract_bold_field(html, "Headquarters")
    emp_text      = extract_bold_field(html, "Employee count") or extract_bold_field(html, "Employees")
    mission_text  = extract_bold_field(html, "Mission")
    industry_text = extract_bold_field(html, "Industry")
    status_text   = extract_bold_field(html, "Status")

    # Clean description — first plain-text paragraph
    plain = strip_tags(html)
    # Take up to 400 chars of clean text
    desc = re.sub(r"\s+", " ", plain).strip()[:400]

    # Website: keep existing or derive
    website = raw.get("website") or f"https://{company_name.lower()}.com"
    domain  = website.replace("https://","").replace("http://","").split("/")[0]

    result = dict(raw)  # start with existing fields
    result.update({
        "description": desc,
        "founded_year": parse_year(founded_text) if founded_text else raw.get("founded_year"),
        "headquarters": hq_text or raw.get("headquarters") or "",
        "employee_count": parse_employee_count(emp_text) if emp_text else raw.get("employee_count") or "",
        "mission": mission_text[:300] if mission_text else raw.get("mission") or "",
        "industry": [i.strip() for i in industry_text.split("/")][:4] if industry_text else raw.get("industry") or ["Technology"],
        "status": "public" if "public" in status_text.lower() else ("private" if status_text else raw.get("status","private")),
        "website": website,
        "logo_url": f"https://logo.clearbit.com/{domain}",
    })
    return result

# ── Yutori Browsing ────────────────────────────────────────────────────────────

async def start_browsing_task(client: httpx.AsyncClient, company: dict) -> str | None:
    url = company["docs_url"]
    print(f"  → Starting Yutori browsing task for {company['name']} ({url})")
    try:
        r = await client.post(
            f"{YUTORI_BASE}/browsing/tasks",
            headers=HEADERS,
            json={
                "task": (
                    f"You are on the {company['name']} developer documentation site. "
                    "Extract and summarize: (1) all main API product names and what they do, "
                    "(2) available SDK languages / client libraries, "
                    "(3) pricing tiers (names and prices if visible), "
                    "(4) key API endpoint categories. "
                    "Return a structured plain-text summary."
                ),
                "start_url": url,
            },
            timeout=30.0,
        )
        r.raise_for_status()
        task_id = r.json().get("task_id")
        print(f"  ✓ Task created: {task_id}")
        return task_id
    except Exception as e:
        print(f"  ✗ Failed to start browsing for {company['name']}: {e}")
        return None

async def poll_browsing_task(client: httpx.AsyncClient, task_id: str, company_name: str,
                              max_wait_s: int = 900) -> dict | None:
    """Poll every 10s until succeeded/failed or timeout."""
    print(f"  ⏳ Polling browsing task {task_id} for {company_name} (max {max_wait_s}s)...")
    for attempt in range(max_wait_s // 10):
        await asyncio.sleep(10)
        try:
            r = await client.get(
                f"{YUTORI_BASE}/browsing/tasks/{task_id}",
                headers=HEADERS,
                timeout=30.0,
            )
            if r.status_code == 200:
                data = r.json()
                status = data.get("status", "")
                if attempt % 6 == 0:  # log every minute
                    print(f"    [{company_name}] status={status} ({attempt * 10}s elapsed)")
                if status == "succeeded":
                    print(f"  ✅ Browsing complete for {company_name}")
                    return data
                if status == "failed":
                    print(f"  ✗ Browsing failed for {company_name}: {data.get('error','unknown')}")
                    return None
        except Exception as e:
            print(f"    Poll error ({company_name}): {e}")
    print(f"  ⏱ Timeout polling browsing for {company_name}")
    return None

def parse_browsing_result(result_data: dict) -> dict:
    """Convert Yutori browsing result to ProductsAPIs format."""
    result = result_data.get("result") or ""
    if isinstance(result, dict):
        text = result.get("content") or result.get("text") or str(result)
    else:
        text = str(result)

    return {
        "products": [],
        "apis": [],
        "documentation_quality": 3.5,
        "sdk_languages": [],
        "pricing": [],
        "raw_content": text[:2000],
    }

# ── Main ───────────────────────────────────────────────────────────────────────

async def main():
    print("\n🚀 CompanyIntel Cache Populator\n")

    redis = await aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)

    # ── Step 1: Re-parse research cache ───────────────────────────────────────
    print("━━━ Step 1: Re-parsing research cache ━━━")
    for company in COMPANIES:
        name = company["name"]
        key  = research_key(name)
        raw  = await redis_get(redis, key)
        if not raw:
            print(f"  ⚠ No research cache for {name}, skipping re-parse")
            continue
        if not raw.get("raw_content"):
            print(f"  ✓ {name} already has clean structured data, skipping")
            continue

        enriched = reparse_research(name, raw)
        await redis_set(redis, key, enriched, ttl=86400 * 7)
        print(f"  📝 {name}: founded={enriched.get('founded_year')} | hq={enriched.get('headquarters')[:50]} | employees={enriched.get('employee_count')}")

    print()

    # ── Step 2: Start browsing tasks in parallel ───────────────────────────────
    print("━━━ Step 2: Starting Yutori browsing tasks ━━━")
    async with httpx.AsyncClient() as client:
        # Check which ones already have browsing cache
        to_browse = []
        for company in COMPANIES:
            bkey = browsing_key(company["website"])
            existing = await redis_get(redis, bkey)
            if existing:
                print(f"  ✓ {company['name']} browsing already cached, skipping")
            else:
                to_browse.append(company)

        if not to_browse:
            print("  All browsing data already cached!")
        else:
            # Start all tasks in parallel
            task_ids = await asyncio.gather(*[
                start_browsing_task(client, c) for c in to_browse
            ])

            print()
            print("━━━ Step 3: Polling browsing tasks ━━━")

            # Poll all in parallel
            results = await asyncio.gather(*[
                poll_browsing_task(client, tid, c["name"])
                for c, tid in zip(to_browse, task_ids)
                if tid is not None
            ])

            # Cache results
            print()
            print("━━━ Step 4: Caching browsing results ━━━")
            valid_companies = [c for c, tid in zip(to_browse, task_ids) if tid is not None]
            for company, result in zip(valid_companies, results):
                if result is None:
                    print(f"  ✗ No result for {company['name']}, skipping")
                    continue
                parsed = parse_browsing_result(result)
                bkey = browsing_key(company["website"])
                await redis_set(redis, bkey, parsed, ttl=86400 * 7)
                snippet = parsed["raw_content"][:120].replace("\n", " ")
                print(f"  📄 {company['name']}: {snippet}...")

    await redis.aclose()
    print("\n✅ Done!\n")

if __name__ == "__main__":
    asyncio.run(main())
