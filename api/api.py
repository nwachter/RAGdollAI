from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import tempfile
import shutil
from typing import List
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Initialize FastAPI app
app = FastAPI()

# Constants
EMBEDDING_MODEL = OllamaEmbeddings(
    model="mxbai-embed-large", 
    base_url="http://ollama:11434"
)

LANGUAGE_MODEL = OllamaLLM(
    model="deepseek-r1:1.5b",
    base_url="http://ollama:11434"
)

# Global variable to store the vector database
DOCUMENT_VECTOR_DB = None

# Prompt Template
PROMPT_TEMPLATE = """
Tu es un assistant support chargé de guider les utilisateurs dans une application web en fournissant des renseignements sur le document PDF fourni. 
Si tu êtes incertain, déclare que tu ne sais pas. Sois concis et factuel, répond en français uniquement sauf si on te demande le contraire et base toi sur le document fourni.

Question: {user_query} 
Contexte: {document_context} 
Réponse:
"""

def process_uploaded_file(file_path: str):
    """Process a single uploaded PDF file"""
    document_loader = PDFPlumberLoader(file_path)
    raw_documents = document_loader.load()
    return raw_documents

def chunk_documents(raw_documents):
    """Split documents into chunks"""
    text_processor = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=300,
        add_start_index=True
    )
    return text_processor.split_documents(raw_documents)

def index_documents(document_chunks):
    """Create and populate vector database"""
    global DOCUMENT_VECTOR_DB
    DOCUMENT_VECTOR_DB = InMemoryVectorStore(EMBEDDING_MODEL)
    DOCUMENT_VECTOR_DB.add_documents(document_chunks)

def find_related_documents(query):
    """Find relevant documents based on query"""
    if DOCUMENT_VECTOR_DB is None:
        return []
    return DOCUMENT_VECTOR_DB.similarity_search(query)

def generate_answer(user_query, context_documents):
    """Generate answer based on query and context"""
    if not context_documents:
        return "Aucun document n'a été chargé. Veuillez d'abord télécharger un document PDF."
    
    context_text = "\n\n".join([doc.page_content for doc in context_documents])
    conversation_prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    response_chain = conversation_prompt | LANGUAGE_MODEL
    return response_chain.invoke({"user_query": user_query, "document_context": context_text})

# Pydantic models
class QueryRequest(BaseModel):
    query: str

class UploadResponse(BaseModel):
    message: str
    filename: str
    chunks_created: int

# API Endpoints
@app.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a PDF document"""
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Copy uploaded file content to temporary file
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        try:
            # Process the uploaded file
            raw_documents = process_uploaded_file(temp_file_path)
            
            if not raw_documents:
                raise HTTPException(status_code=400, detail="Aucun contenu trouvé dans le fichier PDF")
            
            # Chunk and index documents
            document_chunks = chunk_documents(raw_documents)
            index_documents(document_chunks)
            
            return UploadResponse(
                message="Document traité avec succès",
                filename=file.filename,
                chunks_created=len(document_chunks)
            )
        
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement du document: {str(e)}")

@app.post("/query")
def query_documents(request: QueryRequest):
    """Query the uploaded documents"""
    try:
        if DOCUMENT_VECTOR_DB is None:
            return {"response": "Aucun document n'a été chargé. Veuillez d'abord télécharger un document PDF."}
        
        relevant_docs = find_related_documents(request.query)
        ai_response = generate_answer(request.query, relevant_docs)
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
def get_status():
    """Get the current status of the system"""
    has_documents = DOCUMENT_VECTOR_DB is not None
    return {
        "status": "healthy",
        "documents_loaded": has_documents
    }

@app.delete("/clear")
def clear_documents():
    """Clear all loaded documents"""
    global DOCUMENT_VECTOR_DB
    DOCUMENT_VECTOR_DB = None
    return {"message": "Documents supprimés avec succès"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}