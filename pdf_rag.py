import os
import streamlit as st

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM


# ====== CONFIG ======
PDF_DIR = r"C:/Users/Luke/Desktop/Luke Harris Repo/2.Ollama_Models/chat-with-pdf/pdfs/"

os.makedirs(PDF_DIR, exist_ok=True)  # ensure folder exists

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question.
If you don't know the answer, just say that you don't know. 
Use three sentences maximum and keep the answer concise.

Question: {question}
Context: {context}
Answer:
"""


# ====== INIT OLLAMA ======
embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")
vector_store = InMemoryVectorStore(embeddings)

model = OllamaLLM(model="deepseek-r1:1.5b")


# ====== FUNCTIONS ======
def upload_pdf(file):
    """Save uploaded PDF to the local directory."""
    save_path = os.path.join(PDF_DIR, file.name)
    with open(save_path, "wb") as f:
        f.write(file.getbuffer())
    return save_path


def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    return loader.load()


def split_text(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    return splitter.split_documents(documents)


def index_docs(documents):
    vector_store.add_documents(documents)


def retrieve_docs(query):
    return vector_store.similarity_search(query)


def answer_question(question, documents):
    context = "\n\n".join([doc.page_content for doc in documents])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    return chain.invoke({"question": question, "context": context})


# ====== STREAMLIT UI ======
st.title("Chat with PDF – DeepSeek R1 (Ollama)")

uploaded_pdf = st.file_uploader("Upload PDF", type="pdf", accept_multiple_files=False)

if uploaded_pdf:
    st.success(f"Uploaded: {uploaded_pdf.name}")

    filepath = upload_pdf(uploaded_pdf)
    documents = load_pdf(filepath)
    chunks = split_text(documents)
    index_docs(chunks)

    question = st.chat_input("Ask something about the PDF...")

    if question:
        st.chat_message("user").write(question)

        related_docs = retrieve_docs(question)
        answer = answer_question(question, related_docs)

        st.chat_message("assistant").write(answer)
