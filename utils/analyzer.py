import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)

def analyze_resume_vs_jd(resume_json: dict, jd_text: str) -> dict:
    """
    Perform a complete matching and analysis between the structured resume and the job description.
    Returns scores, skill counts, section analysis, prioritized suggestions, roadmap, and projects.
    """
    if not API_KEY:
        raise ValueError("Google API Key is not configured.")
        
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Format the resume for LLM consumption
    resume_dump = json.dumps(resume_json, indent=2)
    
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) recruiter and career consultant.
    Compare the following resume against the job description.
    
    Resume (JSON format):
    {resume_dump}
    
    Job Description:
    {jd_text}
    
    You must perform a detailed evaluation and return a JSON object with this exact structure:
    {{
      "ats_score": 78, // Match score percentage (integer 0-100) based on JD requirements alignment
      "keyword_coverage": 65, // Percentage of critical keywords from JD present in resume (integer 0-100)
      "resume_quality_score": 82, // Quality score based on formatting, bullet point metrics, and section depth (integer 0-100)
      "matched_skills": ["Python", "SQL"], // Skills present in both resume and JD (list of strings)
      "missing_skills": ["Docker", "AWS"], // Key skills in JD but missing in resume (list of strings)
      "recommended_skills": ["Kubernetes", "CI/CD"], // Skills that are highly adjacent and beneficial to add (list of strings)
      "technical_skills_count": 12, // Number of technical skills in the resume (integer)
      "soft_skills_count": 4, // Number of soft/professional skills in the resume (integer)
      "section_analysis": {{
        "Skills": {{ "score": 8, "suggestion": "Categorize them and add missing tools like Docker." }},
        "Experience": {{ "score": 7, "suggestion": "Quantify accomplishments using metrics (e.g. %, $ saved, hours)." }},
        "Projects": {{ "score": 6, "suggestion": "Include technologies used for each project explicitly." }},
        "Education": {{ "score": 9, "suggestion": "Looks good." }},
        "Achievements": {{ "score": 5, "suggestion": "Highlight technical or academic accomplishments." }},
        "Certifications": {{ "score": 4, "suggestion": "Add AWS or other industry-relevant certifications." }}
      }},
      "ai_suggestions": {{
        "Priority 1": {{ "title": "Incorporate missing keywords", "explanation": "Add keywords like Docker and AWS to matching roles." }},
        "Priority 2": {{ "title": "Quantify achievements in Experience", "explanation": "Provide numbers to demonstrate business impact rather than just listing tasks." }},
        "Priority 3": {{ "title": "Add a project using missing tools", "explanation": "Build a deployment project showcasing containerization." }},
        "Priority 4": {{ "title": "Obtain relevant certifications", "explanation": "Validating your cloud skills increases recruiter confidence." }}
      }},
      "learning_roadmap": [
        {{ "step": 1, "topic": "Learn Docker", "current_score": 78, "expected_score": 84, "duration": "1 week" }},
        {{ "step": 2, "topic": "Learn AWS fundamentals", "current_score": 84, "expected_score": 90, "duration": "2 weeks" }},
        {{ "step": 3, "topic": "Learn Git CI/CD pipelines", "current_score": 90, "expected_score": 94, "duration": "3 days" }}
      ],
      "project_suggestions": [
        {{
          "name": "Dockerized Microservice API",
          "difficulty": "Medium",
          "duration": "1 week",
          "skills": ["Docker", "Python", "Flask", "GitHub Actions"],
          "impact": "High - Demonstrates modern containerization and DevOps skills requested in JD"
        }},
        {{
          "name": "AWS Serverless Analytics Pipeline",
          "difficulty": "Hard",
          "duration": "2 weeks",
          "skills": ["AWS Lambda", "S3", "API Gateway", "Terraform"],
          "impact": "High - Validates cloud architecture and serverless development capabilities"
        }}
      ]
    }}
    
    Make the evaluation realistic and high-fidelity. If the resume is excellent, give scores above 85. If it is weak, score it lower.
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        return json.loads(response.text)
    except Exception as e:
        # Retry with a clean extract if failed
        import re
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        raise ValueError("Failed to analyze resume vs JD.")

def generate_cover_letter(resume_text: str, jd_text: str, company_role: str) -> str:
    """
    Generate a tailored cover letter based on resume text, JD, and company/role details.
    """
    if not API_KEY:
        return "API Key not configured."
        
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an expert career advisor. Write a tailored, professional, and compelling cover letter for:
    Company and Role Details: {company_role}
    
    Use the candidate's resume below to extract achievements and match them to the Job Description:
    
    Resume:
    {resume_text}
    
    Job Description:
    {jd_text}
    
    The cover letter should be business-formal, persuasive, highlight 2-3 key accomplishments that match the JD, and be around 300-400 words. Do not use placeholders (like [Company Name]) if they can be inferred; if not, use clear placeholders.
    """
    
    response = model.generate_content(prompt)
    return response.text

def generate_interview_prep(resume_text: str, jd_text: str) -> list:
    """
    Generates a list of interview questions tailored to the resume and JD.
    Each item contains the question, category (Technical, HR, Project, Behavioral), difficulty (Easy, Medium, Hard), and sample_answer.
    """
    if not API_KEY:
        return []
        
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""
    You are an expert interviewer. Generate a list of 10 interview questions based on this resume and job description.
    
    Resume:
    {resume_text}
    
    Job Description:
    {jd_text}
    
    Generate questions across 4 categories: 'Technical', 'HR', 'Project', and 'Behavioral'.
    Assign difficulty levels: 'Easy', 'Medium', or 'Hard'.
    Provide a robust 'sample_answer' for each.
    
    Return a JSON list of objects matching this schema:
    [
      {{
        "category": "Technical", // Technical, HR, Project, Behavioral
        "difficulty": "Medium", // Easy, Medium, Hard
        "question": "The question string",
        "sample_answer": "Sample answer detailing what a top candidate would say."
      }}
    ]
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        return json.loads(response.text)
    except Exception:
        import re
        match = re.search(r"\[.*\]", response.text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        return []

def rewrite_resume_content(resume_json: dict, jd_text: str) -> dict:
    """
    Optimizes and rewrites resume sections (Summary, Projects, Experience, Skills, Achievements)
    to match the Job Description while keeping information truthful.
    """
    if not API_KEY:
        return resume_json
        
    model = genai.GenerativeModel("gemini-2.5-flash")
    resume_dump = json.dumps(resume_json, indent=2)
    
    prompt = f"""
    You are an expert resume writer. Rewrite the following resume content to optimize it for the job description.
    
    Rules:
    1. Keep all facts truthful (e.g. do not change company names, university degrees, or work dates).
    2. Optimize the 'summary' to be engaging and keyword-rich.
    3. Rewrite 'experience' bullet points to use strong action verbs and highlight achievements/impact matching the JD.
    4. Rewrite 'projects' bullet points to explicitly mention tools and methodologies requested in the JD.
    5. Enhance the 'skills' section, organizing it and filling in matching subskills the candidate has but did not list.
    6. Improve formatting of 'achievements'.
    
    Resume JSON:
    {resume_dump}
    
    Job Description:
    {jd_text}
    
    Output a revised JSON representing the optimized resume following the EXACT same keys as the input resume JSON.
    """
    
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    try:
        return json.loads(response.text)
    except Exception:
        import re
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        return resume_json

def chat_with_coach(messages: list, resume_text: str, jd_text: str, analysis_json: dict) -> str:
    """
    Chat with the AI Career Coach.
    Passes full conversation history (messages), resume, JD, and previous analysis as context.
    """
    if not API_KEY:
        return "AI Coach is unavailable because GOOGLE_API_KEY is not set."
        
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Build context prompt
    analysis_dump = json.dumps(analysis_json, indent=2)
    
    system_instruction = f"""
    You are a helpful, professional, and friendly AI Career Coach.
    You help candidates optimize their resumes, prepare for interviews, suggest skills/projects/certifications, and answer career questions.
    
    Use the following candidate context to formulate your answers:
    
    Candidate's Resume Text:
    {resume_text}
    
    Target Job Description:
    {jd_text}
    
    Latest ATS Match & Skill Analysis:
    {analysis_dump}
    
    Tone guidelines: Encourage the user, be actionable, provide bullet points where appropriate, and keep formatting clean.
    You can rewrite sections, give mock feedback, or answer specific questions like "Will this work for Google?" or "Is my ATS score low?".
    """
    
    # Format messages for the API
    # Gemini conversation format: we can construct a list of parts, or send it as a single request
    # To keep it simple and robust, we will build a single prompt history with system instructions
    history_str = ""
    for msg in messages:
        role = "Candidate" if msg["role"] == "user" else "Coach"
        history_str += f"{role}: {msg['content']}\n\n"
        
    prompt = f"""
    {system_instruction}
    
    Here is the conversation history:
    {history_str}
    
    Coach: (Please respond to the last message from the Candidate)
    """
    
    response = model.generate_content(prompt)
    return response.text
