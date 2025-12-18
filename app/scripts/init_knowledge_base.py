#!/usr/bin/env python
"""
Script to initialize the knowledge base by loading best practices into the vector database.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.services.rag_service import RAGService
from app.core.logging import logger
from app.core.config import settings


def main():
    """Initialize knowledge base"""
    logger.info("Starting knowledge base initialization")
    
    try:
        # Initialize RAG service
        rag_service = RAGService()
        
        # Get stats before loading
        stats_before = rag_service.get_collection_stats()
        logger.info(f"Documents before: {stats_before.get('document_count', 0)}")
        
        # Load knowledge base
        kb_path = Path(settings.KNOWLEDGE_BASE_PATH)
        if not kb_path.exists():
            logger.error(f"Knowledge base path does not exist: {kb_path}")
            return 1
        
        logger.info(f"Loading knowledge base from: {kb_path}")
        count = rag_service.load_knowledge_base(kb_path)
        
        # Get stats after loading
        stats_after = rag_service.get_collection_stats()
        logger.info(f"Documents after: {stats_after.get('document_count', 0)}")
        logger.info(f"Successfully loaded {count} documents")
        
        # Test search
        logger.info("\nTesting search functionality...")
        test_queries = [
            ("Python best practices", "python"),
            ("JavaScript security", "javascript"),
            ("SQL injection", "security"),
        ]
        
        for query, language in test_queries:
            result = rag_service.search_by_language(query, language, n_results=2)
            logger.info(f"\nQuery: '{query}' (language: {language})")
            logger.info(f"Found {len(result.relevant_documents)} documents")
            logger.info(f"Confidence: {result.confidence_score:.2f}")
            
            if result.relevant_documents:
                doc = result.relevant_documents[0]
                preview = doc['content'][:150] + "..."
                logger.info(f"Top result preview: {preview}")
        
        logger.info("\nKnowledge base initialization complete!")
        return 0
        
    except Exception as e:
        logger.error(f"Failed to initialize knowledge base: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
