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
```
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
```
{
  "score": 0-100,
  "skill_match": [],
  "missing_skills": [],
  "overqualified": false,
  "underqualified": false,
  "final_recommendation": "SELECT | REVIEW | REJECT"
}
```
## 📊 4. Google Sheets Integration
### The workflow reads job role details from a Google Sheet:
Job ID
Required Skills
Preferred Skills
Min/Max Experience
Job Description

### Another sheet stores:
Candidate info
Score
AI recommendation
HR notes

## 📧 5. Automated Emails
Based on AI decision:
- SELECT → Warm acceptance email
- REVIEW → HR manual review email
- REJECT → Polite rejection email
Emails are fully generated and sent automatically.

🔄 6. End-to-End Automation in n8n

## The n8n workflow includes:
- Webhook trigger
- Resume upload → FastAPI
- Google Sheets lookup
- scoring (JavaScript node)
- Decision engine
- Email automation
- Candidate storage
Everything happens automatically once the candidate submits the form.

🏗️ Project Structure
```bash
/resume-parser-backend
│── main.py              # FastAPI server
│── parser.py            # Resume extraction & LLM enhancement
│── requirements.txt
│── .env                 # GROQ_API_KEY etc.

/frontend
│── index.html           # Tailwind form (Netlify deployed)

/n8n-workflow.json       # Exported workflow (optional)
```
💡 Tech Stack
- FastAPI
- n8n (Automation engine)
- Groq LLM
- Cloudflare Tunnel(for making the API live)
- Google Sheets API
- TailwindCSS
- Netlify (frontend hosting)
---
🚀 How to Run Locally

1. Clone the repo:
```
git clone https://github.com/YOUR-USERNAME/automated-hiring-system.git
```
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Add environment variables:
```
GROQ_API_KEY=your_key_here
```
4. Run FastAPI:
```
uvicorn main:app --reload --port 8000
```
5. Expose API publicly:
```
cloudflared tunnel --url http://127.0.0.1:8000
```
6. Import workflow into n8n

7. Deploy HTML form on Netlify
