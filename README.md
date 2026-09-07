# 🏥 RehabShield: ML-Based Stroke Rehabilitation Decision Support System

[![React 19](https://img.shields.io/badge/React-19.0-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose_Estimation-FF6F00?style=for-the-badge&logo=google)](https://mediapipe.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine_Learning-F7931E?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED?style=for-the-badge&logo=docker)](https://www.docker.com/)

An AI-assisted **Stroke Rehabilitation Clinical Decision Support System (CDSS)** developed for quantitative motor impairment evaluation. The platform helps physiotherapists and neurologists objectively monitor gait symmetry, joint range of motion (ROM), and upper-limb spasticity using computer vision and machine learning.

> **Clinical Disclaimer**: *RehabShield is an objective decision-support tool designed to assist clinicians. Final diagnostic, pharmacological, and treatment decisions must always be made by qualified healthcare professionals.*

---

## 🌟 Key Features

* **🎥 Hardware-Accelerated Pose Estimation (MediaPipe WebAssembly)**:
  * Client-side WebGL pose tracker detecting 33 spatial anatomical landmarks.
  * Completely offline-enabled without external CDN dependencies.
* **📐 Biomechanical Kinematics Engine**:
  * Real-time extraction of Knee Flexion, Hip Extension, Shoulder Elevation, and Elbow Spasticity angles.
  * Calculation of Cadence (steps/min), Stride Length (m), Walking Speed (m/s), Step Symmetry Ratio, and Lateral Trunk Sway (Balance Stability %).
* **🤖 Multi-Model Machine Learning Impairment Classifier**:
  * Evaluates motor recovery into clinical severity tiers: *Normal, Mild, Moderate, Severe, Very Severe*.
  * Supports ensemble **Random Forest**, **Support Vector Machines (SVM)**, and **Gradient Boosting (XGBoost fallback)** with feature importance weight visualization.
* **💊 Intelligent Exercise Prescription & Home Program**:
  * Translates measured kinematic deficits directly into targeted exercise protocols with specific dosages, intensity levels, and clinical rationales.
* **📊 Longitudinal Progress & Trend Analytics**:
  * Interactive Recharts area and multi-series curves tracking motor recovery across multi-month clinical sessions.
* **📑 ReportLab Vector PDF Clinical Reporting**:
  * One-click generation of comprehensive clinical diagnostic reports with standardized scales (Fugl-Meyer, Berg Balance, TUG), demographic data, and clinician signature blocks.
* **🔐 Role-Based Access Control (RBAC)**:
  * Distinct authorization profiles for **Physiotherapists**, **Consulting Doctors / Neurologists**, and **System Administrators**.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Client [Vite React 19 Frontend - Port 5173]
        UI[Medical Dashboards & Patient Profiles]
        MP[MediaPipe WebAssembly Pose Engine]
        SVG[Dynamic SVG Skeleton Viewer]
        CMath[Kinematic Math - Joint Angles, Gait metrics]
    end

    subgraph API [FastAPI Backend - Port 8000]
        Auth[JWT Role Authorization Middleware]
        CRUD[Patient Registry & Assessment CRUD]
        ML[ML Classifier Engine - RF, SVM, XGBoost]
        PDF[ReportLab PDF Compiler]
    end

    subgraph Storage [Database Tier]
        Mongo[(MongoDB)]
        JSONDb[(Thread-Locked JSON Mock DB Fallback)]
    end

    %% Flow lines
    UI -->|1. Upload Gait Video| MP
    MP -->|2. Extract coordinates frame-by-frame| CMath
    CMath -->|3. Calculate joint ROM & Stride| SVG
    CMath -->|4. Post authenticated JSON features| Auth
    Auth -->|5. Validate session| CRUD
    CRUD -->|6. Run prediction query| ML
    CRUD -->|7. Generate clinical report| PDF
    CRUD -->|8. Read/Write records| Mongo
    CRUD -.->|Fallback| JSONDb
    PDF -->|9. Stream authenticated binary blob| UI
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
* **Python 3.10+** (Python 3.11/3.12/3.14 supported)
* **Node.js 18+** & `npm`

### 1. Clone the Repository
```bash
git clone https://github.com/SumitKSinghDev/Stroke-Rehabilitation-Analysis-System.git
cd Stroke-Rehabilitation-Analysis-System
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend server
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```
Backend Swagger API documentation will be live at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite React development server
npm run dev
```
Open your browser at: `http://localhost:5173`

---

## 🔑 Default Clinician Credentials

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Head Physiotherapist** | `therapist` | `therapist123` | Conducts video scans, reviews joint ROM, prescribes exercises |
| **Consulting Doctor** | `doctor` | `doctor123` | Validates clinical scales (FMA/BBS), downloads signed PDF reports |
| **System Administrator** | `admin` | `admin123` | Manages hospital accounts, audit logs, and diagnostic health |

*(Quick 1-click login buttons are also provided directly on the login screen for easy viva demonstration).*

---

## 🐳 Docker Deployment

To build and run the entire application containerized:
```bash
docker-compose up --build
```
Access the application at `http://localhost:8000`.

---

## 🛠️ Tech Stack Overview

* **Frontend**: React 19, TypeScript, Tailwind CSS, Lucide React, Framer Motion, Recharts, Vite.
* **Backend**: FastAPI, Pydantic v2, Scikit-learn, ReportLab, OpenCV, NumPy, Bcrypt, Python-Jose.
* **Computer Vision**: MediaPipe Pose (WebAssembly / WebGL client execution).
* **Storage**: MongoDB with automatic thread-locked JSON local fallback.

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
