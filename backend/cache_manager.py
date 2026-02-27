#!/usr/bin/env python3
"""
Redis Cache Manager for CompanyIntel

Usage:
    python cache_manager.py list              # List all cached keys
    python cache_manager.py get <key>         # Get value for a key
    python cache_manager.py delete <key>      # Delete a key
    python cache_manager.py clear <pattern>   # Clear keys matching pattern
    python cache_manager.py stats             # Show cache statistics
"""

import asyncio
import sys
import json
from app.core.cache import redis_cache
from app.config import settings
import redis.asyncio as redis

async def list_keys(pattern="*"):
    """List all keys matching pattern"""
    await redis_cache.connect()
    try:
        keys = []
        async for key in redis_cache.client.scan_iter(match=pattern):
            ttl = await redis_cache.client.ttl(key)
            keys.append({"key": key, "ttl": ttl})
        
        print(f"\n📦 Found {len(keys)} keys matching '{pattern}':\n")
        for item in sorted(keys, key=lambda x: x['key']):
            ttl_str = f"{item['ttl']}s" if item['ttl'] > 0 else "no expiry"
            print(f"  • {item['key']} (TTL: {ttl_str})")
        print()
    finally:
        await redis_cache.close()

async def get_key(key):
    """Get value for a specific key"""
    await redis_cache.connect()
    try:
        value = await redis_cache.get(key)
        if value:
            print(f"\n✓ Value for '{key}':\n")
            print(json.dumps(value, indent=2))
            print()
        else:
            print(f"\n✗ Key '{key}' not found\n")
    finally:
        await redis_cache.close()

async def delete_key(key):
    """Delete a specific key"""
    await redis_cache.connect()
    try:
        await redis_cache.delete(key)
        print(f"\n✓ Deleted key: {key}\n")
    finally:
        await redis_cache.close()

async def clear_pattern(pattern):
    """Clear all keys matching pattern"""
    await redis_cache.connect()
    try:
        keys = []
        async for key in redis_cache.client.scan_iter(match=pattern):
            keys.append(key)
        
        if keys:
            await redis_cache.client.delete(*keys)
            print(f"\n✓ Deleted {len(keys)} keys matching '{pattern}'\n")
        else:
            print(f"\n✗ No keys found matching '{pattern}'\n")
    finally:
        await redis_cache.close()

async def show_stats():
    """Show cache statistics"""
    await redis_cache.connect()
    try:
        # Count keys by type
        yutori_research = 0
        yutori_browsing = 0
        tavily_competitors = 0
        sentiment_news = 0
        company_data = 0
        progress_data = 0
        other = 0
        
        async for key in redis_cache.client.scan_iter(match="*"):
            if key.startswith("yutori:research:"):
                yutori_research += 1
            elif key.startswith("yutori:browsing:"):
                yutori_browsing += 1
            elif key.startswith("tavily:competitors:"):
                tavily_competitors += 1
            elif key.startswith("sentiment:news:"):
                sentiment_news += 1
            elif key.startswith("company:"):
                company_data += 1
            elif key.startswith("progress:"):
                progress_data += 1
            else:
                other += 1
        
        total = yutori_research + yutori_browsing + tavily_competitors + sentiment_news + company_data + progress_data + other
        
        print("\n📊 Cache Statistics:\n")
        print(f"  Total Keys: {total}")
        print(f"\n  By Type:")
        print(f"    • Yutori Research:    {yutori_research} (TTL: 7 days)")
        print(f"    • Yutori Browsing:    {yutori_browsing} (TTL: 7 days)")
        print(f"    • Tavily Competitors: {tavily_competitors} (TTL: 3 days)")
        print(f"    • Sentiment/News:     {sentiment_news} (TTL: 6 hours)")
        print(f"    • Company Data:       {company_data}")
        print(f"    • Progress Data:      {progress_data} (TTL: 5 min)")
        print(f"    • Other:              {other}")
        print()
        
        # Memory info
        info = await redis_cache.client.info("memory")
        used_memory = info.get("used_memory_human", "unknown")
        print(f"  Memory Used: {used_memory}")
        print()
    finally:
        await redis_cache.close()

def print_usage():
    """Print usage information"""
    print(__doc__)

async def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1].lower()
    
    if command == "list":
        pattern = sys.argv[2] if len(sys.argv) > 2 else "*"
        await list_keys(pattern)
    
    elif command == "get":
        if len(sys.argv) < 3:
            print("\n✗ Error: Please provide a key\n")
            print("Usage: python cache_manager.py get <key>\n")
            return
        await get_key(sys.argv[2])
    
    elif command == "delete":
        if len(sys.argv) < 3:
            print("\n✗ Error: Please provide a key\n")
            print("Usage: python cache_manager.py delete <key>\n")
            return
        await delete_key(sys.argv[2])
    
    elif command == "clear":
        if len(sys.argv) < 3:
            print("\n✗ Error: Please provide a pattern\n")
            print("Usage: python cache_manager.py clear <pattern>\n")
            print("Examples:")
            print("  python cache_manager.py clear 'yutori:*'")
            print("  python cache_manager.py clear 'sentiment:*'")
            print()
            return
        pattern = sys.argv[2]
        confirm = input(f"⚠️  Are you sure you want to delete all keys matching '{pattern}'? (yes/no): ")
        if confirm.lower() == "yes":
            await clear_pattern(pattern)
        else:
            print("\n✗ Cancelled\n")
    
    elif command == "stats":
        await show_stats()
    
    else:
        print(f"\n✗ Unknown command: {command}\n")
        print_usage()

if __name__ == "__main__":
    asyncio.run(main())
