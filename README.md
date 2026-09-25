# 🏥 RehabShield — Stroke Rehabilitation & Movement Analysis System

**Official Project Title**:  
*"Machine Learning-Based Gait and Upper Limb Motor Impairment Analysis for Stroke Rehabilitation"*

[![React 18](https://img.shields.io/badge/React-18.0-61DAFB?style=for-the-badge&logo=react)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.4-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)
[![MediaPipe](https://img.shields.io/badge/MediaPipe-Pose_Estimation-FF6F00?style=for-the-badge&logo=google)](https://mediapipe.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-Machine_Learning-F7931E?style=for-the-badge&logo=scikit-learn)](https://scikit-learn.org/)

**RehabShield** is a scientifically defensible, monocular computer-vision and machine-learning decision-support framework designed for quantitative movement analysis and longitudinal stroke rehabilitation monitoring.

> **Ethical & Research Mandate**: *RehabShield is a research prototype for movement analysis and rehabilitation support. It is not a clinical diagnostic device. Outputs do not replace professional medical judgment.*

---

## 🏗️ System Architecture & Major Execution Streams

RehabShield operates as a decoupled full-stack architecture structured into three distinct execution streams:

1. **Layer A — Application Computer Vision Video Pipeline**:
   * Accepts user-uploaded MP4 video clips.
   * Runs OpenCV frame decoding + MediaPipe Tasks 33 3D Pose Landmark tracking.
   * Calculates joint angles (shoulder, elbow, hip, knee), range of motion (ROM), and movement parameters.
   * Dynamically separates lower-limb gait step detection (`movement_type="gait"`) from upper-limb exercise kinematics (`movement_type="upper_limb"`).

2. **Layer B — Research Machine Learning Evaluation Modules**:
   * **Study37 / StrokeRehab Dataset**: Standalone research benchmark for 5-class functional primitive recognition (*Rest, Reach, Transport, Stabilize, Reposition*) using 431 released video features and majority-vote temporal smoothing (window = 9).
     * *Validation Accuracy*: **69.24%** (Macro F1 = 0.6593)
     * *Final Held-out Test Accuracy*: **63.92%** (Macro F1 = 0.6233)
     * *Raw Test Accuracy*: **59.07%** (Macro F1 = 0.5748)
   * **Study36 Dataset**: Dataset-derived healthy-control movement reference characteristics (1,426 CSV files across 20 healthy subjects sampled at 100 Hz).
   * **Upper-Limb Exercise Video Dataset**: Binary exercise completion evaluation (*Complete* vs. *Incomplete*) across 491 videos (411 Train, 80 Test).

3. **Layer C — Patient Longitudinal Monitoring**:
   * Tracks patient session progress across multiple visits (Session 1, Session 2, Session 3, Session 4).
   * Computes exact quantitative deltas in physical units (e.g. `Elbow ROM change: +12.5°`, `Shoulder Mobility: +8.4°`).

---

## 📊 Three Research Datasets & Their Roles

| Dataset | Location | Structure | Scientific Role | Verified Benchmark Metrics |
|---|---|---|---|---|
| **Study36** | `data/study36-2026-09-08-07-53.zip` | 1,426 CSVs, 20 healthy subjects, 106 joint columns at 100 Hz | Dataset-derived healthy-control movement reference characteristics | Baseline joint ROMs & bilateral symmetry ratios |
| **Study37 / StrokeRehab** | `data/study37-2026-09-08-08-09.zip` | 3,058 trials across 51 subjects, 431 released features | Standalone Research ML Benchmark (5 Functional Primitives) | **69.24% Val Acc** \| **63.92% Held-out Test Acc** |
| **Upper Limb Video Dataset** | `data/An upper limb stroke rehabilitation exercise video.zip` | 491 MP4 videos (411 Train, 80 Test) across 4 exercises | Video-Based Upper-Limb Exercise Completion Evaluation | Complete vs. Incomplete exercise classification |

---

## 🚀 Quick Start & How to Run

### Prerequisites
* **Python 3.10+** (Python 3.11 / 3.12 / 3.14 supported)
* **Node.js 18+** & `npm`

### Standard Launcher (Runs FastAPI Backend + Vite React Frontend)
```bash
python run_app.py
```
* **Frontend Web App**: `http://localhost:8080` (or `http://localhost:5173`)
* **Backend Swagger API**: `http://localhost:8080/docs`

### Manual Dual-Terminal Setup
```bash
# Terminal 1 — Backend API
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8080

# Terminal 2 — Frontend Dev Server
cd frontend
npm run dev
```

---

## 🔑 Default Clinician Credentials

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Head Physiotherapist** | `therapist` | `therapist123` | Conducts video movement scans, reviews joint ROM, prescribes exercise programs |
| **Consulting Doctor** | `doctor` | `doctor123` | Validates clinical assessment scores (FMA/BBS), downloads signed PDF reports |
| **System Administrator** | `admin` | `admin123` | System configuration, user management, and health monitoring |

---

## 🧪 Testing & Verification

Run the automated backend diagnostic suite:
```bash
python test_backend.py
```
Run frontend production build verification:
```bash
cd frontend
cmd /c npm run build
```

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
