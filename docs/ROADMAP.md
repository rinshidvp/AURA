# Development Roadmap & Milestone Verification — AURA

**Autonomous University Response and Action**  
Department of Computer Science & Engineering, TKM College of Engineering (TKMCE)  
Presentation Reference: [`docs/AURA.pdf`](AURA.pdf) (Slide 15, 18, 28)

---

## 1. 10-Week Development Schedule (Slide 28 Alignment)

This roadmap directly maps to the 10-week academic development schedule approved during Phase 1 (Slide 28 of [`docs/AURA.pdf`](AURA.pdf)). It provides clear evidence of **"Significant progress beyond Phase 1"** as required by the presentation evaluation rubric:

```mermaid
gantt
    title AURA 10-Week Academic Development Schedule
    dateFormat  YYYY-MM-DD
    section Phase 1 (Approved)
    Week 1: Requirements & PRD/TRD Documentation       :done,    des1, 2026-08-01, 2026-08-07
    Week 2: Architecture & UML Modeling                :done,    des2, 2026-08-08, 2026-08-14
    section Phase 2 (Implemented & Verified)
    Week 3: Supabase Schema & Java POJO Models         :done,    des3, 2026-08-15, 2026-08-21
    Week 4: DAO & JDBC Data Access Layer               :done,    des4, 2026-08-22, 2026-08-28
    Week 5: Service & Business Logic Layer             :done,    des5, 2026-08-29, 2026-09-04
    Week 6: Auth & Submission Pipeline Engine          :done,    des6, 2026-09-05, 2026-09-11
    Week 7: Admin Resolution Workflow & Hype Engine    :done,    des7, 2026-09-12, 2026-09-18
    Week 8: Modern FlatLaf Desktop GUI                 :done,    des8, 2026-09-19, 2026-09-25
    section Final Phase (Completed)
    Week 9: Automated Testing & Security Audit         :done,    des9, 2026-09-26, 2026-10-02
    Week 10: Golden-Path Walkthrough & Presentation    :done,    des10, 2026-10-03, 2026-10-09
    section Extension (Completed)
    Live Web Portal: Supabase Auth + RPC Security      :done,    ext1, 2026-09-24, 2026-10-12
    Final Evaluation Deck & Report                     :done,    ext2, 2026-10-13, 2026-10-17
```

---

## 2. Planned vs. Completed Verification Matrix (Rubric Criterion 4)

To satisfy the academic evaluation rubric, the table below documents the planned deliverables from Phase 1 alongside the completed technical artifacts for Phase 2:

| Milestone / Week | Planned Deliverables (Slide 28) | Status | Verification Evidence in Repository |
|---|---|---|---|
| **Week 1: Requirements** | • PRD creation (`prd.md`)<br>• TRD creation (`trd.md`)<br>• Requirements & scope finalization | **Completed** | [`docs/PRD.md`](PRD.md), [`docs/TRD.md`](TRD.md) |
| **Week 2: Architecture** | • Architecture spec (`architecture.md`)<br>• Complete UML Class Diagram<br>• Use Case diagram & package design | **Completed** | [`docs/ARCHITECTURE.md`](ARCHITECTURE.md), [`docs/AURA.pdf`](AURA.pdf) |
| **Week 3: Schema & Models** | • Relational schema definition<br>• Java Model POJO classes<br>• Enum definitions & mapping | **Completed** | [`sql/schema.sql`](../sql/schema.sql), `aura.model.*`, `aura.enums.*` |
| **Week 4: DAO & JDBC** | • JDBC Connection Factory<br>• UserDAO & SubmissionDAO<br>• SQL query optimization & mapping | **Completed** | `aura.dao.*`, `aura.config.DatabaseConfig` |
| **Week 5: Services** | • AuthService & SubmissionService<br>• TrackingService<br>• ReportService implementation | **Completed** | `aura.service.*` |
| **Week 6: Auth & Engine** | • Password hashing & verification<br>• Submission creation pipeline<br>• Status state transition engine | **Completed** | `aura.util.PasswordUtil`, `aura.util.ValidationUtil`, `aura.service.AuthService` |
| **Week 7: Resolution Workflow** | • Issue assignment engine<br>• Resolution note recording<br>• Dashboard metrics aggregation | **Completed** | `aura.service.TrackingService`, `aura.service.ReportService`, `aura.dao.ResolutionNoteDAO` |
| **Week 8: Modern Desktop GUI** | • Desktop application layout<br>• FlatLaf modern UI styling<br>• Event handlers & data binding | **Completed** | `aura.ui.LoginFrame`, `aura.ui.student.*`, `aura.ui.admin.*` |
| **Week 9: Testing & Security** | • JUnit 5 test suite execution<br>• Anonymity regression verification | **Completed** | [`docs/TESTING.md`](TESTING.md): 23 JUnit tests (15 offline, 8 DB) + 18 web tests, all passing; CI on every push |
| **Week 10: Golden Walkthrough** | • End-to-end presentation demo<br>• Final academic defense | **Completed** | Phase 2 deck [`presentation/`](presentation/); final deck [`presentation/final/`](presentation/final/index.html) |
| **Extension: Live Web Portal** | • Supabase Auth email/password sign-in<br>• Database RPCs with role checks<br>• Playwright browser tests | **Completed (code)** | [`sql/web_portal.sql`](../sql/web_portal.sql), [`WEB_PORTAL_AUTH.md`](WEB_PORTAL_AUTH.md), `tests/`. Live sign-in needs owner-supplied Vercel/Supabase settings and the human acceptance checklist |

**Schedule note:** The 10-week plan was followed. One deliberate change: desktop Google OAuth (Phase 2) was replaced by institutional email/password sign-in (BCrypt in the desktop app, Supabase Auth on the web portal), because an OAuth client secret cannot be kept secret inside a distributed desktop JAR and the hosted portal needed one direct sign-in method.

---

## 3. Deliberately Out of Scope for Phase 2

To maintain focus on the core student-admin governance loop and ensure defensibility before faculty examiners, the following features remain scheduled for future release:
- Native mobile client (Desktop Java SE is the syllabus requirement).
- Real-time chat threads between students and admins.
- Multi-campus / Multi-university tenancy (TKMCE-only by design).
