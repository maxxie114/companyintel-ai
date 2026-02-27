#!/usr/bin/env python3
"""Test and populate Redis cache with Tesla data from completed Yutori task"""

import redis
import json
import hashlib
import os
from dotenv import load_dotenv

# Load environment
load_dotenv('backend/.env')
redis_url = os.getenv('REDIS_URL')

print(f"Connecting to Redis: {redis_url[:40]}...")
r = redis.from_url(redis_url, decode_responses=True)

# Test connection
r.ping()
print("✓ Redis connected!\n")

# Generate cache key for Tesla
company_name = "Tesla"
name_hash = hashlib.md5(company_name.lower().encode()).hexdigest()
cache_key = f"yutori:research:{name_hash}:{company_name.lower().replace(' ', '_')}"
task_key = f"yutori:task:{name_hash}:{company_name.lower().replace(' ', '_')}"

print(f"Cache key: {cache_key}")
print(f"Task key: {task_key}\n")

# Check if already cached
cached = r.get(cache_key)
if cached:
    print("✓ Tesla data IS cached!")
    data = json.loads(cached)
    print(f"  Name: {data['name']}")
    print(f"  Founded: {data.get('founded_year', 'N/A')}")
    print(f"  HQ: {data.get('headquarters', 'N/A')}")
    print(f"  Employees: {data.get('employee_count', 'N/A')}")
else:
    print("✗ Tesla data NOT cached yet")
    
    # Check if there's a pending task
    task_id = r.get(task_key)
    if task_id:
        print(f"  Pending task ID: {task_id}")
        print("  Background polling may still be running...")
    else:
        print("  No pending task found")
        print("\n  Manually caching Tesla data from completed Yutori task...")
        
        # Tesla data from the Yutori task we know completed
        tesla_data = {
            "name": "Tesla",
            "slug": "tesla",
            "description": "Tesla, Inc. designs, manufactures, and sells electric vehicles, battery energy storage systems, solar panels, and related products and services. It operates in two segments: Automotive and Energy Generation & Storage.",
            "founded_year": 2003,
            "headquarters": "Austin, Texas",
            "employee_count": "134,785",
            "website": "https://www.tesla.com",
            "logo_url": "https://logo.clearbit.com/tesla.com",
            "industry": ["Consumer Cyclical", "Auto Manufacturers"],
            "mission": "Building a world of amazing abundance",
            "status": "public",
            "raw_content": "Tesla, Inc. designs, manufactures, and sells electric vehicles..."
        }
        
        # Cache it (7 days)
        r.setex(cache_key, 86400 * 7, json.dumps(tesla_data))
        print("  ✓ Tesla data cached successfully!")
        print(f"  TTL: 7 days")

print("\n" + "="*50)
print("Now test with: curl http://localhost:8000/api/analyze \\")
print('  -H "Content-Type: application/json" \\')
print('  -d \'{"company_name":"Tesla","options":{...}}\'')
print("="*50)
