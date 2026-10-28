# System Design and Architecture

## AURA — Autonomous University Response and Action

### Academic Project Report

AURA is a campus issue management and suggestion platform designed for TKM College of Engineering. It provides a structured and transparent way for students to submit problems, track their own submissions, support urgent issues through community upvotes, and allow administrators to process and resolve complaints in a disciplined workflow. The system is built to replace fragmented communication methods such as WhatsApp groups, informal reporting channels, and static Google Forms with a formal digital workflow that is secure, auditable, and user-friendly.

The core objective of AURA is to ensure that students can raise valid campus concerns without fear of exposure, while administrators can act on these issues in a consistent, accountable, and scalable way. The system is designed around fairness, anonymity, transparency, and operational efficiency.

---

## 1. Project Context and Design Goal

AURA addresses a common problem in academic institutions: student concerns are often scattered across informal channels, making it difficult to prioritize, categorize, resolve, and monitor issues. Many valid problems remain hidden because students do not trust the process or do not feel that their reports will be addressed.

The design of AURA addresses this by combining:

- Anonymous issue reporting
- Role-based access control
- Structured ticket lifecycle management
- Student tracking of own submissions
- Community prioritization using hype/upvotes
- Administrative review and resolution notes
- Secure persistence using PostgreSQL and JDBC

The system is intended to support both student and administrative workflows while enforcing institutional rules and protecting privacy.

---

## 2. Architectural Vision

AURA follows a disciplined layered architecture that separates:

1. User interface and interaction
2. Business logic and domain rules
3. Data access and persistence operations
4. Relational database storage

The design ensures that the user interface does not directly manipulate database objects, that service classes enforce business rules, and that persistence logic remains isolated in DAO classes.

This layered model improves maintainability, testability, and security. It also allows the team to implement and explain every responsibility clearly during academic evaluation.

---

## 3. System Architecture Overview

AURA uses a four-layer architecture:

### 3.1 Presentation Layer
This layer contains the Java Swing and FlatLaf desktop interfaces, including login pages, student dashboards, and administrative dashboards. The UI is responsible for collecting user input, displaying submissions, and triggering service operations.

Key components:
- LoginFrame
- StudentDashboardFrame
- AdminDashboardFrame
- SubmissionFormPanel
- Tracking and reporting panels

### 3.2 Service Layer
The service layer handles business rules and coordination. This is where validation, authentication, access control, ticket lifecycle updates, and hype logic are managed.

Key components:
- AuthService
- SubmissionService
- DatabaseSubmissionService
- HypeService
- TrackingService
- ReportService
- ServiceRegistry

### 3.3 Data Access Layer
The DAO layer is the only package permitted to interact with the database. It uses JDBC with prepared statements to ensure safe interaction with PostgreSQL.

Key components:
- UserDAO
- SubmissionDAO
- StudentReceiptDAO
- SubmissionHypeDAO
- SubmissionHistoryDAO
- ResolutionNoteDAO

### 3.4 Database Layer
The database layer is implemented using Supabase PostgreSQL. It stores users, submissions, receipts, hype records, resolution notes, and status transitions.

This separation ensures that the system remains modular and protects the architecture from direct dependency leakage between UI and database logic.

---

## 4. Layer Dependency Rule

The most important design rule in AURA is the downward dependency flow:

UI -> Service -> DAO -> Database

This means:
- GUI components call service methods
- Service layer performs validation and rules enforcement
- DAO classes interact with the database
- Database stores only persistence data

This rule prevents direct SQL usage in UI classes and ensures a clean architectural boundary.

---

## 5. Core Functional Modules

### 5.1 Authentication and User Management
The authentication flow allows students and administrators to log in using institutional email credentials. The system validates email addresses against the institution domain and stores password hashes using BCrypt.

Features:
- Domain validation using @tkmce.ac.in
- Password hashing with BCrypt
- Login and session management
- Role-based access to dashboards
- Optional Google OAuth integration

### 5.2 Student Submission Module
Students can submit issues or suggestions with details such as:
- title
- description
- issue type
- category
- location
- priority
- optional photo URL

Each submission is stored as an anonymous public record, which protects student identity while still allowing the system to show the issue to administrators and the rest of the campus.

### 5.3 Hype / Trending Module
AURA includes a hype engine that allows students to support issues they also consider important. This creates a crowd-prioritized list of student concerns.

The design prevents duplicate voting through uniqueness constraints and control logic in HypeService and SubmissionHypeDAO.

### 5.4 My Submissions Tracking
Students can view their own submissions through the private receipt vault. This data is not exposed to administrators. The vault stores the link between the student and the anonymous submission, allowing students to track their own issues while preserving privacy.

### 5.5 Administrative Queue and Resolution Module
Admin users access a structured queue of all submissions. They can:
- filter by category, priority, status
- view issue details
- assign work
- update status through the defined lifecycle
- add resolution notes
- review history and audit status changes

### 5.6 Reporting and Analytics Module
Administrators can analyze issue trends and generate structured reports. This supports campus improvement planning and helps identify recurring problems in infrastructure, academic support, health services, hostel facilities, and general campus operations.

---

## 6. System Workflow

The complete operating flow of AURA is simple but effective:

1. A student logs in using an institutional email account.
2. The student submits an issue or suggestion with category, location, and severity.
3. The submission is stored in the public submissions table without exposing student identity.
4. The system creates a private receipt linking the student to the submission.
5. Other students can view and hype relevant issues.
6. Administrative users review the queue and prioritize the most important items.
7. The issue moves through the lifecycle from pending to assigned to in progress to resolved or rejected.
8. Resolution notes are added, and the history is preserved for auditability.

This creates a transparent and accountable reporting cycle that benefits both students and administrators.

---

## 7. Status Lifecycle

AURA operates on a five-state lifecycle model:

PENDING
-> ASSIGNED
-> IN_PROGRESS
-> RESOLVED
or
-> REJECTED

This lifecycle is essential because it ensures each issue is not treated as a simple one-time ticket. It gives administrators a formal mechanism for progress tracking, review, and final closure. The status transitions are recorded in audit history for transparency.

---

## 8. Design Principles

AURA was designed according to sound software engineering principles:

### 8.1 Separation of Concerns
Each component has a single responsibility. UI classes manage display, service classes manage logic, and DAO classes manage persistence.

### 8.2 Security by Design
Authentication, validation, password hashing, and database-level constraints protect the system from common misuse and attacks.

### 8.3 Privacy by Architecture
The anonymity vault is implemented at the database and architectural level rather than only in the user interface. This is one of the strongest design decisions in the project.

### 8.4 Auditable State Changes
Each status change is tracked through history records so that the development team and faculty reviewers can understand how a submission evolved.

### 8.5 Scalability and Maintainability
The architecture is modular enough to allow future upgrades, such as notifications, analytics, mobile interfaces, or additional administrative modules.

---

## 9. Data Design and Database Schema

The database design is based on PostgreSQL and is organized around clear relational entities such as users, submissions, receipts, hype, history, and notes.

### 9.1 Core Tables
- users
- submissions
- student_submission_receipts
- submission_hype
- resolution_notes
- submission_history

### 9.2 Key Design Choice: Anonymous Public Submission Model
The public submissions table does not store a student identity column. This is necessary to preserve anonymity.

Identity is stored separately in the student receipt mapping table, which is accessible only in the student-owned tracking flow. This ensures that administrators can cleanly manage the queue without being able to know the original reporter.

### 9.3 Data Integrity Controls
The schema uses:
- primary keys
- foreign key references
- uniqueness constraints
- status checks
- professional indexing

Examples include:
- unique vote per student per submission
- unique receipt per student per submission
- email constraint based on TKMCE domain
- status validation for the lifecycle

---

## 10. Security Architecture

Security is a central part of the AURA design.

### 10.1 Institutional Domain Restriction
Only emails ending in @tkmce.ac.in are accepted. This prevents unauthorized users from creating accounts and keeps the system aligned with the institutional environment.

### 10.2 Password Protection
Plaintext passwords are never stored. Passwords are hashed using BCrypt before persistence. This protects account security even if the database is compromised.

### 10.3 SQL Injection Prevention
Every database interaction uses prepared statements instead of direct string concatenation. This protects the application from SQL injection and is a major quality standard in the architecture.

### 10.4 Role-based Access Control
The system distinguishes between student and admin users to ensure the right users access the right part of the system. Students cannot modify admin queues, and admins cannot access private identity mapping data.

### 10.5 Privacy Protection
The decoupled anonymity vault is the key privacy mechanism. It physically separates the public ticket from the private owner mapping, thereby reducing risk from internal misuse and database-level leaks.

---

## 11. System Components and Responsibilities

### 11.1 User Model
The User class defines common identity and role information for both students and administrators. The design uses inheritance to represent specialized user types while preserving shared account behavior.

### 11.2 Submission Model
The Submission model defines the core issue or suggestion object. It includes attributes for title, description, type, category, location, priority, status, and lifecycle data.

### 11.3 Resolution and History Models
ResolutionNote and SubmissionHistory capture administrative outcomes and status transitions. These are essential for accountability and auditing.

### 11.4 Service Classes
Service classes orchestrate all major use cases such as authentication, student reporting, admin actions, hype controls, and report generation.

### 11.5 DAO Classes
DAO classes are responsible for persistence-level operations. They convert database rows into domain objects and perform database operations with proper resource handling and transaction control.

---

## 12. Architectural Strengths

AURA demonstrates several strong architectural qualities:

- Clear separation between UI, service, DAO, and database responsibilities
- Role-aware access patterns
- Data privacy built into the schema and not only the interface
- Identity preservation through private receipt mapping
- Efficient table structure for submission lifecycle and hype scoring
- Transparent, auditable decision paths for administrators
- Compatibility with Java desktop development and modern UI design

These strengths are important because they show that the project is not just a simple interface; it is a real system with thoughtful technical design.

---

## 13. Technical Stack

The system is implemented with a practical and academically appropriate technology stack:

- Java 17
- Swing + FlatLaf
- Apache Maven
- PostgreSQL / Supabase
- JDBC
- BCrypt password hashing
- JUnit 5 for testing

This combination is well aligned with object-oriented Java learning outcomes and is suitable for academic project evaluation.

---

## 14. Non-Functional Requirements Supported by the Architecture

The design satisfies several non-functional requirements:

- Security: password hashing, domain validation, RBAC, and privacy separation
- Data integrity: database constraints and uniqueness rules
- Reliability: transaction-safe status updates and controlled DAO access
- Maintainability: modular service and DAO architecture
- Usability: simple dashboard flows for both students and administrators
- Scalability: indexing and structured table design for growth

---

## 15. Architectural Summary

AURA is a strong academic software design because it balances functional requirement fulfillment with sound technical architecture. The project showcases how a real-world campus problem can be addressed by a secure, structured, and transparent digital system.

The system design reflects a complete engineering mindset:
- the UI is clean and user-centred,
- the backend follows clear logic boundaries,
- the database is carefully designed,
- privacy is protected instead of assumed,
- and administrative resolution is made traceable and measurable.

This is exactly what makes AURA suitable for a self-submission project document and academic defense.

---

## 16. Conclusion

System design and architecture are the heart of AURA. The project is not limited to a simple form or dashboard; it is a complete campus governance system designed with real software engineering principles. From the layered architecture to the anonymity vault, from status lifecycle management to secure database interaction, every decision in AURA supports a practical and professional product vision.

The result is a platform that is functional, explainable, secure, and clearly designed for implementation and evaluation.

Prepared for academic submission as the System Design and Architecture section of the AURA project.
