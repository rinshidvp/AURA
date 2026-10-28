from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, ListFlowable, ListItem, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'AURA_System_Design_and_Architecture.pdf'


def build_pdf():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=14,
        alignment=1,
    )
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0B3B5B'),
        spaceBefore=18,
        spaceAfter=10,
    )
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        alignment=1,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8,
    )
    small_style = ParagraphStyle(
        'SmallStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=14,
        leftIndent=18,
        bulletIndent=12,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=6,
    )

    content = []

    content.append(Paragraph('AURA', title_style))
    content.append(Paragraph('System Design and Architecture', ParagraphStyle('Subtitle', parent=styles['Title'], fontName='Helvetica-Bold', fontSize=16, leading=22, textColor=colors.HexColor('#1E3A5F'), alignment=1, spaceAfter=12)))
    content.append(Paragraph('Autonomous University Response and Action', ParagraphStyle('Subhead', parent=styles['BodyText'], fontName='Helvetica-Bold', fontSize=11, leading=14, textColor=colors.HexColor('#111827'), alignment=1, spaceAfter=6)))
    content.append(Paragraph('Department of Computer Science & Engineering<br/>TKM College of Engineering', small_style))
    content.append(Spacer(1, 16))
    content.append(Paragraph('This document presents the system design and architecture of AURA, a Java-based campus issue and suggestion management platform developed to improve transparency, anonymity, prioritization, and accountability in academic institutions.', body_style))

    content.append(PageBreak())

    def add_heading(text):
        content.append(Paragraph(text, heading_style))

    add_heading('1. Project Context and Design Goal')
    content.append(Paragraph('AURA addresses the problem of fragmented campus issue reporting, where students often raise concerns through informal and unstructured channels. This makes it difficult for administrators to track, prioritize, and resolve problems efficiently. The platform introduces a structured digital workflow that combines anonymous reporting, status tracking, student ownership, and administrative accountability.', body_style))

    add_heading('2. Architectural Vision')
    content.append(Paragraph('The architecture of AURA follows a disciplined four-layer model: user interface, service logic, data access, and database storage. This separation improves maintainability, reduces coupling, and ensures that business rules remain independent from persistence logic and interface design.', body_style))

    add_heading('3. Four-Layer Architecture')
    layer_data = [
        ['Layer', 'Responsibility', 'Key Components'],
        ['Presentation Layer', 'Displays screens and captures user actions', 'LoginFrame, StudentDashboardFrame, AdminDashboardFrame, SubmissionFormPanel'],
        ['Service Layer', 'Contains business logic and validation', 'AuthService, SubmissionService, DatabaseSubmissionService, HypeService, TrackingService'],
        ['Data Access Layer', 'Handles all JDBC operations and database interaction', 'UserDAO, SubmissionDAO, StudentReceiptDAO, SubmissionHypeDAO'],
        ['Database Layer', 'Stores project data in a relational model', 'Supabase PostgreSQL tables such as users, submissions, receipts, hype, notes, and history']
    ]
    table = Table(layer_data, colWidths=[90, 190, 220])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#F8FAFC'), colors.HexColor('#FFFFFF')]),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
    ]))
    content.append(table)
    content.append(Spacer(1, 12))
    content.append(Paragraph('The key rule is the downward dependency flow: UI → Service → DAO → Database. The graphical layer does not contain SQL logic or direct database calls. This separation is essential for architecture clarity and security.', body_style))

    add_heading('4. Core Design Principles')
    list_items = [
        'Separation of concerns: each class has a clearly defined responsibility.',
        'Security by design: authentication, password hashing, validation, and access control are enforced in the application logic.',
        'Privacy by architecture: public submission data is separated from private ownership data.',
        'Auditability: all issue status transitions are recorded through history records.',
        'Maintainability: modular code structure supports future enhancement and testing.'
    ]
    content.append(ListFlowable([ListItem(Paragraph(item, bullet_style), bulletType='bullet', value='•') for item in list_items], bulletType='bullet'))

    add_heading('5. Student Module Design')
    content.append(Paragraph('The student module allows a user to register, log in, submit issues, vote on issues that matter to them, and track their own reports. The system supports both issue reporting and suggestions, enabling constructive feedback beyond complaint handling.', body_style))
    content.append(Paragraph('The student can provide: title, description, category, location, priority, and optional supporting media. Each submission is stored as an anonymous public record so that student identity is not exposed to the administrative queue.', body_style))

    add_heading('6. Admin Module Design')
    content.append(Paragraph('The administrative module provides a structured issue queue. Administrators can filter and review all submissions, inspect details, update the status lifecycle, assign tasks, and add resolution notes. This ensures that campus problems are handled in a transparent and accountable manner.', body_style))
    content.append(Paragraph('The admin flow is designed to prioritize action rather than identity disclosure. Administrators can manage the system without seeing the author of each public ticket, reinforcing the project’s privacy-first approach.', body_style))

    add_heading('7. Hype and Prioritization Design')
    content.append(Paragraph('AURA includes a hype engine that lets students support submissions they also consider important. This creates a crowd-prioritized list of issues and helps urgent problems rise to the top. Duplicate voting is prevented through unique constraints and logic in HypeService and SubmissionHypeDAO.', body_style))

    add_heading('8. Status Lifecycle and Workflow')
    content.append(Paragraph('The system follows a five-state process: PENDING → ASSIGNED → IN_PROGRESS → RESOLVED / REJECTED. This lifecycle is crucial because it transforms the reporting platform from a passive form into a true issue management system with tracked progress and closure evidence.', body_style))

    lifecycle_data = [
        ['Step', 'Meaning'],
        ['PENDING', 'The issue is submitted and awaits administrative review'],
        ['ASSIGNED', 'A responsible authority has been assigned to the issue'],
        ['IN_PROGRESS', 'The issue is actively being addressed'],
        ['RESOLVED', 'The issue has been addressed and closed'],
        ['REJECTED', 'The issue is not valid or not accepted under the defined policy']
    ]
    lifecycle_table = Table(lifecycle_data, colWidths=[120, 360])
    lifecycle_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
    ]))
    content.append(lifecycle_table)

    add_heading('9. Database Design and Data Model')
    content.append(Paragraph('The data model is designed to support secure, structured, and query-friendly operation. The main tables are users, submissions, student_submission_receipts, submission_hype, resolution_notes, and submission_history.', body_style))
    content.append(Paragraph('The most important design decision is that the submissions table does not store student identity. Instead, the student receipt mapping is stored separately and used only when a student needs to view their personal submissions. This is the core privacy mechanism of the system.', body_style))

    db_data = [
        ['Table', 'Purpose'],
        ['users', 'Stores login and role information for students and administrators'],
        ['submissions', 'Stores anonymous public issue and suggestion records'],
        ['student_submission_receipts', 'Links students to their own submissions without exposing identity to admin flows'],
        ['submission_hype', 'Stores peer upvotes and prevents double voting'],
        ['resolution_notes', 'Stores official admin action records linked to a ticket'],
        ['submission_history', 'Tracks every state transition for auditability']
    ]
    db_table = Table(db_data, colWidths=[170, 310])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
    ]))
    content.append(db_table)

    add_heading('10. Security Architecture')
    content.append(Paragraph('AURA incorporates multiple layers of security to protect confidential data and maintain integrity. Email validation restricts access to official institutional addresses, password hashing uses BCrypt, and SQL is accessed via prepared statements to prevent injection attacks.', body_style))
    content.append(Paragraph('The system also enforces role-based authorization, meaning that students cannot access admin functions and admins cannot query the private receipt data used by students. This is enforced in both UI and service logic and is a strong architectural safeguard.', body_style))

    add_heading('11. Technical Stack')
    tech_data = [
        ['Component', 'Choice'],
        ['Language', 'Java 17'],
        ['UI', 'Java Swing with FlatLaf'],
        ['Persistence', 'JDBC with PostgreSQL'],
        ['Database', 'Supabase PostgreSQL'],
        ['Security', 'BCrypt, domain validation, prepared statements'],
        ['Build Tool', 'Apache Maven'],
        ['Testing', 'JUnit 5']
    ]
    tech_table = Table(tech_data, colWidths=[170, 310])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F172A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8FAFC')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
    ]))
    content.append(tech_table)

    add_heading('12. Architectural Strengths')
    content.append(Paragraph('AURA demonstrates a well-structured and practically valid software architecture. It maintains proper boundary separation, active privacy protection, clear role division, efficient persistence design, and auditable state transitions. These qualities reflect strong academic and professional engineering practice.', body_style))

    add_heading('13. Conclusion')
    content.append(Paragraph('The system design and architecture of AURA are built around a real campus need: transparent, secure, and prioritized issue reporting. The project combines strong backend logic, institutional security rules, and a user-friendly desktop experience into one coherent design. This makes AURA a well-balanced academic project and a realistic software solution for campus governance.', body_style))

    doc.build(content)
    print(f'Created PDF at: {OUTPUT}')


if __name__ == '__main__':
    build_pdf()
