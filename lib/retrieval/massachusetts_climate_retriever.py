import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid
from datetime import datetime
import logging

# LangChain imports
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import SupabaseVectorStore
from langchain.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.callbacks import get_openai_callback

# Supabase
from supabase.client import Client, create_client

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MassachusettsClimateConstraints(BaseModel):
    """Constraints for the Massachusetts Climate Economy Assistant"""
    geographic_focus: str = Field(
        default="Massachusetts", 
        description="The assistant should focus on information specific to Massachusetts"
    )
    
    allowed_topics: List[str] = Field(
        default=[
            "clean energy careers", 
            "renewable energy", 
            "energy efficiency", 
            "workforce development",
            "climate economy",
            "green jobs",
            "training programs",
            "environmental justice",
            "clean energy policy",
            "Massachusetts climate initiatives"
        ],
        description="Topics that the assistant is allowed to discuss"
    )
    
    prohibited_topics: List[str] = Field(
        default=[
            "climate change denial",
            "fossil fuel advocacy",
            "political endorsements",
            "non-Massachusetts specific programs",
            "personal financial advice",
            "medical advice"
        ],
        description="Topics that the assistant should not discuss"
    )
    
    source_requirements: Dict[str, Any] = Field(
        default={
            "require_massachusetts_source": True,
            "max_source_age_years": 3,
            "preferred_sources": [
                "MassCEC", 
                "Massachusetts government", 
                "NECEC",
                "Massachusetts educational institutions"
            ]
        },
        description="Requirements for sources of information"
    )
    
    response_requirements: Dict[str, Any] = Field(
        default={
            "cite_sources": True,
            "acknowledge_uncertainty": True,
            "provide_massachusetts_context": True,
            "highlight_ej_considerations": True
        },
        description="Requirements for assistant responses"
    )

class MassachusettsClimateRetriever:
    """
    A domain-specific retrieval system for Massachusetts climate economy information.
    Uses PDF reports and web content as knowledge sources with strict guardrails.
    """
    
    def __init__(
        self, 
        supabase_url: str,
        supabase_key: str,
        openai_api_key: str,
        constraints: Optional[MassachusettsClimateConstraints] = None,
        collection_name: str = "climate_memories",
        model_name: str = "gpt-4o"
    ):
        """Initialize the Massachusetts Climate Retriever"""
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.openai_api_key = openai_api_key
        self.collection_name = collection_name
        self.model_name = model_name
        self.constraints = constraints or MassachusettsClimateConstraints()
        
        # Initialize clients
        self.supabase = create_client(self.supabase_url, self.supabase_key)
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.llm = ChatOpenAI(
            temperature=0.1, 
            model=self.model_name,
            openai_api_key=self.openai_api_key
        )
        
        # Initialize vector store
        self.vector_store = SupabaseVectorStore(
            client=self.supabase,
            embedding=self.embeddings,
            table_name=self.collection_name,
            query_name="match_climate_memories"
        )
        
        # Set up retriever with contextual compression
        base_retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        # Use LLM to extract most relevant parts of retrieved documents
        compressor = LLMChainExtractor.from_llm(self.llm)
        self.retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        
        # Set up QA chain with custom prompt
        self.qa_chain = self._create_qa_chain()
        
        logger.info(f"Massachusetts Climate Retriever initialized with collection: {collection_name}")
    
    def _create_qa_chain(self) -> RetrievalQA:
        """Create a QA chain with custom prompt that enforces constraints"""
        # Create a prompt template that incorporates the constraints
        template = f"""You are the Massachusetts Climate Economy Assistant, a specialized AI focused exclusively on providing information about clean energy careers, training, and resources in Massachusetts.

CONSTRAINTS:
1. Geographic Focus: {self.constraints.geographic_focus}
2. Allowed Topics: {', '.join(self.constraints.allowed_topics)}
3. Prohibited Topics: {', '.join(self.constraints.prohibited_topics)}
4. Source Requirements:
   - Require Massachusetts sources: {self.constraints.source_requirements['require_massachusetts_source']}
   - Maximum source age: {self.constraints.source_requirements['max_source_age_years']} years
   - Preferred sources: {', '.join(self.constraints.source_requirements['preferred_sources'])}
5. Response Requirements:
   - Cite sources: {self.constraints.response_requirements['cite_sources']}
   - Acknowledge uncertainty: {self.constraints.response_requirements['acknowledge_uncertainty']}
   - Provide Massachusetts context: {self.constraints.response_requirements['provide_massachusetts_context']}
   - Highlight environmental justice considerations: {self.constraints.response_requirements['highlight_ej_considerations']}

CONTEXT:
{{context}}

QUESTION:
{{question}}

INSTRUCTIONS:
1. Answer ONLY if the question relates to Massachusetts clean energy economy, careers, training, or resources.
2. If the question is outside your constraints, politely explain that you can only provide information about Massachusetts clean energy economy topics.
3. Base your answer ONLY on the provided context and your knowledge of Massachusetts.
4. If the context doesn't contain relevant information, acknowledge the limitations of your knowledge.
5. Always cite your sources when providing specific information.
6. When discussing programs or resources, emphasize Massachusetts-specific options.
7. Consider environmental justice implications when relevant.
8. Format your response in a clear, helpful manner using markdown.

ANSWER:
"""
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
        
        # Create the QA chain
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
    
    async def ingest_pdf(self, pdf_path: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Ingest a PDF document into the vector store"""
        try:
            logger.info(f"Ingesting PDF: {pdf_path}")
            
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            
            # Add default metadata if not provided
            if metadata is None:
                metadata = {
                    "source": os.path.basename(pdf_path),
                    "source_type": "pdf",
                    "ingestion_date": datetime.now().isoformat()
                }
            
            # Add metadata to each document
            for doc in documents:
                doc.metadata.update(metadata)
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(splits)
            
            logger.info(f"Successfully ingested {len(splits)} chunks from {pdf_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting PDF {pdf_path}: {str(e)}")
            return False
    
    async def ingest_web_content(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Ingest web content into the vector store"""
        try:
            logger.info(f"Ingesting web content: {url}")
            
            # Load web content
            loader = WebBaseLoader(url)
            documents = loader.load()
            
            # Add default metadata if not provided
            if metadata is None:
                metadata = {
                    "source": url,
                    "source_type": "web",
                    "ingestion_date": datetime.now().isoformat()
                }
            
            # Add metadata to each document
            for doc in documents:
                doc.metadata.update(metadata)
            
            # Split documents
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            splits = text_splitter.split_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(splits)
            
            logger.info(f"Successfully ingested {len(splits)} chunks from {url}")
            return True
            
        except Exception as e:
            logger.error(f"Error ingesting web content {url}: {str(e)}")
            return False
    
    async def query(self, question: str) -> Dict[str, Any]:
        """Query the retriever with constraints applied"""
        try:
            logger.info(f"Processing query: {question}")
            
            # Check if question violates constraints
            if self._violates_constraints(question):
                return {
                    "answer": self._get_constraint_violation_response(question),
                    "sources": [],
                    "query": question,
                    "within_constraints": False
                }
            
            # Track token usage
            with get_openai_callback() as cb:
                # Get response from QA chain
                result = self.qa_chain({"query": question})
                
                # Extract sources from source documents
                sources = []
                if "source_documents" in result:
                    for doc in result["source_documents"]:
                        source = {
                            "content": doc.page_content[:200] + "...",  # Truncate for display
                            "metadata": doc.metadata
                        }
                        sources.append(source)
                
                # Log token usage
                logger.info(f"Token usage - Prompt: {cb.prompt_tokens}, Completion: {cb.completion_tokens}, Total: {cb.total_tokens}")
            
            return {
                "answer": result["result"],
                "sources": sources,
                "query": question,
                "within_constraints": True
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again or rephrase your question.",
                "sources": [],
                "query": question,
                "error": str(e),
                "within_constraints": True
            }
    
    def _violates_constraints(self, question: str) -> bool:
        """Check if a question violates the defined constraints"""
        question_lower = question.lower()
        
        # Check for prohibited topics
        for topic in self.constraints.prohibited_topics:
            if topic.lower() in question_lower:
                return True
        
        # Check if question is clearly not about Massachusetts
        non_mass_state_indicators = [
            "california climate", "new york climate", "florida climate",
            "texas climate", "washington climate", "oregon climate"
        ]
        
        for indicator in non_mass_state_indicators:
            if indicator in question_lower:
                return True
        
        return False
    
    def _get_constraint_violation_response(self, question: str) -> str:
        """Generate a response for questions that violate constraints"""
        return f"""I'm sorry, but I'm specifically designed to provide information about the Massachusetts clean energy economy, careers, training programs, and resources. 

Your question appears to be outside the scope of my knowledge and purpose. I can help with:

- Clean energy careers in Massachusetts
- Renewable energy initiatives in Massachusetts
- Energy efficiency programs in Massachusetts
- Workforce development for clean energy in Massachusetts
- Climate economy opportunities in Massachusetts
- Green jobs training in Massachusetts
- Environmental justice considerations in Massachusetts clean energy

Please feel free to ask me about any of these topics related to Massachusetts!"""

    async def ingest_required_reports(self) -> Dict[str, bool]:
        """Ingest all required reports from the constants file"""
        from constants import REQUIRED_REPORTS
        
        results = {}
        reports_dir = "reports"
        
        for report in REQUIRED_REPORTS:
            if report.startswith("http"):
                # Web content
                result = await self.ingest_web_content(
                    report,
                    metadata={
                        "source": report,
                        "source_type": "web",
                        "category": "massachusetts_climate_report"
                    }
                )
                results[report] = result
            else:
                # PDF file
                pdf_path = os.path.join(reports_dir, report)
                if os.path.exists(pdf_path):
                    result = await self.ingest_pdf(
                        pdf_path,
                        metadata={
                            "source": report,
                            "source_type": "pdf",
                            "category": "massachusetts_climate_report"
                        }
                    )
                    results[report] = result
                else:
                    logger.warning(f"Report file not found: {pdf_path}")
                    results[report] = False
        
        return results
