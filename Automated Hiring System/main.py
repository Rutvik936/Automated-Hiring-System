from fastapi import FastAPI, UploadFile, File, Form
from parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    rule_based_parse,
    llm_enhance
)

from groq import Groq
from dotenv import load_dotenv
import os
import json
import shutil
from pydantic import BaseModel

# Load environment variables
load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

# ============================
# HOME ROUTE
# ============================
@app.get("/")
def home():
    return {"message": "Resume Parsing API is running ✔"}


# ============================
# RESUME UPLOAD API
# ============================
@app.post("/upload-resume")
async def upload_resume(
    candidate_name: str = Form(...),
    candidate_email: str = Form(...),
    job_id: str = Form(...),
    file: UploadFile = File(...)
):
    temp_path = f"temp_{file.filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Detect file type
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(temp_path)
    elif file.filename.lower().endswith(".docx"):
        text = extract_text_from_docx(temp_path)
    else:
        return {"error": "Unsupported file type. Only PDF and DOCX allowed."}

    # Rule-based parsing
    rule_output = rule_based_parse(text)

    # LLM Enhanced parsing
    final_output = llm_enhance(rule_output, text)

    os.remove(temp_path)

    return {
        "status": "success",
        "candidate_name": candidate_name,
        "candidate_email": candidate_email,
        "job_id": job_id,
        "parsed": final_output
    }


# ============================
# CANDIDATE SCORING API
# ============================
class ScoreRequest(BaseModel):
    resume: dict
    job_description: str


@app.post("/score-candidate")
async def score_candidate(payload: ScoreRequest):

    resume_json = payload.resume
    job_description = payload.job_description

    prompt = f"""
    You are an ATS scoring engine.
    Score the candidate from 0 to 100 using ONLY the given resume and job description.

    RULES:
    - Do NOT hallucinate missing skills.
    - Explicit skill match: +2
    - Inferred skill match: +1
    - Missing required skill: -3
    - Relevant experience: +10
    - Relevant projects: +10
    - If experience missing: score <= 40

    RETURN STRICT JSON:
    {{
        "score": 0,
        "skill_match": [],
        "missing_skills": [],
        "experience_relevance": "",
        "final_recommendation": ""
    }}

    Resume JSON:
    {resume_json}

    Job Description:
    {job_description}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
    )

    raw = response.choices[0].message.content

    try:
        return json.loads(raw)
    except:
        return {
            "error": "LLM returned invalid JSON",
            "raw_output": raw
        }
