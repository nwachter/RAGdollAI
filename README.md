
# OpenSource AI PDF Chat
*base structure is from Little PDF Bot, thanks to the creator*

A simple application allowing the use of any LLM with a PDF.

## Features

- PDF document upload and processing
- Text chunking and embedding generation
- Semantic search for relevant context retrieval
- Question answering using the Deepseek language model
- Streamlit-based user interface

## Prerequisites

- Python 3.9+
- Ollama installed and running locally
- The Deepseek model downloaded in Ollama

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/RAGdollAI.git
cd RAGdollAI
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows just use without "source": .venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

## Project Structure

```
pdf-qa-system/
├── main.py                # Main application file
├── document_store/pdfs/   # Directory for uploaded PDFs
├── requirements.txt       # Project dependencies
├── .gitignore             # Git ignore file
└── README.md              # Project documentation
```

## Dependencies

```
streamlit
pypdf
langchain
langchain-community
langchain-core
langchain-ollama
```

## Usage

1. Start the Ollama service and ensure the used model is available:

```bash
ollama run model_name
```
```bash
ollama run deepseek-r1:1.5b
```

2. Run the Streamlit application:

```bash
streamlit run streamlit_GUI.py
```

3. Access the application in your web browser at `http://localhost:8501`

4. Upload a PDF document using the file uploader

5. Ask questions about the document content using the chat input

## Configuration

Key parameters can be adjusted in the `Config` class within `main.py`:

- `CHUNK_SIZE`: Size of text chunks (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks (default: 200)
- `MODEL_NAME`: Ollama model to use (default: "deepseek-r1:1.5b")
- `MAX_RETRIES`: Maximum retry attempts for operations (default: 3)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- LangChain for the document processing pipeline
- Ollama for the local language model hosting
- Streamlit for the web interface framework

