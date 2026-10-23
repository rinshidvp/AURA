# AURA — Phase 2 Viva Defense & Project Sign-Off Guide

> **Autonomous University Response and Action**  
> Department of Computer Science & Engineering, TKM College of Engineering (TKMCE)  
> Academic Course: APJ Abdul Kalam Technological University (KTU) CST205 / CSL203 — Object Oriented Programming in Java  
> Presentation Reference: [`docs/AURA.pdf`](AURA.pdf) (Slide 1–30)

> **Final evaluation (Oct 2026):** this guide records the Phase 2 sign-off. For the final deck, running order and updated viva answers, use [`docs/presentation/final/SPEAKER_RUNSHEET.md`](presentation/final/SPEAKER_RUNSHEET.md). Google OAuth was retired after Phase 2; both apps now use email/password sign-in.

---

## 1. Executive Version 1 Completion Statement

As of **September 10, 2026**, **AURA Version 1 (Phase 2 MVP)** is formally **complete, verified, and signed off**.

### Verification Summary
- **Unit & Regression Tests:** 14 automated JUnit 5 tests executed with **0 errors, 0 failures, 0 regressions**.
- **Security Audit:** `AdminAnonymityRegressionTest` passes, mathematically and structurally proving zero leakages of student identities to administrative code paths.
- **Database Architecture:** Cloud-hosted **Supabase PostgreSQL 17.6** with 6 relational tables, strict foreign keys, cascading deletions, and multi-host DNS resilience.
- **Modern GUI:** 100% pure Java SE FlatLaf desktop interface supporting live Student Portal and Admin Governance Dashboard.

---

## 2. Team Member Viva Defense Matrix (Slide 17 Alignment)

Every team member has dedicated module ownership derived from Slide 17 of [`docs/AURA.pdf`](AURA.pdf). The following questions and technical answers must be defended by the assigned member during the viva voce.

```
========================================================================================
TEAM MEMBER 1: MUHAMMED RINSHID VP (B25CSB45) — TEAM LEAD & SYSTEM COORDINATOR
Slides Owned: 1–4, 20 | Module: Core Architecture, DatabaseConfig, Web Portal & CI/CD
========================================================================================
```

### Q1.1: What is the core problem AURA solves, and which UN SDGs does it address?
> **Answer:**  
> "AURA replaces fragmented, untracked channels (WhatsApp groups, paper suggestion boxes, flat Google forms) with a structured, transparent, 5-state campus governance platform at TKMCE. It directly aligns with:
> - **SDG 16 (Peace, Justice and Strong Institutions):** Transparent, auditable campus grievance redressal.
> - **SDG 11 (Sustainable Cities and Communities):** Safe, accessible campus infrastructure and maintenance.
> - **SDG 9 (Industry, Innovation and Infrastructure):** Transition from archaic paper systems to modern Java SE architecture.
> - **SDG 4 (Quality Education):** Prevents lab and classroom downtime through swift issue resolution." (Slides 3–4)

### Q1.2: How is the database connection managed, and how do you handle cloud network failures?
> **Answer:**  
> "We implement a Singleton Connection Factory in `aura.config.DatabaseConfig` backed by HikariCP-compatible pooled JDBC connections to Supabase PostgreSQL 17.6. To guarantee high availability against intermittent ISP DNS hiccups, we configured a multi-host failover JDBC URL:
> `jdbc:postgresql://aws-0-ap-northeast-1.pooler.supabase.com:5432,54.64.190.72:5432/postgres?sslmode=require`
> If domain resolution hangs or fails, the PostgreSQL JDBC driver transparently fails over to the direct AWS ELB IP address without interrupting user operations."

---

```
========================================================================================
TEAM MEMBER 2: NIRMAL BINOY (B25CSB52) — CORE DEVELOPER (HYPE ENGINE & MODELING)
Slides Owned: 5–8 | Module: Proposed Solution, UML Class Modeling, HypeService, SubmissionHypeDAO
========================================================================================
```

### Q2.1: How does the Crowd Prioritization (Hype Engine) work, and how do you prevent double-voting?
> **Answer:**  
> "The Hype Engine aggregates community urgency. In `HypeService`, when a student upvotes an issue, it invokes `SubmissionHypeDAO.toggleHype(submissionId, studentId)`. At the database level, the `submission_hype` table enforces a composite unique constraint:
> `CONSTRAINT uq_submission_student UNIQUE (submission_id, student_id)`
> If the record already exists, it is deleted (toggle off); if it does not exist, an `INSERT` executes (toggle on). This guarantees mathematical idempotency and prevents vote manipulation." (Slide 8, 14)

### Q2.2: Explain the UML Class Model and the relationships between Submission, User, and Hype.
> **Answer:**  
> "The model follows clean OOP domain modeling in package `aura.model`:
> - `User` contains role-based attributes (`STUDENT` vs `ADMIN`).
> - `Submission` is an aggregate entity with strongly typed enums (`Category`, `Priority`, `SubmissionType`, `SubmissionStatus`).
> - Notably, `Submission` does NOT aggregate or reference `User` directly. This structural separation upholds the Decoupled Anonymity Vault." (Slide 14)

---

```
========================================================================================
TEAM MEMBER 3: MOHAMMED NAFIH (B25CSB37) — SECURITY & ANONYMITY VAULT LEAD
Slides Owned: 9–12 | Module: RBAC Pipeline, AuthService, StudentReceiptDAO, PasswordUtil
========================================================================================
```

### Q3.1: Prove that campus administrators cannot identify who submitted an issue.
> **Answer:**  
> "The proof is twofold:
> 1. **Relational Schema Isolation:** The `submissions` table contains NO `student_id` or `user_id` column. When a submission is inserted, only an anonymous ticket row is created.
> 2. **Decoupled Anonymity Vault:** The mapping between student and ticket is written to an isolated table, `student_submission_receipts (receipt_id, student_id, submission_id)`.
> 3. **Architectural Access Boundary:** `student_submission_receipts` is only accessible via `StudentReceiptDAO`, which is strictly invoked by `TrackingService` during the authenticated student's session. No administrative class (`aura.ui.admin.*` or `AdminSubmissionService`) contains any queries or methods referencing receipts.
> 4. **Automated Verification:** `AdminAnonymityRegressionTest` automatically inspects all admin queries to verify zero access to receipt records." (Slides 10, 11, 16)

### Q3.2: How are user credentials secured in transit and at rest?
> **Answer:**  
> "Passwords are salted and hashed using `jBCrypt` with a work factor of 10 in `PasswordUtil.hashPassword()`. Plaintext passwords never touch the database or exception logs. Institutional domain gating strictly validates that all logins and registrations match the regex `^[A-Za-z0-9._%+-]+@tkmce\\.ac\\.in$`." (Slide 9, 16)

---

```
========================================================================================
TEAM MEMBER 4: RAHANDEEP RD (B25CSB53) — DATABASE & GUI ENGINEER
Slides Owned: 13–14, 18 | Module: PostgreSQL Schema, FlatLaf Modern GUI, SubmissionDAO
========================================================================================
```

### Q4.1: Explain the layer boundaries between FlatLaf Swing UI and the Database.
> **Answer:**  
> "Our architecture follows a strict 4-tier model:
> `aura.ui (Swing)` → `aura.service` → `aura.dao` → `Supabase PostgreSQL`
> - `aura.ui` never imports `java.sql.*` and never touches `aura.dao`. All actions pass through service orchestrators.
> - `aura.dao` is the only package permitted to execute SQL queries.
> - Every DAO method uses `try-with-resources` to guarantee that `Connection`, `PreparedStatement`, and `ResultSet` are closed immediately, preventing connection leaks." (Slides 13, 14, 18)

### Q4.2: How does FlatLaf modernize the desktop experience over standard Swing?
> **Answer:**  
> "Standard Swing uses dated native widgets (Metal or Windows 98 aesthetic). In `aura.ui.common.UITheme`, we initialize `FlatDarkLaf`, providing high-DPI scaling, CSS-like rounded corners, modern color tokens (`BG_BASE #0F172A`, `PRIMARY #6366F1`), badge status pills, and responsive layout management." (Slide 20–23)

---

```
========================================================================================
TEAM MEMBER 5: ATHIL RAHUMAN A (B25CSB84) — DOCUMENTATION, TESTING & AUDIT LEAD
Slides Owned: 15–17, 19 | Module: State Lifecycle, ReportService, JUnit 5 Test Suite, CSV Export
========================================================================================
```

### Q5.1: What is the 5-State Resolution Pipeline and how is the audit trail maintained?
> **Answer:**  
> "Submissions progress through 5 deterministic states:
> `PENDING → ASSIGNED → IN_PROGRESS → RESOLVED / REJECTED`
> Whenever an administrator updates a status or attaches an official resolution explanation in `AdminDashboardFrame`, `ResolutionNoteDAO` logs the timestamp, admin ID, and resolution text. This note is immediately rendered back to the student in their 'My Submissions' panel, closing the feedback loop." (Slide 15, 19)

### Q5.2: How does the CSV Export feature work and how is it tested?
> **Answer:**  
> "`ReportService.generateCsvReport()` aggregates all submission records with category, priority, status, and hype counts. It formats records according to RFC-4180 specifications, properly escaping commas and quotes. In `SubmissionAndHypeServiceTest.testReportServiceCsvGeneration()`, we verify that the output contains all standard column headers and valid submission rows." (Slide 19, 28)

---

## 3. Golden-Path Live Demonstration Script (For Faculty Examiners)

Follow this uninterrupted 5-step demonstration during the presentation:

| Step | Persona | Action | Expected Visual Result |
|---|---|---|---|
| **1. Student Login** | `student1@tkmce.ac.in` | Enter email and password, click **Sign In** | Student Portal opens with personalized welcome and category statistics. |
| **2. Anonymous Submit** | Student 1 | Click **+ New Submission**, enter title *"Projector flickers in CSE Lab 3"*, select Category `ACADEMIC_LABS`, Priority `HIGH`, click **Submit Anonymously** | Dialog confirms receipt stored in private vault. Ticket appears in feed with **0 author metadata**. |
| **3. Crowd Hype** | Student 2 (`student2@tkmce.ac.in`) | View **Trending** feed, locate the projector issue, click **Hype (Flame icon)** | Hype count increments from `0 → 1`. Ticket rises in priority ranking. |
| **4. Admin Triage** | `admin@tkmce.ac.in` | In Admin Governance window, click **Refresh**, select projector ticket, change status to `IN_PROGRESS`, add note *"Technician dispatched"* | Status badge transitions to Blue (`IN_PROGRESS`). Note is committed to database. |
| **5. Student Redressal** | Student 1 | Refresh **My Submissions** tab | Ticket status updates to `IN_PROGRESS`, displaying the official admin note. |

---

## 4. Academic Viva Readiness Checklist

- [x] All 14 JUnit 5 tests pass (`mvn test`).
- [x] Application compiles cleanly into a shaded fat JAR (`target/aura.jar`).
- [x] Both Student and Admin GUI portals run locally side-by-side.
- [x] Cloud Supabase PostgreSQL database is online and seeded.
- [x] Slide-by-slide ownership maps directly to [`docs/AURA.pdf`](AURA.pdf) Slide 17.
- [x] Multi-host connection resilience prevents network/DNS drops during examination.
- [x] Version 1 sign-off is complete.
