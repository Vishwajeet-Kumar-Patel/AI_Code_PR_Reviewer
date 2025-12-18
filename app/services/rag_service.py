import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
from pathlib import Path
import hashlib
from sentence_transformers import SentenceTransformer
from app.core.config import settings
from app.core.logging import logger
from app.models.code_analysis import RAGContext


class RAGService:
    """Retrieval Augmented Generation service using vector embeddings"""
    
    def __init__(self):
        """Initialize RAG service"""
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        
        # Initialize ChromaDB
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY,
                anonymized_telemetry=False,
            )
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=settings.VECTOR_DB_COLLECTION
            )
            logger.info(f"Loaded existing collection: {settings.VECTOR_DB_COLLECTION}")
        except Exception:
            self.collection = self.client.create_collection(
                name=settings.VECTOR_DB_COLLECTION,
                metadata={"description": "Code best practices and patterns"}
            )
            logger.info(f"Created new collection: {settings.VECTOR_DB_COLLECTION}")
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def _generate_doc_id(self, content: str, metadata: Dict[str, Any]) -> str:
        """Generate unique document ID"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        category = metadata.get("category", "general")
        language = metadata.get("language", "general")
        return f"{language}_{category}_{content_hash[:8]}"
    
    def add_document(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """Add a document to the vector database"""
        if metadata is None:
            metadata = {}
        
        if doc_id is None:
            doc_id = self._generate_doc_id(content, metadata)
        
        embedding = self._generate_embedding(content)
        
        try:
            self.collection.add(
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            logger.info(f"Added document: {doc_id}")
            return doc_id
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    def add_documents_batch(
        self,
        contents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        doc_ids: Optional[List[str]] = None,
    ) -> List[str]:
        """Add multiple documents in batch"""
        if metadatas is None:
            metadatas = [{}] * len(contents)
        
        if doc_ids is None:
            doc_ids = [
                self._generate_doc_id(content, metadata)
                for content, metadata in zip(contents, metadatas)
            ]
        
        embeddings = [self._generate_embedding(content) for content in contents]
        
        try:
            self.collection.add(
                embeddings=embeddings,
                documents=contents,
                metadatas=metadatas,
                ids=doc_ids
            )
            logger.info(f"Added {len(contents)} documents in batch")
            return doc_ids
        except Exception as e:
            logger.error(f"Failed to add documents in batch: {e}")
            raise
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None,
    ) -> RAGContext:
        """Search for relevant documents"""
        query_embedding = self._generate_embedding(query)
        
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata,
            )
            
            # Process results
            documents = []
            best_practices = []
            examples = []
            
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    distance = results["distances"][0][i] if results["distances"] else 0
                    
                    doc_info = {
                        "content": doc,
                        "metadata": metadata,
                        "distance": distance,
                        "score": 1 - distance,  # Convert distance to similarity score
                    }
                    documents.append(doc_info)
                    
                    # Categorize based on metadata
                    category = metadata.get("category", "")
                    if category == "best_practice":
                        best_practices.append(doc)
                    elif category == "example":
                        examples.append(doc)
            
            # Calculate confidence based on top result
            confidence = documents[0]["score"] if documents else 0.0
            
            return RAGContext(
                query=query,
                relevant_documents=documents,
                best_practices=best_practices,
                examples=examples,
                confidence_score=confidence,
            )
        except Exception as e:
            logger.error(f"Failed to search documents: {e}")
            return RAGContext(
                query=query,
                relevant_documents=[],
                best_practices=[],
                examples=[],
                confidence_score=0.0,
            )
    
    def search_by_language(
        self,
        query: str,
        language: str,
        n_results: int = 5,
    ) -> RAGContext:
        """Search for documents filtered by programming language"""
        return self.search(
            query=query,
            n_results=n_results,
            filter_metadata={"language": language}
        )
    
    def search_by_category(
        self,
        query: str,
        category: str,
        n_results: int = 5,
    ) -> RAGContext:
        """Search for documents filtered by category"""
        return self.search(
            query=query,
            n_results=n_results,
            filter_metadata={"category": category}
        )
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from the collection"""
        try:
            self.collection.delete(ids=[doc_id])
            logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection"""
        try:
            self.client.delete_collection(name=settings.VECTOR_DB_COLLECTION)
            self.collection = self.client.create_collection(
                name=settings.VECTOR_DB_COLLECTION,
                metadata={"description": "Code best practices and patterns"}
            )
            logger.info("Cleared collection")
            return True
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            return {
                "name": settings.VECTOR_DB_COLLECTION,
                "document_count": count,
                "embedding_model": settings.EMBEDDING_MODEL,
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    def load_knowledge_base(self, kb_path: Optional[Path] = None) -> int:
        """Load knowledge base from markdown files"""
        if kb_path is None:
            kb_path = Path(settings.KNOWLEDGE_BASE_PATH)
        
        if not kb_path.exists():
            logger.warning(f"Knowledge base path does not exist: {kb_path}")
            return 0
        
        count = 0
        for md_file in kb_path.rglob("*.md"):
            try:
                content = md_file.read_text(encoding="utf-8")
                
                # Extract metadata from file path
                language = md_file.stem
                category = md_file.parent.name
                
                # Split content into sections
                sections = self._split_content(content)
                
                metadatas = [
                    {
                        "language": language,
                        "category": category,
                        "source": str(md_file),
                        "section": i,
                    }
                    for i in range(len(sections))
                ]
                
                self.add_documents_batch(sections, metadatas)
                count += len(sections)
                logger.info(f"Loaded {len(sections)} sections from {md_file}")
            except Exception as e:
                logger.error(f"Failed to load {md_file}: {e}")
        
        logger.info(f"Loaded {count} documents from knowledge base")
        return count
    
    def _split_content(self, content: str, max_length: int = 1000) -> List[str]:
        """Split content into smaller sections"""
        # Split by headers or paragraphs
        sections = []
        current_section = []
        current_length = 0
        
        for line in content.split("\n"):
            line_length = len(line)
            
            # Start new section on header or when max length reached
            if (line.startswith("#") or current_length + line_length > max_length) and current_section:
                sections.append("\n".join(current_section))
                current_section = []
                current_length = 0
            
            current_section.append(line)
            current_length += line_length
        
        if current_section:
            sections.append("\n".join(current_section))
        
        return [s.strip() for s in sections if s.strip()]
