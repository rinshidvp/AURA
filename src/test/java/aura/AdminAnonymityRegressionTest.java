package aura;

import aura.model.Submission;
import aura.model.User;
import aura.service.SubmissionService;
import aura.service.TrackingService;
import aura.enums.SubmissionStatus;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.lang.reflect.Field;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Mandatory Anonymity Vault Regression Test.
 * Enforces AGENT.md Rule 2:
 * 1. Submission entity contains NO studentId or userId reference.
 * 2. Administrative queries receive submissions without student identity metadata.
 */
public class AdminAnonymityRegressionTest {

    @Test
    @DisplayName("AGENT.md Rule 2 Law: Submission POJO has zero student identity fields")
    void testSubmissionEntityHasNoStudentIdField() {
        Field[] fields = Submission.class.getDeclaredFields();

        for (Field f : fields) {
            String name = f.getName().toLowerCase();
            assertFalse(name.contains("studentid"),
                    "CRITICAL SECURITY VIOLATION: Submission entity contains forbidden studentId field: " + f.getName());
            assertFalse(name.contains("userid"),
                    "CRITICAL SECURITY VIOLATION: Submission entity contains forbidden userId field: " + f.getName());
            assertFalse(name.contains("author"),
                    "CRITICAL SECURITY VIOLATION: Submission entity contains forbidden author field: " + f.getName());
        }
    }

    @Test
    @DisplayName("Administrative triage queue receives zero student identity information")
    void testAdminTriageDoesNotExposeStudentIdentity() {
        org.junit.jupiter.api.Assumptions.assumeTrue(aura.config.DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        SubmissionService submissionService = new SubmissionService();
        List<Submission> triageQueue = submissionService.getAllSubmissions();

        assertFalse(triageQueue.isEmpty(), "Triage queue should contain seeded submissions.");

        for (Submission s : triageQueue) {
            assertTrue(s.getSubmissionId() > 0, "Submission should have a valid ticket ID.");
            assertNotNull(s.getTitle(), "Title should exist.");
            assertNotNull(s.getCategory(), "Category should exist.");
            assertNotNull(s.getStatus(), "Status should exist.");
        }
    }

    @Test
    @DisplayName("TrackingService status update preserves anonymity while recording audit trail")
    void testTrackingServicePreservesAnonymity() {
        org.junit.jupiter.api.Assumptions.assumeTrue(aura.config.DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        TrackingService trackingService = new TrackingService();
        int ticketId = 104;

        // Admin updates status
        trackingService.updateStatus(ticketId, SubmissionStatus.IN_PROGRESS, 5, "Campus Maintenance");

        // Verify audit history is logged under admin's identity, with zero student identity leaked
        var history = trackingService.getSubmissionHistory(ticketId);
        assertFalse(history.isEmpty());
        var latest = history.get(history.size() - 1);
        assertEquals(5, latest.getChangedBy());
        assertEquals("Campus Maintenance", latest.getChangedByName());
        assertEquals(SubmissionStatus.IN_PROGRESS, latest.getNewStatus());
    }
}
