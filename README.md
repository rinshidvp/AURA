# AURA — Autonomous University Response and Action

[![CI/CD Pipeline](https://github.com/rinshidvp/AURA/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/rinshidvp/AURA/actions/workflows/ci-cd.yml)
[![Live Web Portal](https://img.shields.io/badge/Vercel-aura--campus--three.vercel.app-6366f1?logo=vercel&logoColor=white)](https://aura-campus-three.vercel.app)
[![Java 17](https://img.shields.io/badge/Java-17%20SE-ED8B00?logo=openjdk&logoColor=white)](https://www.oracle.com/java/technologies/javase/jdk17-archive-downloads.html)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E?logo=supabase&logoColor=white)](https://supabase.com)
[![Course](https://img.shields.io/badge/KTU-CST205%20%2F%20CSL203-blue)](https://ktu.edu.in)

> *"REPORT. TRACK. RESOLVE. IMPROVE."*  
> **Department of Computer Science & Engineering, TKM College of Engineering (TKMCE)**  
> Academic Course: APJ Abdul Kalam Technological University (KTU) CST205 / CSL203 — Advanced Programming Java Project  
> **Live Web & Mobile Portal:** [https://aura-campus-three.vercel.app](https://aura-campus-three.vercel.app)

---

## 1. Project Overview

**AURA** is an enterprise-grade campus issue and suggestion governance platform developed for TKM College of Engineering. It replaces fragmented, untracked channels (WhatsApp groups, paper suggestion boxes, and flat Google Forms) with a structured, transparent, and crowd-prioritized system.

### Core Value Propositions:
1. **Anonymous Campus Reporting:** Students can report infrastructural defects and campus suggestions without fear of reprisal. Identity is protected through a **Decoupled Anonymity Vault** at the database level.
2. **Crowd Prioritization (Hype Engine):** Students upvote issues they also experience, pushing high-impact problems to the top of the **Trending** list.
3. **5-State Resolution Pipeline:** Transparent administrative lifecycle (`PENDING → ASSIGNED → IN_PROGRESS → RESOLVED / REJECTED`) with official resolution notes visible to students.
4. **100% Java Desktop Architecture:** Built with **Java 17 (SE)**, modern **FlatLaf** desktop GUI, **JDBC DAO patterns**, and cloud-hosted **Supabase PostgreSQL**.

---

## 2. Master Documentation Index

Every component of AURA is rigorously documented and directly aligned with the faculty-approved Phase 1 presentation:

| Document | Key Information Answered | Approved Presentation Reference |
|---|---|---|
| [`docs/AURA.pdf`](docs/AURA.pdf) | **Official approved Phase 1 presentation deck** (UML Use Cases, Class Diagram, Sequence Diagram, Mockups) | Full 30-Slide Deck |
| [`AGENT.md`](AGENT.md) | Engineering rules, layer boundaries, and Definition of Done for coding sessions | General |
| [`docs/PRD.md`](docs/PRD.md) | Problem statement, UN SDGs (16, 11, 9, 4), and UML Use Case Model (Slide 7) | Slides 3–7 |
| [`docs/TRD.md`](docs/TRD.md) | Technical stack, NFRs, and mapping to KTU CST205/CSL203 syllabus | Slides 2, 15 |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | 4-Layer design, UML Class Diagram (Slide 14), Sequence Diagram (Slide 11), Anonymity Vault | Slides 11–15 |
| [`docs/DATABASE.md`](docs/DATABASE.md) | Relational ER diagram (Slide 13/24), data dictionary, performance indexes, Supabase setup | Slides 13, 24 |
| [`docs/SECURITY.md`](docs/SECURITY.md) | Domain gating (`@tkmce.ac.in`), BCrypt hashing, and Anonymity Vault mathematical proof | Slides 9, 10, 16 |
| [`docs/TESTING.md`](docs/TESTING.md) | Automated JUnit 5 test suites and administrative anonymity regression verification | Slides 15, 28 |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | 10-Week schedule (Slide 28) with Planned vs. Completed verification matrix | Slide 18, 28 |
| [`docs/VIVA_DEFENSE_GUIDE.md`](docs/VIVA_DEFENSE_GUIDE.md) | **Phase 2 Viva Voce Defense Guide** (Slide-by-slide Q&A for all 5 team members & Golden Path script) | Slides 1–30 |

---

## 3. Team Members & Slide Assignments (Slide 1 & 17)

All deliverables and modules map directly to the approved presentation assignments from Slide 17 of [`docs/AURA.pdf`](docs/AURA.pdf):

| Member | University Reg No | Role | Presentation Slides | Module Ownership |
|---|---|---|---|---|
| **Muhammed Rinshid VP** | B25CSB45 | **Team Lead** | Slides 1–4, 20 | System Coordination, Core Architecture, Supabase Integration, Presentation Lead |
| **Nirmal Binoy** | B25CSB52 | **Core Developer** | Slides 5–8 | Proposed Solution, UML Class Modeling, Hype/Trending Engine (`HypeService`) |
| **Mohammed Nafih** | B25CSB37 | **Core Developer** | Slides 9–12 | RBAC Security Pipeline, Anonymity Vault (`AuthService`, `StudentReceiptDAO`) |
| **Rahandeep RD** | B25CSB53 | **Database & GUI Engineer** | Slides 13–14, 18 | PostgreSQL Schema (`schema.sql`), FlatLaf Desktop UI (`aura.ui.student.*`, `SubmissionDAO`) |
| **Athil Rahuman A** | B25CSB84 | **Documentation & Process Lead** | Slides 15–17, 19 | Audit Lifecycle (`TrackingService`, `ReportService`), Progress Tracking, CSV Export |

---

## 4. Quickstart Setup Guide

### Prerequisites:
- **JDK 17** or higher installed and configured on PATH (`java -version`).
- **Apache Maven 3.9+** (`mvn -version`).
- **Supabase Cloud Account** or local PostgreSQL 15+ database instance.

### Setup Instructions:

```bash
# 1. Clone repository
git clone https://github.com/rinshidvp/AURA.git
cd AURA

# 2. Apply Database Schema and Seed Data in Supabase SQL Editor
# Execute sql/schema.sql followed by sql/seed.sql

# 3. Configure Database Credentials
cp src/main/resources/db.properties.example src/main/resources/db.properties
# Edit db.properties with your Supabase JDBC connection string and password

# 4. Run Automated Unit & Regression Tests
mvn test

# 5. Launch the Modern FlatLaf Desktop Application
mvn exec:java
```

---

## 5. Demo Credentials (from Presentation Mockups Slide 21)

| Persona | Email | Password | Role |
|---|---|---|---|
| **Student 1** | `student1@tkmce.ac.in` | `password123` | STUDENT |
| **Student 2** | `student2@tkmce.ac.in` | `password123` | STUDENT |
| **Administrator** | `admin@tkmce.ac.in` | `admin123` | ADMIN |
| **Estate Officer** | `estate@tkmce.ac.in` | `admin123` | ADMIN |
