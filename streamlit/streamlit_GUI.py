import streamlit as st
import requests
import time

# API URL
API_URL = "http://api:8000"

# UI Styling
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Chat Input Styling */
    .stChatInput input {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        border: 1px solid #3A3A3A !important;
    }
    
    /* User Message Styling */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: #1E1E1E !important;
        border: 1px solid #3A3A3A !important;
        color: #E0E0E0 !important;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Assistant Message Styling */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #2A2A2A !important;
        border: 1px solid #404040 !important;
        color: #F0F0F0 !important;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Avatar Styling */
    .stChatMessage .avatar {
        background-color: #00FFAA !important;
        color: #000000 !important;
    }
    
    /* Text Color Fix */
    .stChatMessage p, .stChatMessage div {
        color: #FFFFFF !important;
    }
    
    .upload-area {
        background-color: #1E1E1E;
        border: 2px dashed #3A3A3A;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin: 20px 0;
    }
    
    .upload-success {
        background-color: #2A4A2A;
        border: 1px solid #4A8A4A;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
    
    h1, h2, h3 {
        color: #00FFAA !important;
    }
    
    .status-indicator {
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 12px;
        font-weight: bold;
    }
    
    .status-ready {
        background-color: #2A4A2A;
        color: #4AFA4A;
    }
    
    .status-empty {
        background-color: #4A2A2A;
        color: #FA4A4A;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'documents_loaded' not in st.session_state:
    st.session_state.documents_loaded = False
if 'current_document' not in st.session_state:
    st.session_state.current_document = None

def check_api_status():
    """Check if API is available and if documents are loaded"""
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data.get("documents_loaded", False)
    except:
        pass
    return False, False

def upload_document(uploaded_file):
    """Upload document to the API"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
        response = requests.post(f"{API_URL}/upload", files=files)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"message": "Erreur lors du téléchargement"}
    except Exception as e:
        return False, {"message": f"Erreur: {str(e)}"}

def clear_documents():
    """Clear all loaded documents"""
    try:
        response = requests.delete(f"{API_URL}/clear")
        if response.status_code == 200:
            return True
    except:
        pass
    return False

# UI Configuration
st.title("📘 RAGdoll IA")
st.markdown("### Meilleure que votre meilleur ami")
st.markdown("---")

# Check API status
api_available, documents_loaded = check_api_status()
st.session_state.documents_loaded = documents_loaded

# Status indicator
col1, col2 = st.columns([3, 1])
with col1:
    if api_available:
        if documents_loaded:
            st.markdown('<div class="status-indicator status-ready">✅ Prêt à répondre</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator status-empty">📄 En attente de document</div>', unsafe_allow_html=True)
    else:
        st.error("❌ API non disponible")

with col2:
    if documents_loaded:
        if st.button("🗑️ Effacer", help="Supprimer le document actuel"):
            if clear_documents():
                st.session_state.documents_loaded = False
                st.session_state.current_document = None
                st.session_state.chat_history = []
                st.rerun()

# Document upload section
if not documents_loaded:
    st.markdown("### 📤 Télécharger un document")
    
    uploaded_file = st.file_uploader(
        "Choisissez un fichier PDF",
        type=['pdf'],
        help="Seuls les fichiers PDF sont acceptés"
    )
    
    if uploaded_file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("📤 Traiter le document", type="primary"):
                with st.spinner("Traitement du document en cours..."):
                    success, result = upload_document(uploaded_file)
                    
                if success:
                    st.session_state.documents_loaded = True
                    st.session_state.current_document = uploaded_file.name
                    st.success(f"✅ {result['message']}")
                    st.info(f"📊 Document découpé en {result['chunks_created']} segments")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {result['message']}")

# Chat section
if documents_loaded:
    st.markdown("### 💬 Chat avec votre document")
    
    if st.session_state.current_document:
        st.info(f"📄 Document actuel: {st.session_state.current_document}")
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"], avatar=message["avatar"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Posez votre question concernant le document...")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_input,
            "avatar": "👤"
        })
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        # Get AI response
        with st.spinner("Analyse du document..."):
            try:
                response = requests.post(f"{API_URL}/query", json={"query": user_input})
                if response.status_code == 200:
                    ai_response = response.json().get("response")
                else:
                    ai_response = "Erreur lors de la communication avec l'API."
            except Exception as e:
                ai_response = f"Erreur: {str(e)}"
        
        # Add AI response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": ai_response,
            "avatar": "😺"
        })
        
        # Display AI response
        with st.chat_message("RAGdoll", avatar="😺"):
            st.write(ai_response)

else:
    st.markdown("### ℹ️ Comment utiliser RAGdoll IA")
    st.markdown("""
    1. **Téléchargez** un document PDF en utilisant le bouton ci-dessus
    2. **Attendez** que le document soit traité et indexé
    3. **Posez** vos questions concernant le contenu du document
    4. **Obtenez** des réponses précises basées sur le document
    """)

# Sidebar with additional info
with st.sidebar:
    st.markdown("### 📋 Informations")
    
    if documents_loaded:
        st.success("Document chargé ✅")
        if st.session_state.current_document:
            st.write(f"**Fichier:** {st.session_state.current_document}")
    else:
        st.warning("Aucun document chargé")
    
    st.markdown("---")
    st.markdown("### 🛠️ Fonctionnalités")
    st.markdown("""
    - Upload de documents PDF
    - Analyse intelligente du contenu
    - Chat contextuel
    """)
    
    st.markdown("---")
    st.markdown("### 🤖 Modèles utilisés")
    st.markdown("""
    - **LLM:** DeepSeek-R1 1.5B
    - **Embeddings:** mxbai-embed-large
    - **Backend:** Ollama + FastAPI
    """)