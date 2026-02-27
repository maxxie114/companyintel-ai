#!/usr/bin/env python3
"""Update Tesla cache with real Yutori data"""

import redis
import json
import hashlib
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('backend/.env')
redis_url = os.getenv('REDIS_URL')

print(f"Connecting to Redis...")
r = redis.from_url(redis_url, decode_responses=True)
r.ping()
print("✓ Connected!\n")

# Generate cache key for Tesla
company_name = "Tesla"
name_hash = hashlib.md5(company_name.lower().encode()).hexdigest()
cache_key = f"yutori:research:{name_hash}:{company_name.lower().replace(' ', '_')}"

# Real Tesla data from completed Yutori task (655f085d-7294-43ee-8655-76752e0efffb)
tesla_data = {
    "name": "Tesla",
    "slug": "tesla",
    "description": "Tesla, Inc. designs, manufactures, and sells electric vehicles, battery energy storage systems, solar panels, and related products and services. It operates in two segments: Automotive and Energy Generation & Storage, and is widely recognized in the transition to sustainable energy.",
    "founded_year": 2003,
    "headquarters": "Austin, Texas",
    "employee_count": "134,785",
    "website": "https://www.tesla.com",
    "logo_url": "https://logo.clearbit.com/tesla.com",
    "industry": ["Consumer Cyclical", "Auto Manufacturers"],
    "mission": "Building a world of amazing abundance",
    "status": "public",
    "raw_content": "<h3>Tesla: Public EV and Energy Leader</h3>\n<p><b>Company description:</b> Tesla, Inc. designs, manufactures, and sells electric vehicles, battery energy storage systems, solar panels, and related products and services. It operates in two segments: Automotive and Energy Generation & Storage, and is widely recognized in the transition to sustainable energy.</p>\n<p><b>Founding year:</b> 2003.</p>\n<p><b>Headquarters:</b> Austin, Texas — 1 Tesla Road, Austin, Texas 78725 (relocated from Palo Alto, California in 2021).</p>\n<p><b>Employee count:</b> 134,785 (as of December 31, 2025).</p>\n<p><b>Mission:</b> \"Building a world of amazing abundance\" (previously \"Accelerating the world's transition to sustainable energy\").</p>\n<p><b>Industry:</b> Consumer Cyclical / Auto Manufacturers.</p>\n<p><b>Official website:</b> https://www.tesla.com/</p>\n<p><b>Status:</b> Publicly traded — listed on NASDAQ under ticker symbol TSLA; IPO on June 29, 2010.</p>"
}

# Update cache (7 days TTL)
r.setex(cache_key, 86400 * 7, json.dumps(tesla_data))

print("✅ Updated Tesla cache with real Yutori data!")
print(f"   Key: {cache_key}")
print(f"   Name: {tesla_data['name']}")
print(f"   Founded: {tesla_data['founded_year']}")
print(f"   HQ: {tesla_data['headquarters']}")
print(f"   Employees: {tesla_data['employee_count']}")
print(f"   Status: {tesla_data['status']}")
print(f"   TTL: 7 days\n")

# Verify
cached = r.get(cache_key)
if cached:
    data = json.loads(cached)
    print("✓ Verified: Cache updated successfully!")
    print(f"  Description: {data['description'][:100]}...")
