# 🚀 Automated Hiring Workflow (n8n + FastAPI + AI Resume Parser)

A fully automated hiring pipeline built using **FastAPI**, **n8n**, **Cloudflare Tunnel**, and **AI-powered scoring**.  
This system parses resumes, evaluates candidates using structured scoring logic, updates Google Sheets, and sends automated emails — all with zero manual effort.

---

## 🔥 Features

### ✅ **1. Resume Upload Form (Tailwind + Netlify)**
- Clean UI built with TailwindCSS  
- Candidates can submit:
  - Full Name  
  - Email  
  - Job ID  
  - Resume (PDF/DOCX)  
- Resume goes directly to n8n webhook

### ✅ **2. FastAPI Resume Parsing**
FastAPI backend includes:
- PDF/DOCX extraction  
- Rule-based resume parsing  
- LLM enhancement using **Groq LLM**  
- Clean JSON output (name, email, phone, skills, experience)

Run the API:
```bash
uvicorn main:app --reload --port 8000
🧠 3. AI Scoring Engine (Custom JavaScript Logic)

Instead of unpredictable LLM scoring, the workflow uses deterministic scoring rules, including:

- Required skill match (weighted)
- Preferred skill match
- Project detection
- Domain detection
- Fresher-friendly scoring boosts
- Overqualified / underqualified logic
- Experience validation

Outputs:

{
  "score": 0-100,
  "skill_match": [],
  "missing_skills": [],
  "overqualified": false,
  "underqualified": false,
  "final_recommendation": "SELECT | REVIEW | REJECT"
}

📊 4. Google Sheets Integration

#### The workflow reads job role details from a Google Sheet:
Job ID
Required Skills
Preferred Skills
Min/Max Experience
Job Description

#### Another sheet stores:
Candidate info
Score
AI recommendation
HR notes
