"""
Initialize the database with tables and initial data
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.db import init_db
from app.core.logging import logger


def main():
    """Initialize database"""
    try:
        logger.info("Starting database initialization...")
        
        # Create all tables
        init_db()
        
        logger.info("Database tables created successfully!")
        logger.info("Tables: users, repositories, pull_requests, reviews, feedback")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
