from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# Initialize FastAPI app
app = FastAPI()

# Constants
PDF_STORAGE_PATH = 'document_store/pdfs/'
EMBEDDING_MODEL = OllamaEmbeddings(
    model="mxbai-embed-large", 
    #model="SFR-Embedding-Mistral", //n'était pas indiqué
    #model="deepseek-r1",
    base_url="http://ollama:11434"  # Connect to the Ollama service //testerror
    #base_url="http://localhost:11434"  # Connect to the Ollama service
)
DOCUMENT_VECTOR_DB = InMemoryVectorStore(EMBEDDING_MODEL)
LANGUAGE_MODEL = OllamaLLM(
   # model="mistral:7b",
   model="deepseek-r1:1.5b",
    base_url="http://ollama:11434"  # Connect to the Ollama service
    #base_url="http://localhost:11434"  # Connect to the Ollama service
)

# Prompt Template
PROMPT_TEMPLATE = """
Tu es un assistant support chargé de guider les utilisateurs dans une application web en fournissant des renseignements sur le document PDF fourni. 
Si tu êtes incertain, déclare que tu ne sais pas. Sois concis et factuel, répond en français uniquement sauf si on te demande le contraire et base toi sur le document fourni.

Question: {user_query} 
Contexte: {document_context} 
Réponse:
"""

# Load and process all PDFs from the folder
def load_and_process_pdfs():
    raw_documents = []
    for filename in os.listdir(PDF_STORAGE_PATH):
        if filename.endswith(".pdf"):
            file_path = os.path.join(PDF_STORAGE_PATH, filename)
            document_loader = PDFPlumberLoader(file_path)
            raw_documents.extend(document_loader.load())
    return raw_documents

def chunk_documents(raw_documents):
    text_processor = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=300,
        add_start_index=True
    )
    return text_processor.split_documents(raw_documents)

def index_documents(document_chunks):
    DOCUMENT_VECTOR_DB.add_documents(document_chunks)

def find_related_documents(query):
    return DOCUMENT_VECTOR_DB.similarity_search(query)

def generate_answer(user_query, context_documents):
    context_text = "\n\n".join([doc.page_content for doc in context_documents])
    conversation_prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    response_chain = conversation_prompt | LANGUAGE_MODEL
    return response_chain.invoke({"user_query": user_query, "document_context": context_text})

# Reindex documents on startup
raw_docs = load_and_process_pdfs()
processed_chunks = chunk_documents(raw_docs)
index_documents(processed_chunks)

# Pydantic model for request body
class QueryRequest(BaseModel):
    query: str

# API Endpoints
@app.post("/query")
def query_documents(request: QueryRequest):
    try:
        relevant_docs = find_related_documents(request.query)
        ai_response = generate_answer(request.query, relevant_docs)
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}