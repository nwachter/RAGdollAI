import streamlit as st
import requests

# API URL
API_URL = "http://api:8000"  # Use the service name for inter-container communication
#API_URL = "http://localhost:8000"
# UI Styling (unchanged)
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
    
    .stFileUploader {
        background-color: #1E1E1E;
        border: 1px solid #3A3A3A;
        border-radius: 5px;
        padding: 15px;
    }
    
    h1, h2, h3 {
        color: #00FFAA !important;
    }
    </style>
    """, unsafe_allow_html=True)

# UI Configuration
st.title("📘 RAGdoll IA")
st.markdown("### Meilleure que votre meilleur ami")
st.markdown("---")

st.success("✅ Connecté à l'API. Posez vos questions ci-dessous.")

# Chat input for user queries
user_input = st.chat_input("Entrez votre question concernant les documents...")

if user_input:
    with st.chat_message("user", avatar="👤"):
        st.write(user_input)
    
    with st.spinner("Analyse des documents..."):
        try:
            # Send query to the API
            response = requests.post(f"{API_URL}/query", json={"query": user_input})
            if response.status_code == 200:
                ai_response = response.json().get("response")
            else:
                ai_response = "Erreur lors de la communication avec l'API."
        except Exception as e:
            ai_response = f"Erreur: {str(e)}"
        
    with st.chat_message("RAGdoll", avatar="😺"):
        st.write(ai_response)