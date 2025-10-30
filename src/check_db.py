#!/usr/bin/env python3
"""Quick script to check database contents"""

import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / "vds_data.db"

if not db_path.exists():
    print("❌ Database not found at:", db_path)
    exit(1)

conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

print("=" * 80)
print("DATABASE CHECK")
print("=" * 80)

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"\nTables found: {len(tables)}")
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"  - {table}: {count} rows")

# Check Analyses
print("\n" + "=" * 80)
print("ANALYSES (Recent 10)")
print("=" * 80)
cursor.execute("""
    SELECT id, filename, status, user_question, 
           created_at, execution_time_ms, is_cached
    FROM analyses 
    ORDER BY created_at DESC 
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"ID: {row[0][:8]}...")
    print(f"  File: {row[1]}")
    print(f"  Status: {row[2]}")
    q_text = row[3][:50] + "..." if len(row[3]) > 50 else row[3]
    print(f"  Question: {q_text}")
    print(f"  Time: {row[5] or 0}ms | Cached: {row[6]}")
    print(f"  Created: {row[4]}")
    print()

# Check Agent Executions
print("=" * 80)
print("AGENT EXECUTIONS (Recent 10)")
print("=" * 80)
cursor.execute("""
    SELECT agent_name, success, execution_time_ms, 
           started_at, error
    FROM agent_executions 
    ORDER BY started_at DESC 
    LIMIT 10
""")
for row in cursor.fetchall():
    status = "[OK]" if row[1] else "[FAIL]"
    print(f"{status} {row[0]}: {row[2] or 0}ms | {row[3]}")
    if row[4]:
        print(f"   Error: {row[4][:100]}...")

# Check Agent Performance
print("\n" + "=" * 80)
print("AGENT PERFORMANCE")
print("=" * 80)
cursor.execute("""
    SELECT agent_name, total_runs, success_rate, 
           avg_execution_time_ms, min_execution_time_ms, max_execution_time_ms
    FROM agent_performance 
    ORDER BY total_runs DESC
""")
for row in cursor.fetchall():
    success_pct = f"{row[2] * 100:.1f}" if row[2] else "N/A"
    print(f"{row[0]}:")
    print(f"  Runs: {row[1]} | Success Rate: {success_pct}%")
    print(f"  Avg: {row[3] or 0}ms | Min: {row[4] or 0}ms | Max: {row[5] or 0}ms")
    print()

# Check Cache
print("=" * 80)
print("CACHE ENTRIES (Recent 10)")
print("=" * 80)
cursor.execute("""
    SELECT cache_key, access_count, time_saved_ms, 
           created_at, expires_at
    FROM cached_analyses 
    ORDER BY created_at DESC 
    LIMIT 10
""")
for row in cursor.fetchall():
    print(f"Key: {row[0][:16]}...")
    print(f"  Hits: {row[1]} | Time Saved: {row[2] or 0}ms")
    print(f"  Created: {row[3]}")
    print(f"  Expires: {row[4]}")
    print()

conn.close()
print("=" * 80)
print("Done!")
print("=" * 80)

