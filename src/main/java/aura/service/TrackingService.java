package aura.service;

import aura.dao.ResolutionNoteDAO;
import aura.dao.SubmissionDAO;
import aura.dao.SubmissionHistoryDAO;
import aura.enums.SubmissionStatus;
import aura.model.ResolutionNote;
import aura.model.Submission;
import aura.model.SubmissionHistory;

import java.util.List;
import java.util.Optional;

/**
 * Handles submission lifecycle tracking, status state transitions, and audit trails.
 */
public class TrackingService {
    private final SubmissionDAO submissionDAO;
    private final SubmissionHistoryDAO historyDAO;
    private final ResolutionNoteDAO noteDAO;

    public TrackingService() {
        this.submissionDAO = new SubmissionDAO();
        this.historyDAO = new SubmissionHistoryDAO();
        this.noteDAO = new ResolutionNoteDAO();
    }

    public TrackingService(SubmissionDAO submissionDAO, SubmissionHistoryDAO historyDAO, ResolutionNoteDAO noteDAO) {
        this.submissionDAO = submissionDAO;
        this.historyDAO = historyDAO;
        this.noteDAO = noteDAO;
    }

    public void updateStatus(int submissionId, SubmissionStatus newStatus, int adminId, String adminName) {
        if (newStatus == null) {
            throw new IllegalArgumentException("Target status cannot be null.");
        }

        Optional<Submission> currentOpt = submissionDAO.findById(submissionId);
        if (currentOpt.isEmpty()) {
            throw new IllegalArgumentException("Submission " + submissionId + " does not exist.");
        }
        SubmissionStatus oldStatus = currentOpt.get().getStatus();

        submissionDAO.updateStatus(submissionId, newStatus);

        // Only record real transitions, matching the web portal's portal_admin_update_submission RPC.
        if (oldStatus != newStatus) {
            SubmissionHistory history = new SubmissionHistory(0, submissionId, oldStatus, newStatus, adminId, adminName);
            historyDAO.create(history);
        }
    }

    public void addResolutionNote(int submissionId, int adminId, String adminName, String noteText) {
        if (noteText == null || noteText.trim().isEmpty()) {
            throw new IllegalArgumentException("Resolution note cannot be empty.");
        }
        ResolutionNote note = new ResolutionNote(0, submissionId, adminId, adminName, noteText.trim());
        noteDAO.create(note);
    }

    public List<ResolutionNote> getResolutionNotes(int submissionId) {
        return noteDAO.findBySubmissionId(submissionId);
    }

    public List<SubmissionHistory> getSubmissionHistory(int submissionId) {
        return historyDAO.findBySubmissionId(submissionId);
    }
}
