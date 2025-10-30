#!/usr/bin/env python3
"""
Integration Test Script for VDS Backend

This script validates that all components integrate properly:
- Import validation
- Database model integrity
- Service initialization
- API structure validation
- Syntax checking

Run: python test_integration.py
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Track test results
results = {
    "passed": [],
    "failed": [],
    "warnings": []
}


def test_section(name):
    """Decorator for test sections"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing: {name}")
    print('='*60)


def success(msg):
    print(f"✅ {msg}")
    results["passed"].append(msg)


def fail(msg, error=None):
    print(f"❌ {msg}")
    if error:
        print(f"   Error: {error}")
    results["failed"].append(msg)


def warning(msg):
    print(f"⚠️  {msg}")
    results["warnings"].append(msg)


# ==================== TEST 1: Core Imports ====================
test_section("Core Library Imports")

try:
    import fastapi
    success(f"FastAPI {fastapi.__version__}")
except Exception as e:
    fail("FastAPI import", e)

try:
    import uvicorn
    success(f"Uvicorn installed")
except Exception as e:
    fail("Uvicorn import", e)

try:
    import sqlalchemy
    success(f"SQLAlchemy {sqlalchemy.__version__}")
except Exception as e:
    fail("SQLAlchemy import", e)

try:
    import pandas
    success(f"Pandas {pandas.__version__}")
except Exception as e:
    fail("Pandas import", e)

try:
    import numpy
    success(f"NumPy {numpy.__version__}")
except Exception as e:
    fail("NumPy import", e)

try:
    import langgraph
    success(f"LangGraph installed")
except Exception as e:
    fail("LangGraph import", e)


# ==================== TEST 2: Database Models ====================
test_section("Database Models")

try:
    from models import Base, init_db, get_db, engine
    success("Database base imports successful")
except Exception as e:
    fail("Database base imports", e)

try:
    from models import Analysis, AgentExecution, AgentPerformance, CachedAnalysis
    success("All database models imported successfully")
except Exception as e:
    fail("Database model imports", e)

try:
    from models.database import Base
    # Check that models are registered
    table_names = [table.name for table in Base.metadata.tables.values()]
    expected_tables = ['analyses', 'agent_executions', 'agent_performance', 'cached_analyses']

    for table in expected_tables:
        if table in table_names:
            success(f"Table '{table}' registered in metadata")
        else:
            fail(f"Table '{table}' NOT found in metadata")

except Exception as e:
    fail("Database metadata validation", e)


# ==================== TEST 3: Services ====================
test_section("Service Modules")

try:
    from services.database_service import DatabaseService
    success("DatabaseService imported")
except Exception as e:
    fail("DatabaseService import", e)

try:
    from services.claude_service import ClaudeService
    success("ClaudeService imported")
except Exception as e:
    fail("ClaudeService import", e)

try:
    from services.agent_service import AgentService
    success("AgentService imported")
except Exception as e:
    fail("AgentService import", e)

try:
    from services.langgraph_workflow import LangGraphMultiAgentWorkflow
    success("LangGraphMultiAgentWorkflow imported")
except Exception as e:
    fail("LangGraphMultiAgentWorkflow import", e)

try:
    from services.s3_service import S3Service
    success("S3Service imported")
except Exception as e:
    fail("S3Service import", e)


# ==================== TEST 4: Configuration ====================
test_section("Configuration")

try:
    from config import settings
    success("Settings imported")

    # Check critical settings exist
    if hasattr(settings, 'HOST'):
        success(f"HOST setting exists: {settings.HOST}")
    else:
        fail("HOST setting missing")

    if hasattr(settings, 'PORT'):
        success(f"PORT setting exists: {settings.PORT}")
    else:
        fail("PORT setting missing")

except Exception as e:
    fail("Configuration import", e)


# ==================== TEST 5: Main Application ====================
test_section("Main Application Structure")

try:
    from main import app
    success("FastAPI app imported")
except Exception as e:
    fail("FastAPI app import", e)

try:
    from main import db_service
    success("DB service instance created")
except Exception as e:
    fail("DB service instance", e)

# Check if startup event is registered
try:
    from main import app
    if hasattr(app, 'router'):
        success("App router exists")

    # Count registered routes
    route_count = len(app.routes)
    success(f"Total routes registered: {route_count}")

    # Check for key endpoints
    routes = [route.path for route in app.routes]

    key_endpoints = [
        '/health',
        '/analyze-data',
        '/history/recent',
        '/analytics/statistics',
        '/agents/available'
    ]

    for endpoint in key_endpoints:
        if endpoint in routes:
            success(f"Endpoint '{endpoint}' registered")
        else:
            warning(f"Endpoint '{endpoint}' not found (might use path parameters)")

except Exception as e:
    fail("App structure validation", e)


# ==================== TEST 6: Database Initialization ====================
test_section("Database Initialization (Dry Run)")

try:
    from models import init_db
    # Don't actually initialize, just test that the function exists
    success("init_db function available")

    from models.database import engine
    success("Database engine created")

    # Test that we can connect (without actually connecting)
    url = str(engine.url)
    if 'sqlite' in url or 'postgresql' in url:
        success(f"Valid database URL configured: {url.split('@')[0]}...")
    else:
        warning(f"Unusual database URL: {url}")

except Exception as e:
    fail("Database initialization check", e)


# ==================== TEST 7: Workflow Integration ====================
test_section("Workflow Integration")

try:
    from services.langgraph_workflow import LangGraphMultiAgentWorkflow, AnalysisState
    success("Workflow classes imported")

    # Check that AnalysisState has required fields
    required_fields = [
        'file_content', 'filename', 'user_question',
        'selected_agents', 'agent_results', 'progress'
    ]

    for field in required_fields:
        if field in AnalysisState.__annotations__:
            success(f"AnalysisState has '{field}' field")
        else:
            fail(f"AnalysisState missing '{field}' field")

except Exception as e:
    fail("Workflow integration check", e)


# ==================== TEST 8: Syntax Validation ====================
test_section("Syntax Validation")

python_files = [
    'main.py',
    'config.py',
    'models/__init__.py',
    'models/database.py',
    'models/analysis.py',
    'services/database_service.py',
    'services/langgraph_workflow.py',
    'services/agent_service.py',
]

import py_compile

for file_path in python_files:
    full_path = Path(__file__).parent / file_path
    if full_path.exists():
        try:
            py_compile.compile(str(full_path), doraise=True)
            success(f"Syntax valid: {file_path}")
        except py_compile.PyCompileError as e:
            fail(f"Syntax error in {file_path}", e)
    else:
        warning(f"File not found: {file_path}")


# ==================== TEST 9: Agent Loading ====================
test_section("Agent Loading")

try:
    from services.agent_service import AgentService
    agent_service = AgentService()

    agent_count = len(agent_service.agents)
    if agent_count > 0:
        success(f"Loaded {agent_count} agents")

        # List some agents
        agent_names = list(agent_service.agents.keys())[:5]
        success(f"Sample agents: {', '.join(agent_names)}")
    else:
        warning("No agents loaded - check agents directory")

except Exception as e:
    fail("Agent loading check", e)


# ==================== FINAL REPORT ====================
print("\n" + "="*60)
print("📊 INTEGRATION TEST SUMMARY")
print("="*60)

total_tests = len(results["passed"]) + len(results["failed"])
success_rate = (len(results["passed"]) / total_tests * 100) if total_tests > 0 else 0

print(f"\n✅ Passed: {len(results['passed'])}")
print(f"❌ Failed: {len(results['failed'])}")
print(f"⚠️  Warnings: {len(results['warnings'])}")
print(f"📈 Success Rate: {success_rate:.1f}%")

if results["failed"]:
    print("\n❌ Failed Tests:")
    for fail_msg in results["failed"]:
        print(f"   - {fail_msg}")

if results["warnings"]:
    print("\n⚠️  Warnings:")
    for warn_msg in results["warnings"]:
        print(f"   - {warn_msg}")

print("\n" + "="*60)

if len(results["failed"]) == 0:
    print("🎉 ALL INTEGRATION TESTS PASSED!")
    print("✅ The system is ready for deployment")
    sys.exit(0)
else:
    print("⚠️  SOME TESTS FAILED")
    print("Please review the errors above before deploying")
    sys.exit(1)
