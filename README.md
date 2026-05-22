# AI Resume & Job Match Assistant 🚀

## Overview

**AI Resume & Job Match Assistant** is an end-to-end Generative AI application that analyzes a candidate's resume against a target job description and provides intelligent recommendations to improve job alignment.

The system combines **Large Language Models (Gemini)**, **Retrieval-Augmented Generation (RAG)**, **semantic vector search (FAISS)**, document parsing, and local embedding generation to produce actionable career insights such as:

- ✅ Resume–job match score
- 🔍 Missing technical skills
- 💪 Candidate strengths
- 📝 ATS optimization suggestions
- ✏️ Improved resume bullet points
- 📄 Tailored AI-generated cover letter

Built as a production-style **Streamlit** application, this project demonstrates practical implementation of LLM orchestration, semantic search pipelines, and intelligent career recommendation systems.

---

## Features ✨

### 📄 Resume Parsing

**Supports:**
- PDF resumes (PyPDF)
- DOCX resumes (python-docx)

**Extracts:**
- Skills
- Experience
- Education
- Keywords
- Semantic content

### 🧾 Job Description Analysis

Processes raw job descriptions to identify:
- Required technical skills
- Core responsibilities
- Domain-specific keywords
- Priority competency areas

### 🔎 Semantic Resume Matching

**Uses:**
- Sentence Transformers
- FAISS Vector Database

Performs semantic similarity search to compare resume relevance against job requirements — beyond exact keyword matching.

### 🤖 LLM-Powered Reasoning

Uses **Google Gemini 1.5 Flash** for:
- Resume quality evaluation
- Context-aware gap analysis
- Resume enhancement suggestions
- Personalized cover letter generation

### 💡 AI Recommendations

Generates:
- Match percentage score
- Missing skills analysis
- Key strengths identification
- Optimized resume bullet rewrites
- Tailored cover letter

---

## Tech Stack 🛠️

| Layer              | Technology                              |
|--------------------|------------------------------------------|
| **Frontend**       | Streamlit                               |
| **Backend**        | Python                                  |
| **LLM**            | Google Gemini 1.5 Flash                 |
| **Embeddings**     | Sentence Transformers (all-MiniLM-L6-v2) |
| **Vector Database**| FAISS                                   |
| **Document Processing** | PyPDF, python-docx                 |
| **AI Framework**   | LangChain                               |

---

## Architecture

```
Resume Upload
   ↓
Document Parsing
   ↓
Text Chunking
   ↓
Embedding Generation
   ↓
FAISS Vector Indexing
   ↓
Semantic Retrieval
   ↓
Gemini Reasoning Engine
   ↓
Resume Matching + Suggestions + Cover Letter
```

---

## Getting Started 🚀

### Prerequisites

- Python 3.9+
- Google Gemini API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Devika7447/AI-Resume-Job-Match-Assistant.git
   cd AI-Resume-Job-Match-Assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**

   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

---

## Usage

1. Upload your resume (PDF or DOCX format)
2. Paste the target job description into the text area
3. Click **Analyze** to run the AI pipeline
4. Review your:
   - Match score
   - Missing skills
   - Strengths
   - ATS-optimized bullet points
   - Generated cover letter

---

## Real-World Applications

This project can be used for:
- 🎯 AI-powered ATS optimization
- 🧭 Career recommendation platforms
- 📋 Resume enhancement tools
- 🏢 HR screening assistants
- 🔍 Talent acquisition automation

---

## Key Learning Outcomes

This project demonstrates expertise in:
- Generative AI Engineering
- RAG pipelines
- Vector databases
- Semantic search
- LLM prompt orchestration
- Streamlit production apps
- Resume intelligence systems

---

## License

This project is open-source and available under the [MIT License](LICENSE).
