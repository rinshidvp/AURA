from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "AURA_Progress_Review.pdf"
PHOTO = Path(r"C:\Users\naafi\Desktop\projects\java project\New folder\AURA\needed to include.jpeg")
W, H = 595, 842
M = 44

NAVY = (0.07, 0.15, 0.25)
TEAL = (0.05, 0.48, 0.52)
GOLD = (0.91, 0.62, 0.18)
INK = (0.12, 0.15, 0.18)
MUTED = (0.36, 0.41, 0.46)
PALE = (0.93, 0.96, 0.96)
LIGHT = (0.97, 0.98, 0.98)


def esc(value):
    value = str(value).encode("ascii", "replace").decode("ascii")
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def jpeg_size(path):
    data = path.read_bytes()
    i = 2
    while i < len(data) - 9:
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in (0xD8, 0xD9):
            continue
        length = int.from_bytes(data[i:i + 2], "big")
        if marker in range(0xC0, 0xC4):
            return int.from_bytes(data[i + 5:i + 7], "big"), int.from_bytes(data[i + 3:i + 5], "big")
        i += length
    return 1, 1


class Page:
    def __init__(self, number, title=""):
        self.n = number
        self.ops = ["q"]
        self.title = title

    def color(self, c, stroke=False):
        self.ops.append(f"{c[0]} {c[1]} {c[2]} {'RG' if stroke else 'rg'}")

    def rect(self, x, y, w, h, fill, stroke=None, sw=1):
        if fill:
            self.color(fill)
        if stroke:
            self.color(stroke, True)
            self.ops.append(f"{sw} w")
        self.ops.append(f"{x} {y} {w} {h} re {'B' if fill and stroke else 'f' if fill else 'S'}")

    def line(self, x1, y1, x2, y2, c=MUTED, sw=1):
        self.color(c, True)
        self.ops.append(f"{sw} w {x1} {y1} m {x2} {y2} l S")

    def text(self, x, y, value, size=10, font="F1", c=INK):
        self.color(c)
        self.ops.append(f"BT /{font} {size} Tf 1 0 0 1 {x} {y} Tm ({esc(value)}) Tj ET")

    def wrap(self, x, y, value, width=82, size=9, leading=13, font="F1", c=INK):
        words = str(value).split()
        lines, current = [], ""
        for word in words:
            if len(current) + len(word) + 1 <= width:
                current = (current + " " + word).strip()
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        for line in lines:
            self.text(x, y, line, size, font, c)
            y -= leading
        return y

    def heading(self, title, subtitle=""):
        self.rect(0, H - 76, W, 76, NAVY)
        self.text(M, H - 43, title, 22, "F2", (1, 1, 1))
        if subtitle:
            self.text(M, H - 61, subtitle, 8.5, "F1", (0.82, 0.91, 0.91))
        self.line(M, H - 91, W - M, H - 91, GOLD, 2)

    def footer(self):
        self.line(M, 31, W - M, 31, (0.83, 0.86, 0.87), 0.5)
        self.text(M, 18, "AURA | Technical Learning Manual | Source-based study document", 7, "F1", MUTED)
        self.text(W - M - 25, 18, str(self.n), 7, "F2", MUTED)

    def end(self):
        self.ops.append("Q")
        return "\n".join(self.ops).encode("ascii")


def bullet(page, y, label, body, x=M, width=78):
    page.text(x, y, "-", 10, "F2", TEAL)
    return page.wrap(x + 12, y, f"{label}: {body}" if label else body, width, 9.2, 13)


def table(page, x, y, widths, headers, rows, row_h=28, fs=7.5):
    total = sum(widths)
    page.rect(x, y - row_h, total, row_h, NAVY)
    xx = x
    for width, head in zip(widths, headers):
        page.text(xx + 5, y - 18, head, fs, "F2", (1, 1, 1))
        xx += width
    yy = y - row_h
    for r, row in enumerate(rows):
        page.rect(x, yy - row_h, total, row_h, PALE if r % 2 == 0 else (1, 1, 1), (0.82, 0.86, 0.87), 0.35)
        xx = x
        for width, value in zip(widths, row):
            page.wrap(xx + 5, yy - 11, value, max(8, int(width / 5.2)), fs, 8.5, "F1", INK)
            xx += width
        yy -= row_h
    return yy


def box(page, x, y, w, h, title, body, accent=TEAL):
    page.rect(x, y - h, w, h, LIGHT, (0.78, 0.84, 0.85), 0.7)
    page.rect(x, y - h, 5, h, accent)
    page.text(x + 14, y - 18, title, 10, "F2", NAVY)
    page.wrap(x + 14, y - 34, body, max(12, int(w / 5.2)), 8.3, 11, "F1", INK)


def arrow(page, x1, y1, x2, y2, label=""):
    page.line(x1, y1, x2, y2, TEAL, 1.5)
    page.line(x2, y2, x2 - 5, y2 + 4, TEAL, 1.5)
    page.line(x2, y2, x2 - 5, y2 - 4, TEAL, 1.5)
    if label:
        page.text((x1 + x2) / 2 - 18, y1 + 5, label, 7, "F1", MUTED)


def make_pages():
    pages = []
    n = 1
    p = Page(n); p.rect(0, 0, W, H, NAVY); p.rect(0, 0, W, 110, TEAL)
    p.text(54, 685, "AURA", 50, "F2", (1, 1, 1)); p.text(57, 650, "AUTONOMOUS UNIVERSITY RESPONSE AND ACTION", 10, "F2", GOLD)
    p.text(57, 590, "Project Progress Review", 28, "F2", (1, 1, 1)); p.text(57, 560, "Second presentation study document", 14, "F1", (0.82, 0.91, 0.91))
    p.text(57, 500, "Department of Computer Science & Engineering", 12, "F1", (1, 1, 1)); p.text(57, 478, "TKM College of Engineering | Java 17 desktop application", 10, "F1", (0.82, 0.91, 0.91))
    p.text(57, 390, "Team", 10, "F2", GOLD)
    for i, name in enumerate(["Ringshit", "Nirmal", "Rehandeep", "Adil", "Nafee"]): p.text(57, 365 - i * 25, name, 15, "F1", (1, 1, 1))
    p.text(57, 165, "Progress position: 70% complete | 30% planned work", 11, "F2", (1, 1, 1)); p.text(57, 142, "Prepared from source code, SQL, tests, and engineering documentation", 8.5, "F1", (0.82, 0.91, 0.91))
    if PHOTO.exists():
        iw, ih = jpeg_size(PHOTO); data = PHOTO.read_bytes(); p.image = (data, iw, ih, 375, 185, 155, 105)
    p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Executive Summary", "What AURA solves and where the build stands"); y = 715
    y = p.wrap(M, y, "AURA is a campus issue and suggestion governance platform. It gives students a trusted way to submit anonymous reports, follow their own tickets, and support important issues through hype votes. Administrators triage the shared queue, move tickets through a five-state lifecycle, and attach resolution notes.", 84, 10, 14)
    y -= 10; box(p, M, y, 157, 115, "OBJECTIVE", "Convert informal campus complaints into traceable, prioritised, and auditable work items while preserving student anonymity.", TEAL); box(p, 219, y, 157, 115, "PROBLEM", "Students lack a single channel for issues and suggestions; administrators lack structured prioritisation, status history, and accountability.", GOLD); box(p, 394, y, 157, 115, "CURRENT POSITION", "70% complete: core authentication, submission, tracking, administration, persistence, security controls, and tests are implemented.", TEAL)
    y -= 145; p.text(M, y, "Progress split", 13, "F2", NAVY); p.rect(M, y - 35, 420, 24, (0.86, 0.89, 0.90)); p.rect(M, y - 35, 294, 24, TEAL); p.text(M + 304, y - 19, "70% completed", 9, "F2", NAVY); p.text(M + 430, y - 19, "30% pending", 9, "F2", MUTED)
    y -= 72; p.text(M, y, "Evidence used", 12, "F2", NAVY); y -= 20
    for label, body in [("Code", "20+ Java classes across config, DAO, model, service, UI, and util packages."), ("Data", "PostgreSQL schema with six tables, constraints, indexes, seed users, tickets, hypes, notes, and history."), ("Quality", "Maven/JUnit suite covering authentication, submissions, hype, password rules, validation, and anonymity regression.")]: y = bullet(p, y, label, body)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Progress Timeline", "From the zeroth presentation to the current review");
    events = [("Zeroth presentation", "Approved objective, architecture, privacy boundary, and interface direction."), ("UI designed", "FlatLaf Swing entry point and student/admin dashboard frames are wired."), ("Database created", "PostgreSQL schema, seed data, indexes, foreign keys, and checks are present."), ("Authentication completed", "Password login, BCrypt, Google OAuth/PKCE path, domain gate, and session context."), ("Student module completed", "Submission form, receipt vault lookup, personal list, detail history, and hype action."), ("Admin module progress", "Queue, status change, resolution notes, history view, and role guard are present."), ("Current stage", "Integration hardening, reporting/analytics, polish, wider test coverage, and documentation closure.")]
    y = 718
    for i, (title, body) in enumerate(events):
        p.rect(65, y - 7, 14, 14, TEAL if i < 6 else GOLD); p.text(68, y - 4, str(i + 1), 7, "F2", (1, 1, 1));
        if i < len(events) - 1: p.line(72, y - 8, 72, y - 62, TEAL, 2)
        p.text(105, y, title, 12, "F2", NAVY); p.wrap(105, y - 17, body, 66, 9, 12); y -= 78
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Completed Work | Core Modules", "Implemented classes, data path, screens, and status");
    rows = [("Authentication", "AuthService, GoogleOAuthService, UserDAO, LoginFrame, ValidationUtil, PasswordUtil", "users", "Password + OAuth entry; domain gate; session set", "Complete / OAuth configuration dependent"), ("Student dashboard", "StudentDashboardFrame, SubmissionFormPanel, Submission, User", "submissions, receipts, hype", "Personal table, new submission, details, hype", "Complete core flow"), ("Issue + suggestion", "SubmissionService, DatabaseSubmissionService, SubmissionDAO", "submissions", "Form writes ISSUE or SUGGESTION with category/location/priority", "Complete"), ("Status tracking", "SubmissionHistory, ResolutionNote, SubmissionDAO, service", "submission_history, resolution_notes", "History and note display in student/admin detail views", "Complete core flow"), ("Database connectivity", "DatabaseConfig, DAO classes", "All six tables", "JDBC DriverManager, prepared statements, transactions", "Complete; environment configuration required")]
    table(p, M, 718, [93, 170, 103, 105, 80], ["Module", "Classes", "Tables", "Screens / behavior", "Status"], rows, 48, 6.7)
    p.text(M, 420, "Implementation notes", 13, "F2", NAVY); y = 397
    for label, body in [("Anonymity", "Submission rows do not store student_id. StudentReceiptDAO is the private ownership mapping used for My Submissions."), ("Integrity", "SubmissionDAO uses transactions for createWithReceipt and updateStatusWithHistory; database uniqueness blocks duplicate receipts and hypes."), ("UI", "Main applies FlatDarkLaf. LoginFrame routes authenticated STUDENT and ADMIN roles to separate frames."), ("Caveat", "Several classes describe themselves as minimal skeletons, and the dashboard UI is functional but not yet the final polished interface.")]: y = bullet(p, y, label, body, width=83)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Completed Work | Admin, Hype, Security", "The operational spine of the system");
    boxes = [("Admin dashboard", "AdminDashboardFrame loads all submissions, changes status through the five-state list, adds resolution notes, views history, refreshes, and logs out."), ("Hype / trending", "HypeService and SubmissionHypeDAO add, remove, count, and detect a student's hype. SubmissionDAO sorts by hype_count then created_at."), ("RBAC", "AuthService and SessionContext gate student/admin screens. AdminDashboardFrame rejects unauthenticated or non-admin sessions; student frame rejects admin sessions."), ("Security", "ValidationUtil enforces @tkmce.ac.in and minimum password length. PasswordUtil uses BCrypt. DAO queries use PreparedStatement. OAuth uses state + PKCE."), ("Testing", "Existing JUnit tests cover AuthService, DatabaseSubmissionService, HypeService, PasswordUtil, ValidationUtil, and AdminAnonymityRegressionTest."), ("Source-of-truth status", "This 70% score is a project review estimate: the primary user journey works, while reporting, analytics, notification, polish, and broader integration closure remain.")]
    y = 718
    for title, body in boxes:
        box(p, M, y, 507, 78, title, body, GOLD if title in ("Security", "Source-of-truth status") else TEAL); y -= 91
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Pending Work | Remaining 30%", "Prioritised closure plan");
    rows = [("Report generation", "Nirmal", "High", "3-5 days", "CSV/export service and admin action"), ("Analytics", "Ringshit", "High", "3-5 days", "Counts, trends, SLA-style metrics"), ("Notifications", "Adil", "Medium", "4-6 days", "Status-change feedback and delivery design"), ("History improvements", "Nafee", "Medium", "2-3 days", "Richer student timeline and edge cases"), ("UI polishing", "Ringshit", "High", "4-6 days", "Replace placeholder layouts, validation states, responsive sizing"), ("Testing", "Rehandeep", "High", "4-6 days", "DAO coverage, integration setup, failure paths"), ("Bug fixing", "All", "High", "Ongoing", "Run full suite and resolve DB/config/runtime issues"), ("Documentation", "Nafee", "Medium", "2-3 days", "Keep diagrams, setup, and speaking evidence current")]
    table(p, M, 718, [125, 78, 55, 70, 179], ["Pending feature", "Responsible", "Priority", "Estimate", "Definition of done"], rows, 45, 7)
    p.text(M, 300, "Completion gate", 13, "F2", NAVY); p.wrap(M, 280, "The remaining work is complete when every pending item has an implementation or accepted design decision, a test or verification note, and a presentation-ready screen or output.", 82, 9.5, 13)
    p.footer(); p.end(); pages.append(p); n += 1

    assignments = [
        ("Ringshit", "Student experience and analytics lead", "StudentDashboardFrame, SubmissionFormPanel, SubmissionService integration, analytics/report UI", "Student flow is core-complete; polish and analytics remain", "Finish UI states, filters, trending/analytics view, and demo student journey", "Explain the student problem, anonymous submission, hype, and how the dashboard turns reports into visible campus priorities."),
        ("Nirmal", "Reporting and admin workflow lead", "AdminDashboardFrame, report requirements, admin queue and export design", "Admin triage core is implemented; reporting remains", "Implement CSV/report generation, admin filters, and review metrics", "Explain how administrators read the queue, change lifecycle status, attach resolution notes, and use reports for accountability."),
        ("Rehandeep", "Persistence and quality lead", "UserDAO, SubmissionDAO, DatabaseConfig integration, database tests", "Database foundation is complete; test depth remains", "Add DAO integration coverage, schema verification, and failure-path tests", "Defend JDBC, prepared statements, transactions, six tables, indexes, and why persistence is isolated behind DAO classes."),
        ("Adil", "Security and notification lead", "Auth/session review, security acceptance, notification design and UI feedback", "Authentication/security controls are present; notifications remain", "Design notification events, status feedback, and security regression checklist", "Explain role boundaries, domain restriction, BCrypt, OAuth state/PKCE, and the next step for user notifications."),
        ("Nafee", "Authentication, privacy, and documentation lead", "AuthService, GoogleOAuthService, PasswordUtil, ValidationUtil, SessionContext, StudentReceiptDAO", "Authentication and anonymity boundary are implemented", "Harden history edge cases, consolidate docs, and lead final integration review", "Explain the login journey, session routing, decoupled anonymity vault, and why admins can resolve a ticket without knowing its author."),
    ]
    for name, role, files, progress, tasks, script in assignments:
        p = Page(n); p.heading(f"Team Responsibility | {name}", "One-page ownership brief and speaking plan")
        p.text(M, 715, role, 16, "F2", TEAL); p.line(M, 699, W - M, 699, GOLD, 1)
        y = 670
        for label, body in [("Assigned module", role), ("Main files / classes", files), ("Progress", progress), ("Remaining tasks", tasks)]:
            p.text(M, y, label, 9, "F2", MUTED); y = p.wrap(M + 105, y, body, 67, 9.5, 13); y -= 12
        box(p, M, y, 507, 145, "2-3 MINUTE SPEAKING PART", script, GOLD)
        p.text(M, y - 178, "Evidence to show", 12, "F2", NAVY); ey = y - 198
        evidence = {"Ringshit":"StudentDashboardFrame and SubmissionFormPanel; demonstrate new submission, My Submissions, and hype.", "Nirmal":"AdminDashboardFrame; demonstrate queue, status transition, resolution note, and planned report.", "Rehandeep":"sql/schema.sql plus SubmissionDAO; point to transaction boundaries, indexes, and prepared statements.", "Adil":"AuthService, SessionContext, ValidationUtil, and LoginFrame; explain role protection and notification gap.", "Nafee":"GoogleOAuthService, StudentReceiptDAO, SECURITY.md; show OAuth path and the no-student_id rule."}[name]
        p.wrap(M, ey, evidence, 84, 9, 12)
        p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Complete Code Architecture", "MVC-style presentation, service orchestration, DAO persistence");
    layers = [("Presentation / UI", "aura.Main, LoginFrame, StudentDashboardFrame, SubmissionFormPanel, AdminDashboardFrame", 690, NAVY), ("Service", "AuthService, GoogleOAuthService, DatabaseSubmissionService, HypeService, ServiceRegistry, SubmissionService", 575, TEAL), ("DAO / JDBC", "UserDAO, SubmissionDAO, StudentReceiptDAO, SubmissionHypeDAO", 460, GOLD), ("Model / domain", "User, Submission, ResolutionNote, SubmissionHistory and role/status/type/category/priority strings", 345, (0.35, 0.43, 0.48)), ("PostgreSQL / Supabase", "users, submissions, receipts, hype, resolution_notes, submission_history", 230, NAVY)]
    for title, body, y, c in layers: box(p, M, y, 507, 70, title, body, c)
    for y in [690, 575, 460, 345]: arrow(p, 297, y - 72, 297, y - 108, "calls")
    p.text(M, 130, "Dependency rule", 12, "F2", NAVY); p.wrap(M, 112, "Each layer depends downward. UI never executes SQL; services own business rules and session checks; DAO owns JDBC and PreparedStatement work; models carry data between boundaries.", 84, 9, 12)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Architecture and Workflow Diagrams", "Simplified diagrams derived from the current code");
    p.text(M, 716, "Request path", 13, "F2", NAVY)
    for x, label in [(55, "LoginFrame"), (175, "AuthService"), (295, "UserDAO"), (415, "DatabaseConfig"), (505, "PostgreSQL")]: p.rect(x, 655, 80, 32, PALE, TEAL, 0.8); p.text(x + 7, 668, label, 7.5, "F2", NAVY)
    for x in [135, 255, 375, 495]: arrow(p, x, 671, x + 35, 671)
    p.text(M, 615, "Login flow", 13, "F2", NAVY)
    flow = [(55, 550, "Credentials / Google"), (185, 550, "Validate domain"), (315, 550, "Find or provision"), (445, 550, "SessionContext")]
    for x, y, label in flow: p.rect(x, y, 105, 34, LIGHT, GOLD, 0.8); p.wrap(x + 7, y + 22, label, 17, 7.4, 9)
    for x in [160, 290, 420]: arrow(p, x, 567, x + 25, 567)
    p.text(M, 495, "Student submit -> admin resolve", 13, "F2", NAVY)
    p.rect(55, 415, 125, 42, PALE, TEAL, 0.8); p.text(67, 438, "Student form", 9, "F2", NAVY); p.rect(235, 415, 125, 42, PALE, TEAL, 0.8); p.text(247, 438, "createWithReceipt", 9, "F2", NAVY); p.rect(415, 415, 125, 42, PALE, GOLD, 0.8); p.text(428, 438, "Admin status + note", 9, "F2", NAVY)
    arrow(p, 180, 436, 235, 436); arrow(p, 360, 436, 415, 436)
    p.text(M, 355, "Status state machine", 13, "F2", NAVY); states = ["PENDING", "ASSIGNED", "IN_PROGRESS", "RESOLVED / REJECTED"]
    x = 55
    for i, s in enumerate(states): p.rect(x, 285, 108 if i < 3 else 145, 34, LIGHT, TEAL, 0.8); p.text(x + 7, 298, s, 7.5, "F2", NAVY); x += 125 if i < 3 else 0
    arrow(p, 163, 302, 180, 302); arrow(p, 288, 302, 305, 302); arrow(p, 413, 302, 430, 302)
    p.text(M, 220, "Database interaction", 13, "F2", NAVY); p.wrap(M, 198, "DatabaseConfig loads db.properties or environment variables, loads org.postgresql.Driver, and returns a TLS-capable JDBC connection. DAO methods use try-with-resources; status updates with history use a transaction and rollback on failure.", 84, 9, 12)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Class Documentation | Models and Utilities", "Important classes in the actual source tree");
    rows = [("User", "Domain user; id, name, email, passwordHash, role", "getters/setters, isAdmin, isStudent", "AuthService, UserDAO, SessionContext"), ("Submission", "Anonymous ticket data and hype count", "getters/setters for title, type, category, status, photo", "SubmissionService, SubmissionDAO, both dashboards"), ("ResolutionNote", "Admin resolution text linked to a submission", "getters/setters for ids, note, createdAt", "SubmissionDAO, dashboards"), ("SubmissionHistory", "Old/new status audit record", "getters/setters for transition and actor", "SubmissionDAO, dashboards"), ("AuthService", "Credential/OAuth login, registration, logout, RBAC checks", "authenticate, registerStudent, loginWithGoogle, loginMock, logout", "LoginFrame, dashboard guards"), ("SessionContext", "Volatile process-local active session", "set/get current user, role checks, clear", "AuthService and UI guards"), ("ValidationUtil", "Institutional email/password rules", "isValidTkmceEmail, normalizeEmail, isValidPassword", "AuthService, UserDAO, tests")]
    table(p, M, 718, [85, 160, 150, 112], ["Class", "Purpose / attributes", "Key methods", "Called by"], rows, 48, 6.8)
    p.text(M, 315, "Relationships", 13, "F2", NAVY); p.wrap(M, 295, "AuthService creates or retrieves User and places it in SessionContext. SubmissionService coordinates Submission, ResolutionNote, and SubmissionHistory through SubmissionDAO. StudentReceiptDAO links the current student to an otherwise anonymous Submission.", 84, 9, 12)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Class Documentation | Services, DAO, and UI", "Who calls what and where database access stops");
    rows = [("UserDAO", "CRUD users; maps ResultSet to User", "save, findById, findByEmail, update, delete", "AuthService"), ("SubmissionDAO", "Submission CRUD, receipts, history, notes, hype aggregation", "save, findById, findAll, createWithReceipt, updateStatusWithHistory", "DatabaseSubmissionService"), ("StudentReceiptDAO", "Private receipt vault lookup", "createReceipt, findSubmissionIdsByStudent", "student tracking service path"), ("SubmissionHypeDAO", "Single-vote persistence and counts", "addHype, removeHype, count, hasStudentHyped", "HypeService"), ("DatabaseSubmissionService", "Concrete SubmissionService and error translation", "create/list/find/update/note/history operations", "ServiceRegistry, dashboards"), ("LoginFrame", "Password, OAuth, mock login entry", "passwordLogin, googleLogin, openDashboard", "Main"), ("StudentDashboardFrame", "Student list and actions", "loadSubmissions, openSubmissionDialog, showDetails", "LoginFrame"), ("AdminDashboardFrame", "Admin queue and controls", "loadData, status, note, history", "LoginFrame")]
    table(p, M, 718, [105, 170, 145, 87], ["Class", "Purpose", "Key methods", "Called by"], rows, 48, 6.8)
    p.text(M, 315, "UML relationship sketch", 13, "F2", NAVY)
    box(p, 55, 285, 135, 62, "AuthService", "uses UserDAO and SessionContext", TEAL); box(p, 230, 285, 135, 62, "DatabaseSubmissionService", "uses SubmissionDAO", GOLD); box(p, 405, 285, 135, 62, "UI frames", "call services only", TEAL)
    arrow(p, 190, 315, 230, 315); arrow(p, 365, 315, 405, 315)
    p.wrap(M, 220, "The key architectural relationship is ownership: service classes are the seam between user actions and persistence. UI classes do not import java.sql.*; DAO classes are the only direct SQL boundary.", 84, 9, 12)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Database Documentation", "ER model, keys, constraints, and sample records");
    p.text(M, 716, "ER diagram (simplified)", 13, "F2", NAVY)
    entities = [(55, 610, "USERS", "user_id PK | email UNIQUE | role"), (395, 610, "SUBMISSIONS", "submission_id PK | status | no student_id"), (55, 480, "RECEIPTS", "receipt_id PK | student_id FK | submission_id FK"), (395, 480, "HYPE", "hype_id PK | submission_id FK | student_id FK"), (55, 350, "HISTORY", "history_id PK | old/new status | changed_by FK"), (395, 350, "NOTES", "note_id PK | admin_id FK | note")]
    for x, y, title, body in entities: box(p, x, y, 145, 62, title, body, TEAL if title in ("USERS", "SUBMISSIONS") else GOLD)
    arrow(p, 200, 635, 395, 635, "references"); arrow(p, 127, 610, 127, 542, "owns"); arrow(p, 200, 375, 395, 375, "related")
    p.text(M, 270, "Keys and sample data", 13, "F2", NAVY)
    rows = [("users", "user_id", "6 seeded: 4 STUDENT, 2 ADMIN", "@tkmce.ac.in check"), ("submissions", "submission_id", "5 tickets: 104, 103, 98, 89, 85", "5-state status check"), ("receipts", "receipt_id", "5 private ownership mappings", "unique student + submission"), ("submission_hype", "hype_id", "10 seeded votes", "unique submission + student"), ("resolution_notes", "note_id", "3 admin notes", "submission/admin FKs"), ("submission_history", "history_id", "6 lifecycle transitions", "submission/actor FKs")]
    table(p, M, 250, [130, 88, 180, 109], ["Table", "Primary key", "Seed evidence", "Important constraint"], rows, 35, 6.8)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Folder Structure", "Actual repository tree and purpose of each area");
    tree = ["AURA/", "|-- AGENT.md                 engineering and security rules", "|-- pom.xml                  Java 17, Maven dependencies, test runner", "|-- mvp_dashboard.html       visual MVP reference", "|-- docs/                     architecture, PRD, roadmap, security, tests", "|   |-- ARCHITECTURE.md       layer rules and diagrams", "|   |-- DATABASE.md           ER model and data dictionary", "|   |-- SECURITY.md           threat model and anonymity boundary", "|   `-- TESTING.md             verification plan", "|-- sql/                      deployable persistence definition", "|   |-- schema.sql            tables, constraints, indexes", "|   `-- seed.sql              sample users, tickets, votes, history", "|-- src/main/java/aura/      application source", "|   |-- config/               DatabaseConfig and OAuthConfig", "|   |-- dao/                  JDBC persistence classes", "|   |-- model/                User and submission domain objects", "|   |-- service/              business orchestration and registry", "|   |-- ui/                   Swing login, student, admin screens", "|   `-- util/                 validation, BCrypt, process session", "|-- src/main/resources/      db.properties.example and OAuth example", "`-- src/test/java/aura/      JUnit service, security, and utility tests"]
    y = 720
    for line in tree: p.text(M, y, line, 8.3, "F1" if not line.startswith("AURA") else "F2", NAVY if line.startswith(("AURA", "|--")) else MUTED); y -= 24 if line.startswith("AURA") else 21
    p.text(320, 720, "Reading guide", 12, "F2", TEAL); p.wrap(320, 698, "Start at Main and LoginFrame. Follow the service call to the DAO. Then inspect schema.sql to see the relational contract and the test classes to see the acceptance evidence.", 38, 8.5, 11)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Presentation Speaking Script", "A shared sequence for the second review");
    p.text(M, 716, "Recommended order", 13, "F2", NAVY); y = 690
    for label, body in [("1. Nafee", "Set the context: objective, login/security, anonymity vault, and the 70/30 position."), ("2. Ringshit", "Demonstrate the student experience: submit, view personal tickets, hype, and inspect history."), ("3. Rehandeep", "Defend the database and DAO layer: schema, keys, indexes, prepared statements, and transactions."), ("4. Nirmal", "Demonstrate the admin queue: status progression, resolution note, history, and reporting gap."), ("5. Adil", "Close with security acceptance, notification plan, testing gaps, and the remaining work checklist.")]: y = bullet(p, y, label, body)
    y -= 15; p.text(M, y, "Common technical phrases to use", 13, "F2", NAVY); y -= 23
    for phrase in ["The UI calls services; it never touches JDBC directly.", "Anonymity is enforced by the schema because submissions has no student_id.", "The receipt vault lets a student find their own ticket without exposing ownership to the admin queue.", "PreparedStatement, foreign keys, uniqueness constraints, and transactions protect integrity.", "The 70% claim describes the working core; the 30% is closure work around reporting, analytics, notifications, polish, testing, and documentation."]: y = bullet(p, y, "", phrase, width=84)
    p.footer(); p.end(); pages.append(p); n += 1

    p = Page(n); p.heading("Final Review Checklist", "Use this page during the rehearsal and before submission");
    checks = [("Completed features", ["[ ] Password login and institutional email validation", "[ ] Google OAuth configuration tested", "[ ] Student submission and receipt flow", "[ ] Hype and duplicate-vote rule", "[ ] Admin status, notes, and history", "[ ] Database schema, seed data, and anonymity boundary"]), ("Pending features", ["[ ] Report generation", "[ ] Analytics and filters", "[ ] Notifications", "[ ] History improvements", "[ ] Final UI polish"]), ("Quality and delivery", ["[ ] Full Maven test run with configured database", "[ ] Bug list triaged with owners", "[ ] DAO and integration tests expanded", "[ ] README/setup and diagrams updated", "[ ] Each member rehearsed a 2-3 minute section", "[ ] Demo data and presentation screenshots ready"])]
    y = 715
    for title, items in checks:
        p.text(M, y, title, 13, "F2", NAVY); y -= 22
        for item in items: p.text(M + 10, y, item, 10, "F1", INK); y -= 21
        y -= 18
    box(p, M, 245, 507, 100, "FINAL MESSAGE", "AURA already demonstrates a complete academic core: secure access, anonymous reporting, structured persistence, role separation, and auditable resolution. The next review should show the core live and frame the remaining 30% as a disciplined closure plan.", TEAL)
    p.footer(); p.end(); pages.append(p); n += 1
    return pages


def build_pdf(pages):
    objects = []
    def add(data): objects.append(data); return len(objects)
    catalog = add(None); pages_obj = add(None); font = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"); bold = add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    image_obj = None
    if PHOTO.exists():
        iw, ih = jpeg_size(PHOTO); image_obj = add(b"<< /Type /XObject /Subtype /Image /Width %d /Height %d /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length %d >>\nstream\n" % (iw, ih, len(PHOTO.read_bytes())) + PHOTO.read_bytes() + b"\nendstream")
    page_refs = []
    for page in pages:
        if hasattr(page, "image") and image_obj:
            data, iw, ih, x, y, w, h = page.image
            page.ops.insert(-1, f"q {w / iw} 0 0 {h / ih} {x} {y} cm /Im1 Do Q")
        content = add(b"<< /Length %d >>\nstream\n" % len(page.end()) + page.end() + b"\nendstream")
        resources = f"<< /Font << /F1 {font} 0 R /F2 {bold} 0 R >>" + (f" /XObject << /Im1 {image_obj} 0 R >>" if image_obj else "") + " >>"
        page_refs.append(add(f"<< /Type /Page /Parent {pages_obj} 0 R /MediaBox [0 0 {W} {H}] /Resources {resources} /Contents {content} 0 R >>".encode()))
    objects[catalog - 1] = f"<< /Type /Catalog /Pages {pages_obj} 0 R >>".encode()
    objects[pages_obj - 1] = (f"<< /Type /Pages /Kids [{' '.join(str(x) + ' 0 R' for x in page_refs)}] /Count {len(page_refs)} >>").encode()
    pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(pdf)); pdf += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    start = len(pdf); pdf += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode(); pdf += b"".join(f"{off:010d} 00000 n \n".encode() for off in offsets[1:]); pdf += f"trailer\n<< /Size {len(objects) + 1} /Root {catalog} 0 R >>\nstartxref\n{start}\n%%EOF\n".encode(); OUT.write_bytes(pdf)


if __name__ == "__main__":
    pages = make_pages(); build_pdf(pages); print(f"Wrote {OUT} ({len(pages)} pages)")