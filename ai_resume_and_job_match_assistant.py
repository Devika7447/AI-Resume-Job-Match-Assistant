import os
import re
import tempfile
from typing import List

import streamlit as st
from dotenv import load_dotenv
import pypdf
from docx import Document

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter


# -----------------------------
# Load API Key
# -----------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    st.error("Set GOOGLE_API_KEY in your .env file")
    st.stop()


# -----------------------------
# Gemini Models
# -----------------------------
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=API_KEY,
)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# -----------------------------
# File Parsing
# -----------------------------
def extract_pdf(file):
    reader = pypdf.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_docx(file):
    doc = Document(file)
    return "\n".join([p.text for p in doc.paragraphs])


def extract_resume_text(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        return extract_pdf(uploaded_file)

    elif uploaded_file.name.endswith(".docx"):
        return extract_docx(uploaded_file)

    else:
        raise ValueError("Unsupported file format")


# -----------------------------
# Text Splitter
# -----------------------------
def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    return splitter.split_text(text)


# -----------------------------
# Build Vector Store
# -----------------------------
def build_vector_store(text):
    chunks = split_text(text)
    return FAISS.from_texts(chunks, embeddings)


# -----------------------------
# Similarity Match
# -----------------------------
def compute_match(resume_text, jd_text):
    resume_store = build_vector_store(resume_text)

    docs = resume_store.similarity_search(jd_text, k=5)

    combined = "\n".join([d.page_content for d in docs])

    prompt = f"""
    Compare this resume against the job description.

    Resume:
    {combined}

    Job Description:
    {jd_text}

    Return:
    1. Match Score %
    2. Missing Skills
    3. Strengths
    4. 2 Improved Resume Bullet Points
    5. Tailored Cover Letter
    """

    response = llm.invoke(prompt)

    return response.content


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(
    page_title="AI Resume Match Assistant",
    layout="wide",
)

st.title("📄 AI Resume & Job Match Assistant")

uploaded_file = st.file_uploader(
    "Upload Resume (PDF/DOCX)",
    type=["pdf", "docx"],
)

job_description = st.text_area(
    "Paste Job Description",
    height=300,
)

if st.button("Analyze Resume"):
    if not uploaded_file:
        st.error("Upload a resume")

    elif not job_description.strip():
        st.error("Paste job description")

    else:
        with st.spinner("Analyzing..."):
            try:
                resume_text = extract_resume_text(uploaded_file)

                result = compute_match(
                    resume_text,
                    job_description,
                )

                st.success("Analysis Complete")
                st.markdown(result)

            except Exception as e:
                st.error(f"Error: {str(e)}")