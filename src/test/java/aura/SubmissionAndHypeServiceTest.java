package aura;

import aura.enums.Category;
import aura.enums.Priority;
import aura.enums.SubmissionStatus;
import aura.enums.SubmissionType;
import aura.model.Submission;
import aura.model.User;
import aura.service.AuthService;
import aura.service.HypeService;
import aura.service.ReportService;
import aura.service.SubmissionService;
import aura.util.ValidationUtil;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests verifying submission lifecycle, Anonymity Vault receipt mappings,
 * Hype upvote rules, and Report generation.
 */
public class SubmissionAndHypeServiceTest {
    private SubmissionService submissionService;
    private HypeService hypeService;
    private AuthService authService;
    private ReportService reportService;

    @BeforeEach
    void setUp() {
        submissionService = new SubmissionService();
        hypeService = new HypeService();
        authService = new AuthService();
        reportService = new ReportService();
    }

    @Test
    @DisplayName("Email domain validation strictly requires @tkmce.ac.in")
    void testEmailValidation() {
        assertTrue(ValidationUtil.isValidTkmceEmail("student1@tkmce.ac.in"));
        assertTrue(ValidationUtil.isValidTkmceEmail("admin@tkmce.ac.in"));
        assertFalse(ValidationUtil.isValidTkmceEmail("student@gmail.com"));
        assertFalse(ValidationUtil.isValidTkmceEmail("user@yahoo.com"));
        assertFalse(ValidationUtil.isValidTkmceEmail(""));
        assertFalse(ValidationUtil.isValidTkmceEmail(null));
    }

    @Test
    @DisplayName("AuthService successfully authenticates valid TKMCE credentials")
    void testAuthServiceSuccess() {
        org.junit.jupiter.api.Assumptions.assumeTrue(aura.config.DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        User user = authService.authenticate("student1@tkmce.ac.in", "password123");
        assertNotNull(user);
        assertEquals("Muhammed Rinshid VP", user.getName());
        assertTrue(user.isStudent());
    }

    @Test
    @DisplayName("AuthService rejects non-institutional emails and invalid passwords")
    void testAuthServiceFailures() {
        org.junit.jupiter.api.Assumptions.assumeTrue(aura.config.DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        assertThrows(IllegalArgumentException.class, () ->
                authService.authenticate("outsider@gmail.com", "password123"));

        assertThrows(SecurityException.class, () ->
                authService.authenticate("student1@tkmce.ac.in", "wrongPassword"));
    }

    @Test
    @DisplayName("Submission creation registers private receipt in Anonymity Vault")
    void testSubmissionCreationAndVaultReceipt() {
        org.junit.jupiter.api.Assumptions.assumeTrue(aura.config.DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        int studentId = 1;
        Submission newSub = new Submission(0, "Broken Switchboard in Seminar Hall",
                "Two main sockets are non-functional causing projector disconnections.",
                SubmissionType.ISSUE, Category.ELECTRICAL, "Seminar Hall 2", Priority.HIGH);

        Submission created = submissionService.createSubmission(newSub, studentId);
        assertTrue(created.getSubmissionId() > 0);

        // Verify it appears in "My Submissions" for Student 1
        List<Submission> mySubs = submissionService.getStudentSubmissions(studentId);
        boolean found = mySubs.stream().anyMatch(s -> s.getSubmissionId() == created.getSubmissionId());
        assertTrue(found, "Newly created submission must appear in author's Anonymity Vault view.");

        // Verify it does NOT appear in Student 2's private vault
        List<Submission> otherStudentSubs = submissionService.getStudentSubmissions(2);
        boolean foundInOther = otherStudentSubs.stream().anyMatch(s -> s.getSubmissionId() == created.getSubmissionId());
        assertFalse(foundInOther, "Submission must not appear in other student's vault.");
    }

    @Test
    @DisplayName("Hype upvoting enforces one vote per student with toggle behavior")
    void testHypeToggling() {
        org.junit.jupiter.api.Assumptions.assumeTrue(aura.config.DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        int subId = 85;
        int studentId = 3;

        int initialCount = hypeService.getHypeCount(subId);
        assertFalse(hypeService.hasStudentHyped(subId, studentId));

        // Upvote
        boolean firstToggle = hypeService.toggleHype(subId, studentId);
        assertTrue(firstToggle, "First toggle should add hype.");
        assertTrue(hypeService.hasStudentHyped(subId, studentId));
        assertEquals(initialCount + 1, hypeService.getHypeCount(subId));

        // Toggle again (remove upvote)
        boolean secondToggle = hypeService.toggleHype(subId, studentId);
        assertFalse(secondToggle, "Second toggle should remove hype.");
        assertFalse(hypeService.hasStudentHyped(subId, studentId));
        assertEquals(initialCount, hypeService.getHypeCount(subId));
    }

    @Test
    @DisplayName("ReportService generates RFC-4180 compliant CSV")
    void testReportServiceCsvGeneration() {
        org.junit.jupiter.api.Assumptions.assumeTrue(aura.config.DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        String csv = reportService.generateCsvReport();
        assertNotNull(csv);
        assertTrue(csv.contains("Submission ID,Title,Type,Category,Location,Priority,Status,Hype Count,Created At"));
        assertTrue(csv.contains("Lab 3 Projector Lamp Faulty"));
    }
}
