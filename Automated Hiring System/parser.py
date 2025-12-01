import re
import pdfplumber
import dateparser
import spacy
from docx import Document
import requests
import json
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Load spaCy model
nlp = spacy.load("en_core_web_sm")


# =====================================================
# 1. TEXT EXTRACTION
# =====================================================
def extract_text_from_pdf(path: str):
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text.append(t)
    return "\n".join(text)


def extract_text_from_docx(path: str):
    doc = Document(path)
    return "\n".join([p.text for p in doc.paragraphs])


# =====================================================
# 2. REGEX EXTRACTORS
# =====================================================
EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
PHONE_REGEX = r"\+?\d{7,15}"
YEAR_REGEX = r"(\d{4})"


def extract_email(text):
    m = re.search(EMAIL_REGEX, text)
    return m.group(0) if m else None


def extract_phone(text):
    clean = text.replace(" ", "")
    m = re.search(PHONE_REGEX, clean)
    return m.group(0) if m else None


def extract_years_of_experience(text):
    numeric = re.search(r"(\d+)\+?\s+years", text.lower())
    if numeric:
        return int(numeric.group(1))

    years = re.findall(YEAR_REGEX, text)
    years = sorted(list(set([int(y) for y in years if int(y) < 2050])))

    if len(years) >= 2:
        return max(years) - min(years)

    return None


# =====================================================
# 3. SKILLS LIST + SIMPLE BASELINE MATCHER
# =====================================================
SKILLS = [
    "python", "sql", "pandas", "numpy",
    "machine learning", "deep learning",
    "tensorflow", "keras", "nlp",
    "power bi", "tableau", "excel",
    "react", "node", "aws", "docker",
    "flask", "django", "fastapi"
]


def extract_skills(text):
    text_lower = text.lower()
    return list({s for s in SKILLS if s in text_lower})


# =====================================================
# 4. NAME & EDUCATION (spaCy)
# =====================================================
def extract_name(text):
    first_line = text.split("\n")[0]
    doc = nlp(first_line)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return None


def extract_education(text):
    keywords = ["B.Tech", "BSc", "B.Sc", "BE", "B.E", "M.Tech",
                "MSc", "M.Sc", "BCA", "MCA", "Bachelor", "Master"]
    lines = text.split("\n")
    return [line for line in lines if any(k.lower() in line.lower() for k in keywords)]


# =====================================================
# 5. RULE-BASED PARSE
# =====================================================
def rule_based_parse(text):
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "explicit_skills": extract_skills(text),
        "years_experience": extract_years_of_experience(text),
        "education_entries": extract_education(text),
        "raw_text": text[:6000]
    }


# =====================================================
# 6. LLM ENHANCEMENT USING GROQ (NO HALLUCINATIONS)
# =====================================================
def llm_enhance(parsed, text):
    prompt = f"""
    Extract structured JSON from this resume.

    STRICT RULES:
    - NO hallucinations.
    - Only infer skills from summary, responsibilities, projects.
    - Do NOT assume AWS/Azure/GCP from vague terms like "deployment".
    - If information is uncertain → leave field empty.
    - Use only clear, factual content present in the resume.

    Return JSON with keys:
    - name
    - email
    - phone
    - explicit_skills
    - inferred_skills
    - all_skills
    - years_experience
    - experience: [{{"title": "", "company": "", "start": "", "end": ""}}]
    - education: [{{"degree": "", "institution": "", "year": ""}}]

    Resume Text:
    {text}

    Initial Parsed:
    {parsed}
    """

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    output = response.choices[0].message.content

    try:
        return json.loads(output)
    except:
        return parsed
