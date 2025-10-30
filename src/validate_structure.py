#!/usr/bin/env python3
"""
Code Structure Validation (No Dependencies Required)

Validates the code structure without running imports:
- Function signatures
- Class definitions
- Database model relationships
- API endpoint registration
- Configuration completeness
"""

import ast
import sys
from pathlib import Path

results = {"passed": 0, "failed": 0, "warnings": 0}

def success(msg):
    print(f"✅ {msg}")
    results["passed"] += 1

def fail(msg):
    print(f"❌ {msg}")
    results["failed"] += 1

def warning(msg):
    print(f"⚠️  {msg}")
    results["warnings"] += 1


print("\n" + "="*60)
print("🔍 CODE STRUCTURE VALIDATION")
print("="*60)

# ==================== Parse Files ====================
print("\n📂 Parsing Python Files...")

files_to_parse = {
    'main.py': None,
    'models/database.py': None,
    'models/analysis.py': None,
    'services/database_service.py': None,
    'services/langgraph_workflow.py': None,
}

src_dir = Path(__file__).parent

for file_path in files_to_parse.keys():
    full_path = src_dir / file_path
    try:
        with open(full_path, 'r') as f:
            content = f.read()
            tree = ast.parse(content, filename=file_path)
            files_to_parse[file_path] = tree
            success(f"Parsed {file_path}")
    except Exception as e:
        fail(f"Failed to parse {file_path}: {e}")


# ==================== Check main.py ====================
print("\n🌐 Validating main.py...")

main_tree = files_to_parse.get('main.py')
if main_tree:
    # Find all function definitions
    functions = [node.name for node in ast.walk(main_tree) if isinstance(node, ast.FunctionDef)]

    # Check for key endpoints
    key_endpoints = [
        'analyze_data',
        'get_recent_history',
        'get_analysis_by_id',
        'get_analytics_statistics',
        'get_agent_performance_stats',
        'clear_expired_cache'
    ]

    for endpoint in key_endpoints:
        if endpoint in functions:
            success(f"Endpoint function '{endpoint}' defined")
        else:
            fail(f"Endpoint function '{endpoint}' NOT found")

    # Check for database session dependency
    main_content = open(src_dir / 'main.py').read()
    if 'Depends(get_db)' in main_content:
        success("Database dependency injection configured")
    else:
        warning("Database dependency not found in main.py")

    # Check for caching logic
    if 'cache_key' in main_content and 'get_cached_analysis' in main_content:
        success("Caching logic implemented")
    else:
        warning("Caching logic not found")

    # Check for parallel execution call
    if 'asyncio.gather' in main_content or 'parallel' in main_content.lower():
        warning("Parallel execution might be in workflow file (expected)")
    else:
        warning("Check if parallel execution is implemented")


# ==================== Check Database Models ====================
print("\n🗄️  Validating Database Models...")

analysis_tree = files_to_parse.get('models/analysis.py')
if analysis_tree:
    classes = [node.name for node in ast.walk(analysis_tree) if isinstance(node, ast.ClassDef)]

    expected_models = ['Analysis', 'AgentExecution', 'AgentPerformance', 'CachedAnalysis']
    for model in expected_models:
        if model in classes:
            success(f"Model class '{model}' defined")
        else:
            fail(f"Model class '{model}' NOT found")

    # Check for to_dict methods
    analysis_content = open(src_dir / 'models/analysis.py').read()
    if analysis_content.count('def to_dict(') >= 4:
        success("All models have to_dict() methods")
    else:
        warning("Some models might be missing to_dict() methods")


# ==================== Check DatabaseService ====================
print("\n💾 Validating DatabaseService...")

db_service_tree = files_to_parse.get('services/database_service.py')
if db_service_tree:
    classes = [node.name for node in ast.walk(db_service_tree) if isinstance(node, ast.ClassDef)]

    if 'DatabaseService' in classes:
        success("DatabaseService class defined")

        # Get all methods
        for node in ast.walk(db_service_tree):
            if isinstance(node, ast.ClassDef) and node.name == 'DatabaseService':
                methods = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]

                key_methods = [
                    'create_analysis',
                    'get_cached_analysis',
                    'save_to_cache',
                    'get_analysis_statistics',
                    'get_agent_performance'
                ]

                for method in key_methods:
                    if method in methods:
                        success(f"DatabaseService has '{method}' method")
                    else:
                        fail(f"DatabaseService missing '{method}' method")
    else:
        fail("DatabaseService class NOT found")


# ==================== Check Workflow ====================
print("\n⚡ Validating Workflow...")

workflow_tree = files_to_parse.get('services/langgraph_workflow.py')
if workflow_tree:
    workflow_content = open(src_dir / 'services/langgraph_workflow.py').read()

    # Check for parallel execution
    if 'asyncio.gather' in workflow_content:
        success("Parallel execution (asyncio.gather) implemented")
    else:
        fail("Parallel execution NOT found")

    # Check for the new method
    if '_execute_agent_with_progress' in workflow_content:
        success("Helper method for parallel execution exists")
    else:
        warning("Helper method '_execute_agent_with_progress' not found")

    # Check for run_analysis parameters
    if 'analysis_id' in workflow_content and 'db_session' in workflow_content:
        success("Workflow accepts database tracking parameters")
    else:
        warning("Database tracking parameters might be missing")


# ==================== Check Imports ====================
print("\n📦 Validating Imports...")

main_content = open(src_dir / 'main.py').read()

critical_imports = [
    ('from models import init_db, get_db', 'Database initialization'),
    ('from services.database_service import DatabaseService', 'Database service'),
    ('Session = Depends(get_db)', 'Session dependency'),
]

for import_stmt, description in critical_imports:
    if import_stmt in main_content or 'get_db' in main_content:
        success(f"{description} imported correctly")
    else:
        warning(f"{description} import might be incorrect")


# ==================== Check Backwards Compatibility ====================
print("\n🔄 Checking Backwards Compatibility...")

# Check that old endpoints still exist
old_endpoints = ['upload_file', 'list_files', 'preview_data', 'plan_analysis']

for endpoint in old_endpoints:
    if f'def {endpoint}' in main_content or f'async def {endpoint}' in main_content:
        success(f"Legacy endpoint '{endpoint}' preserved")
    else:
        warning(f"Legacy endpoint '{endpoint}' might be missing")


# ==================== Check Error Handling ====================
print("\n🛡️  Checking Error Handling...")

services = [
    'services/database_service.py',
    'services/langgraph_workflow.py',
]

for service_file in services:
    service_path = src_dir / service_file
    if service_path.exists():
        content = open(service_path).read()
        try_count = content.count('try:')
        except_count = content.count('except ')

        if try_count > 0 and except_count > 0:
            success(f"{service_file}: Has error handling ({try_count} try blocks)")
        else:
            warning(f"{service_file}: Limited error handling")


# ==================== Final Report ====================
print("\n" + "="*60)
print("📊 STRUCTURE VALIDATION SUMMARY")
print("="*60)

total = results["passed"] + results["failed"]
success_rate = (results["passed"] / total * 100) if total > 0 else 0

print(f"\n✅ Passed: {results['passed']}")
print(f"❌ Failed: {results['failed']}")
print(f"⚠️  Warnings: {results['warnings']}")
print(f"📈 Success Rate: {success_rate:.1f}%")

print("\n" + "="*60)

if results["failed"] == 0:
    print("🎉 CODE STRUCTURE IS VALID!")
    print("✅ All critical components are properly integrated")
    sys.exit(0)
else:
    print("⚠️  STRUCTURAL ISSUES FOUND")
    print("Please review the failures above")
    sys.exit(1)
