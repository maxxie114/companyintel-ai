#!/usr/bin/env python3
"""Check for active Yutori tasks in Redis and their status"""

import redis
import json
import hashlib
import os
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment
load_dotenv('backend/.env')
redis_url = os.getenv('REDIS_URL')
yutori_key = os.getenv('YUTORI_API_KEY')

print("Connecting to Redis...")
r = redis.from_url(redis_url, decode_responses=True)
r.ping()
print("✓ Connected!\n")

# Check for task IDs in Redis
companies = ["Tesla", "OpenAI", "Stripe"]

print("="*60)
print("CHECKING YUTORI TASKS")
print("="*60)

async def check_task_status(task_id):
    """Check Yutori task status"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"https://api.yutori.com/v1/research/tasks/{task_id}",
                headers={"X-API-Key": yutori_key}
            )
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        return {"error": str(e)}
    return None

async def main():
    for company in companies:
        name_hash = hashlib.md5(company.lower().encode()).hexdigest()
        task_key = f"yutori:task:{name_hash}:{company.lower().replace(' ', '_')}"
        cache_key = f"yutori:research:{name_hash}:{company.lower().replace(' ', '_')}"
        
        print(f"\n{company}:")
        print("-" * 40)
        
        # Check if cached
        cached = r.get(cache_key)
        if cached:
            data = json.loads(cached)
            print(f"  ✅ CACHED (research complete)")
            print(f"     Founded: {data.get('founded_year', 'N/A')}")
            print(f"     HQ: {data.get('headquarters', 'N/A')}")
        else:
            print(f"  ❌ NOT CACHED")
        
        # Check for pending task
        task_id = r.get(task_key)
        if task_id:
            print(f"  🔄 TASK RUNNING: {task_id}")
            
            # Check task status on Yutori
            status_data = await check_task_status(task_id)
            if status_data:
                status = status_data.get('status', 'unknown')
                print(f"     Status: {status}")
                if status == 'succeeded':
                    print(f"     ✅ Task completed! Should be cached soon.")
                elif status == 'failed':
                    print(f"     ❌ Task failed: {status_data.get('error', 'Unknown')}")
                elif status in ['running', 'queued']:
                    print(f"     ⏳ Still processing...")
        else:
            print(f"  ⭕ NO PENDING TASK")

asyncio.run(main())

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print("If tasks are 'succeeded' but not cached, background polling")
print("may have failed. Run update_tesla_cache.py to manually cache.")
