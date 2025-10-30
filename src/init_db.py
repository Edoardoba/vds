#!/usr/bin/env python3
"""
Database initialization script

This script initializes the database schema for the VDS application.
Run this before starting the application for the first time.

Usage:
    python init_db.py

Environment Variables:
    DATABASE_URL - Database connection string (default: sqlite:///./vds_data.db)
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from models import init_db, drop_all_tables, engine
from sqlalchemy import inspect

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_existing_tables():
    """Check if tables already exist"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return tables


def main():
    """Main initialization function"""
    logger.info("=" * 60)
    logger.info("VDS Database Initialization Script")
    logger.info("=" * 60)

    # Check existing tables
    existing_tables = check_existing_tables()

    if existing_tables:
        logger.warning(f"Found existing tables: {', '.join(existing_tables)}")
        response = input("\nDo you want to DROP all existing tables and recreate them? (yes/no): ")

        if response.lower() == 'yes':
            logger.warning("Dropping all existing tables...")
            drop_all_tables()
            logger.info("All tables dropped successfully")
        elif response.lower() == 'no':
            logger.info("Skipping table drop. Will create missing tables only.")
        else:
            logger.error("Invalid response. Exiting.")
            sys.exit(1)

    # Initialize database (create tables)
    logger.info("\nInitializing database...")
    try:
        init_db()
        logger.info("✅ Database initialized successfully!")

        # List created tables
        tables = check_existing_tables()
        logger.info(f"\nCreated tables: {', '.join(tables)}")

        logger.info("\n" + "=" * 60)
        logger.info("Database is ready to use!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
