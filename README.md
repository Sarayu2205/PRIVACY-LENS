# 🔒 PrivacyLens — AI-Based Detection and Prevention of Sensitive Data Exposure

> **B.Tech Cybersecurity Project** | Full-Stack Web Application

---

## Project Description

PrivacyLens is a preventive cybersecurity application that detects sensitive information **before** a user shares a document, image, text, or source-code file. It uses regular expressions, entropy analysis, and NLP (spaCy) to identify 15+ categories of sensitive data, calculates a risk score, masks the data, and generates a downloadable PDF security report.

---

## Problem Statement

People frequently share documents containing sensitive information — credentials, government IDs, financial data, API keys — without realizing the risk. PrivacyLens intercepts this before it happens by scanning content and warning the user.

---

## Objectives

1. Detect sensitive data across 15+ categories using pattern matching + NLP
2. Assign a transparent, explainable risk score (0–100)
3. Mask detected values and generate a sanitized document
4. Generate a downloadable PDF security report
5. Store scan history for user review
6. Provide a professional cybersecurity-themed UI

---

## Features

| Feature | Description |
|---|---|
| **File Upload Scanning** | Scan TXT, PDF, DOCX, PNG, JPG files |
| **Text Scanner** | Paste text directly to scan |
| **OCR** | Extract text from images using Tesseract |
| **15+ Detectors** | Email, Phone, PAN, Aadhaar, Card (Luhn), Bank Account, Password, API Key (entropy), JWT, Private Key, Address, DOB, IFSC |
| **NLP Enhancement** | spaCy NER for person name detection + context analysis |
| **Risk Scoring** | Transparent formula, 0–100 score, 4 severity levels |
| **Data Masking** | Type-specific masking (e.g. `s******@gmail.com`) |
| **PDF Reports** | Professional downloadable reports (ReportLab) |
| **Scan History** | Paginated, searchable, filterable scan history |
| **Auth** | JWT authentication, bcrypt password hashing |
| **Dashboard** | Stats cards + charts (Recharts) |

---

## Architecture

```
PrivacyLens/
├── frontend/              React + Vite + Tailwind CSS
│   └── src/
│       ├── pages/         Login, Register, Dashboard, Scan, Results, History, Report, Profile
│       ├── components/    Layout, FindingsTable, RiskMeter, StatCard, RiskBadge
│       ├── services/      API client (Axios)
│       ├── context/       AuthContext (JWT)
│       └── utils/         Helpers
├── backend/               Python + FastAPI
│   └── app/
│       ├── detectors/     12 individual detector modules + master scanner
│       ├── processors/    TXT, PDF, DOCX, Image/OCR handlers
│       ├── services/      ScanService, RiskAnalyzer, MaskingService, NLPService, ReportService
│       ├── routes/        auth, scan, history, dashboard, report
│       ├── models/        SQLAlchemy ORM (User, Scan, Finding, Report)
│       ├── schemas/       Pydantic v2 schemas
│       └── security/      bcrypt hashing, JWT handler
├── database/              schema.sql (MySQL)
├── sample_data/           Synthetic test files
└── reports/               Generated PDF reports (auto-created)
```

---

## Technologies

**Backend:** Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, PyMySQL, Pydantic v2  
**Auth:** python-jose (JWT), passlib + bcrypt  
**Detection:** Python `re`, Shannon entropy, spaCy `en_core_web_sm`  
**File Processing:** PyMuPDF (PDF), python-docx (DOCX), pytesseract + Pillow (OCR)  
**Reports:** ReportLab  
**Frontend:** React 18, Vite, Tailwind CSS, React Router v6, Axios, Recharts  
**Database:** MySQL 8.0 (SQLite for tests)  
**Testing:** pytest, HTTPX (TestClient)

---

## Risk Scoring Formula

| Type | Weight | Severity |
|---|---|---|
| PASSWORD, API_KEY, JWT_TOKEN, PRIVATE_KEY, CREDIT_CARD, BANK_ACCOUNT | 20 | CRITICAL |
| PAN, AADHAAR, DATE_OF_BIRTH | 15 | HIGH |
| PHONE, ADDRESS, IFSC_CODE | 10 | MEDIUM |
| EMAIL, PINCODE | 5 | LOW |

**Formula:** `score = Σ(type_weight × confidence)` capped at 100  
**Levels:** 0–24 LOW · 25–49 MEDIUM · 50–74 HIGH · 75–100 CRITICAL

---

## Installation & Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- MySQL 8.0
- Tesseract OCR (for image scanning)

### 1. Tesseract Installation (Windows)

Download from: https://github.com/UB-Mannheim/tesseract/wiki  
Add to PATH or set in pytesseract config.

### 2. Database Setup

```sql
-- In MySQL CLI or MySQL Workbench:
mysql -u root -p < database/schema.sql
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Create .env file
copy ..\.env.example .env
# Edit .env with your MySQL credentials and JWT secret

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### 5. Access the Application

- **Frontend:** http://localhost:5173
- **API docs:** http://localhost:8000/docs
- **ReDoc:**     http://localhost:8000/redoc

---

## Environment Variables

Copy `.env.example` to `backend/.env` and configure:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/privacylens
JWT_SECRET=your-long-random-secret-here
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=10
REPORTS_DIR=reports
SPACY_MODEL=en_core_web_sm
```

Generate a JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | Login, get JWT |
| GET | `/api/auth/me` | Yes | Get current user |
| POST | `/api/scan/text` | Yes | Scan pasted text |
| POST | `/api/scan/file` | Yes | Upload & scan file |
| GET | `/api/scan/{id}` | Yes | Get scan + findings |
| DELETE | `/api/scan/{id}` | Yes | Delete scan |
| POST | `/api/scan/{id}/mask` | Yes | Mark as masked |
| GET | `/api/scans` | Yes | Paginated scan history |
| GET | `/api/dashboard/stats` | Yes | Dashboard statistics |
| GET | `/api/report/{id}/generate` | Yes | Generate PDF report |
| GET | `/api/report/{id}/download` | Yes | Download PDF report |
| GET | `/api/health` | No | Health check |

Full interactive docs: http://localhost:8000/docs

---

## Running Tests

```bash
cd backend

# Activate venv first
venv\Scripts\activate

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_detectors.py -v
pytest tests/test_api.py -v
```

Tests use SQLite in-memory DB — no MySQL required for testing.

---

## Sample Test Data

**Test the scanner:**

1. Go to **Text Scanner** page
2. Click "Load sample sensitive data →" for pre-filled test data
3. Click **Scan Text**

Or upload `sample_data/sample_sensitive.txt` on the **Scan Document** page.

**Expected results for sample_sensitive.txt:**
- EMAIL detected (arjun.kumar@example.com)
- PHONE detected (+91 9876543210)
- PAN detected (ABCDE1234F)
- AADHAAR detected (2345 6789 0123)
- CREDIT_CARD detected (4111 1111 1111 1111)
- API_KEY detected (multiple)
- JWT_TOKEN detected
- PRIVATE_KEY detected
- Risk Level: CRITICAL
- Risk Score: ~100

---

## Sample Credentials

Register a new account on the Register page. There are no pre-seeded accounts — all accounts are created by users. Example:

```
Name: Demo User
Email: demo@example.com
Password: Demo@12345
```

---

## Known Limitations

1. **Tesseract OCR** quality depends on image clarity — blurry images may not extract well
2. **spaCy NER** person-name detection has false positives on certain proper nouns
3. **Address detection** uses context-based patterns — very unusual address formats may be missed
4. **Phone numbers** embedded in larger numbers (e.g. order IDs) may occasionally trigger
5. **No 2FA** — single-factor auth only in this demo version

---

## Future Enhancements

- [ ] Two-factor authentication (TOTP)
- [ ] Bulk file scanning
- [ ] Custom pattern configuration per user
- [ ] Browser extension for real-time detection
- [ ] REST API rate limiting
- [ ] Email notifications for high-risk scans
- [ ] Fine-tuned ML model for credential detection
- [ ] Integration with Google Drive / OneDrive
- [ ] LDAP/SSO authentication
- [ ] Multi-language support

---

## Project Info

**Title:** PrivacyLens — AI-Based Detection and Prevention of Sensitive Data Exposure  
**Domain:** Cybersecurity / Data Security / Privacy Protection  
**Type:** B.Tech Final Year Project  
**Stack:** Python + FastAPI + React + MySQL  
**License:** MIT (for educational use)

---

*This project uses only synthetic test data. No real personal information is stored or processed in the sample files.*
