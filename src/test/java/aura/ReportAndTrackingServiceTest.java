package aura;

import aura.dao.ResolutionNoteDAO;
import aura.dao.SubmissionDAO;
import aura.dao.SubmissionHistoryDAO;
import aura.enums.Category;
import aura.enums.Priority;
import aura.enums.SubmissionStatus;
import aura.enums.SubmissionType;
import aura.model.ResolutionNote;
import aura.model.Submission;
import aura.model.SubmissionHistory;
import aura.service.ReportService;
import aura.service.TrackingService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/** Offline checks for dashboard metrics, CSV export and the status audit trail, using in-memory DAOs. */
class ReportAndTrackingServiceTest {

    private final List<Submission> store = new ArrayList<>();
    private final List<SubmissionHistory> history = new ArrayList<>();
    private final List<ResolutionNote> notes = new ArrayList<>();

    private final SubmissionDAO submissionDAO = new SubmissionDAO() {
        @Override
        public List<Submission> findAll() {
            return store;
        }

        @Override
        public Optional<Submission> findById(int id) {
            return store.stream().filter(s -> s.getSubmissionId() == id).findFirst();
        }

        @Override
        public void updateStatus(int id, SubmissionStatus status) {
            findById(id).ifPresent(s -> s.setStatus(status));
        }
    };

    private final SubmissionHistoryDAO historyDAO = new SubmissionHistoryDAO() {
        @Override
        public SubmissionHistory create(SubmissionHistory h) {
            history.add(h);
            return h;
        }
    };

    private final ResolutionNoteDAO noteDAO = new ResolutionNoteDAO() {
        @Override
        public ResolutionNote create(ResolutionNote n) {
            notes.add(n);
            return n;
        }
    };

    private ReportService reports;
    private TrackingService tracking;

    @BeforeEach
    void setUp() {
        store.add(submission(1, "Broken fan, CSE \"Lab 3\"", SubmissionStatus.PENDING, 4));
        store.add(submission(2, "Wi-Fi drops in library", SubmissionStatus.IN_PROGRESS, 12));
        store.add(submission(3, "Water cooler leak", SubmissionStatus.ASSIGNED, 2));
        store.add(submission(4, "Canteen hygiene", SubmissionStatus.RESOLVED, 7));
        store.add(submission(5, "Duplicate of #2", SubmissionStatus.REJECTED, 0));
        reports = new ReportService(submissionDAO);
        tracking = new TrackingService(submissionDAO, historyDAO, noteDAO);
    }

    @Test
    void dashboardCountsEachLifecycleBucket() {
        assertEquals(1, reports.getPendingCount());
        assertEquals(2, reports.getActiveCount(), "ASSIGNED and IN_PROGRESS are both active");
        assertEquals(1, reports.getResolvedCount());
        assertEquals(1, reports.getRejectedCount());
        assertEquals(2, reports.getTopHypedSubmission().orElseThrow().getSubmissionId());
    }

    @Test
    void csvEscapesQuotesAndCommasAndCarriesNoIdentity() {
        String[] lines = reports.generateCsvReport().split("\n");

        assertEquals(6, lines.length, "header plus one row per submission");
        assertFalse(lines[0].toLowerCase().matches(".*(student|email|user|receipt).*"),
                "export must not include identity columns");
        assertTrue(lines[1].startsWith("1,\"Broken fan, CSE \"\"Lab 3\"\"\",ISSUE,"),
                "titles are quoted and inner quotes doubled per RFC 4180: " + lines[1]);
    }

    @Test
    void statusChangeIsAuditedWithOldAndNewState() {
        tracking.updateStatus(1, SubmissionStatus.ASSIGNED, 9, "Admin");

        assertEquals(SubmissionStatus.ASSIGNED, store.get(0).getStatus());
        assertEquals(1, history.size());
        assertEquals(SubmissionStatus.PENDING, history.get(0).getOldStatus());
        assertEquals(SubmissionStatus.ASSIGNED, history.get(0).getNewStatus());
    }

    @Test
    void unchangedStatusWritesNoHistoryAndUnknownTicketIsRejected() {
        tracking.updateStatus(2, SubmissionStatus.IN_PROGRESS, 9, "Admin");
        assertTrue(history.isEmpty());

        assertThrows(IllegalArgumentException.class,
                () -> tracking.updateStatus(99, SubmissionStatus.RESOLVED, 9, "Admin"));
        assertThrows(IllegalArgumentException.class,
                () -> tracking.updateStatus(1, null, 9, "Admin"));
        assertTrue(history.isEmpty());
    }

    @Test
    void resolutionNoteIsTrimmedAndBlankNotesAreRejected() {
        tracking.addResolutionNote(4, 9, "Admin", "  Deep cleaned and inspected.  ");
        assertEquals("Deep cleaned and inspected.", notes.get(0).getNote());

        assertThrows(IllegalArgumentException.class, () -> tracking.addResolutionNote(4, 9, "Admin", "   "));
    }

    private static Submission submission(int id, String title, SubmissionStatus status, int hype) {
        Submission s = new Submission(id, title, "Description long enough", SubmissionType.ISSUE,
                Category.values()[0], "Main Block", Priority.MEDIUM);
        s.setStatus(status);
        s.setHypeCount(hype);
        s.setCreatedAt(LocalDateTime.of(2026, 10, 1, 9, 0));
        return s;
    }
}
