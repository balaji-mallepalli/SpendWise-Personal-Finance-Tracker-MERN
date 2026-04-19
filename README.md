# 💰 SpendWise - Personal Finance Tracker

A premium, full-stack personal financial tracking ecosystem designed with a focus on professional aesthetics and robust ledger auditing. SpendWise empowers users to take control of their finances through encrypted account management, dynamic budgeting, and real-time data visualization.

---

## 📺 Project Overview

SpendWise is built around a **Monochrome Glassmorphism** design language, providing a sleek, distraction-free environment for financial analysis. It leverages a decoupled modern tech stack to ensure high performance and mobile responsiveness.

### ✨ Key Features
- **Secure Authentication**: JWT-based session management with Bcrypt password hashing.
- **Multi-Account Management**: Track Bank accounts, Cash, and Digital Wallets in one place.
- **Categorized Transactions**: Log income and expenses with automated balance updates.
- **Smart Budgeting**: Set monthly limits per category and receive visual alerts as you approach thresholds.
- **Dashboard Analytics**: Interactive circular charts and trend lines for immediate spending insight.
- **Data Export**: Download your entire financial ledger as a CSV for local auditing.

---

## 📚 SE/PM Course Deliverables
All functional, structural, and behavioral modeling diagrams required for **Software Engineering & Project Management** evaluation are natively rendered in this repository.

> [!IMPORTANT]
> **[0. Software Requirements Spec (SRS)](docs/SRS.md)** - Full 830-compliant IEEE documentation.

- 🏗️ **[1. Functional Model & DFDs](docs/1_FUNCTIONAL_MODEL.md)**: (Context DFD, Level 1 DFD, Data Dictionary, Structured Hierarchy).
- 👤 **[2. User View Analysis](docs/2_USER_VIEW.md)**: (Use Case Diagram, Use Case Scenarios).
- 🧬 **[3. Structural View Diagrams](docs/3_STRUCTURAL_VIEW.md)**: (Class Diagram, Object State Diagram, Package Architecture).
- ⚡ **[4. Behavioral View Diagrams](docs/4_BEHAVIORAL_VIEW.md)**: (Sequence, Communication, State-Chart, Activity Workflows).
- 🌐 **[5. Implementation & Environment Views](docs/5_IMPLEMENTATION_AND_ENV_VIEW.md)**: (Component Diagram, Hardware Deployment Network).

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React (Vite), Tailwind CSS v4, Recharts, Framer Motion |
| **Backend** | FastAPI (Python), Motor (Async MongoDB Driver), Pydantic |
| **Database** | MongoDB Atlas (Cloud) |
| **Testing** | Pytest (Backend), Vitest (Frontend) |
| **Auth** | JWT (JSON Web Tokens), Bcrypt Hashing |

---

## 🚀 Getting Started

### Prerequisites
- Node.js (v20+)
- Python (3.11+)
- MongoDB connection string (Atlas or Local)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Activate venv: .\venv\Scripts\activate (Win) or source venv/bin/activate (Unix)
pip install -r requirements.txt
cp .env.example .env
# Update .env with your MONGODB_URL and SECRET_KEY
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Quality Assurance & Testing

SpendWise maintains a rigorous testing suite to ensure ledger integrity and UI stability.

**Backend (API Logic)**
```bash
cd backend
pytest tests/ -v
```

**Frontend (UI Components)**
```bash
cd frontend
npm run test
```

---

## ☁️ Deployment Status
Prepare your environment for production deployment (Render & Vercel) by following the **[Deployment Guide](docs/DEPLOYMENT.md)**.

- **Backend (API)**: [Pending Deployment]
- **Frontend (UI)**: [Pending Deployment]

---

*Developed for academic evaluation in Software Engineering.*
