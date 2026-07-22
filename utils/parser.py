import os
import json
import pypdf
from docx import Document
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

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
    """
    Extract text from uploaded PDF or DOCX file.
    uploaded_file can be a file-like object (Streamlit UploadedFile) or a path.
    """
    if hasattr(uploaded_file, "name"):
        name = uploaded_file.name
    else:
        name = str(uploaded_file)
        
    if name.endswith(".pdf"):
        return extract_pdf(uploaded_file)
    elif name.endswith(".docx"):
        return extract_docx(uploaded_file)
    else:
        # Try reading as text file
        try:
            return uploaded_file.read().decode("utf-8")
        except Exception:
            raise ValueError("Unsupported file format. Please upload PDF or DOCX.")

def parse_resume_to_json(resume_text: str) -> dict:
    """
    Use Gemini to parse the unstructured resume text into a structured JSON format.
    """
    if not API_KEY:
        raise ValueError("Google API Key is not configured.")
        
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an expert resume parsing assistant. Analyze the following unstructured resume text and extract all information into a structured JSON format.
    Ensure that you normalize dates (e.g. 'June 2022 - Present' or '05/2021 - 12/2023').
    Ensure skills are categorized logically into broad groups (e.g. 'Languages', 'Databases', 'Tools', 'Frameworks'). If not categorized in the resume, categorize them yourself.
    
    Resume Text:
    {resume_text}
    
    You must output a JSON object matching this schema:
    {{
      "name": "Full Name (string)",
      "email": "Email (string)",
      "phone": "Phone (string)",
      "linkedin": "LinkedIn Profile URL (string or empty)",
      "github": "GitHub Profile URL (string or empty)",
      "website": "Portfolio/Website URL (string or empty)",
      "summary": "Professional Summary (string or empty)",
      "skills": {{
        "Category1": ["Skill1", "Skill2"],
        "Category2": ["Skill3", "Skill4"]
      }},
      "experience": [
        {{
          "company": "Company Name (string)",
          "role": "Job Title (string)",
          "location": "Location (string or empty)",
          "dates": "Dates of employment (string)",
          "bullet_points": ["bullet point 1", "bullet point 2"]
        }}
      ],
      "projects": [
        {{
          "name": "Project Name (string)",
          "technologies": "Comma-separated list of technologies used (string)",
          "dates": "Dates (string or empty)",
          "bullet_points": ["bullet point 1", "bullet point 2"]
        }}
      ],
      "education": [
        {{
          "institution": "University/School Name (string)",
          "degree": "Degree and Major (string)",
          "location": "Location (string or empty)",
          "dates": "Dates attended/Graduation date (string)"
        }}
      ],
      "achievements": [
        {{
          "title": "Title of Achievement (string)",
          "issuer": "Issuer/Organizer (string or empty)",
          "date": "Date (string or empty)",
          "description": "Short description of achievement (string or empty)"
        }}
      ],
      "certifications": [
        {{
          "title": "Certification Title (string)",
          "issuer": "Issuing Body (string or empty)",
          "date": "Date (string or empty)"
        }}
      ]
    }}
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        parsed_data = json.loads(response.text)
        return parsed_data
    except Exception as e:
        # Fallback in case JSON parsing fails
        print(f"Failed parsing JSON from Gemini response: {e}")
        # Try regex extract
        import re
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        raise ValueError("Failed to parse resume into structured JSON.")
