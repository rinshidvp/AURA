package aura.service;

import aura.config.DatabaseConfig;
import aura.dao.StudentReceiptDAO;
import aura.dao.SubmissionDAO;
import aura.dao.SubmissionHistoryDAO;
import aura.model.Submission;
import aura.model.SubmissionHistory;
import aura.util.ValidationUtil;

import java.sql.Connection;
import java.sql.SQLException;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

/**
 * Orchestrates campus submission lifecycles, feeds, and the Decoupled Anonymity Vault.
 */
public class SubmissionService {
    private final SubmissionDAO submissionDAO;
    private final StudentReceiptDAO studentReceiptDAO;
    private final SubmissionHistoryDAO submissionHistoryDAO;

    public SubmissionService() {
        this.submissionDAO = new SubmissionDAO();
        this.studentReceiptDAO = new StudentReceiptDAO();
        this.submissionHistoryDAO = new SubmissionHistoryDAO();
    }

    public SubmissionService(SubmissionDAO submissionDAO, StudentReceiptDAO studentReceiptDAO,
                             SubmissionHistoryDAO submissionHistoryDAO) {
        this.submissionDAO = submissionDAO;
        this.studentReceiptDAO = studentReceiptDAO;
        this.submissionHistoryDAO = submissionHistoryDAO;
    }

    public Submission createSubmission(Submission submission, int studentId) {
        if (submission == null) {
            throw new IllegalArgumentException("Submission cannot be null.");
        }
        ValidationUtil.validateSubmission(submission.getTitle(), submission.getDescription(), submission.getLocation());

        // All three writes commit together, so a report can never exist without its owner's receipt.
        try (Connection conn = DatabaseConfig.getConnection()) {
            conn.setAutoCommit(false);
            try {
                // 1. Store anonymous submission
                Submission saved = submissionDAO.create(conn, submission);

                // 2. Store private student receipt in the Anonymity Vault
                studentReceiptDAO.createReceipt(conn, studentId, saved.getSubmissionId());

                // 3. Record initial audit history
                SubmissionHistory initialHistory = new SubmissionHistory(
                        0, saved.getSubmissionId(), null, saved.getStatus(), studentId, "Student");
                submissionHistoryDAO.create(conn, initialHistory);

                conn.commit();
                return saved;
            } catch (RuntimeException e) {
                conn.rollback();
                throw e;
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error creating submission: " + e.getMessage(), e);
        }
    }

    public Optional<Submission> getSubmissionById(int submissionId) {
        return submissionDAO.findById(submissionId);
    }

    public List<Submission> getAllSubmissions() {
        return submissionDAO.findAll();
    }

    public List<Submission> getTrendingSubmissions() {
        return submissionDAO.findAll().stream()
                .sorted(Comparator.comparingInt(Submission::getHypeCount).reversed()
                        .thenComparing(Submission::getCreatedAt, Comparator.reverseOrder()))
                .collect(Collectors.toList());
    }

    public List<Submission> getRecentSubmissions() {
        return submissionDAO.findAll().stream()
                .sorted(Comparator.comparing(Submission::getCreatedAt).reversed())
                .collect(Collectors.toList());
    }

    /**
     * Resolves a student's personal submissions strictly through the Anonymity Vault receipts.
     */
    public List<Submission> getStudentSubmissions(int studentId) {
        List<Integer> allowedIds = studentReceiptDAO.findSubmissionIdsByStudentId(studentId);
        if (allowedIds.isEmpty()) {
            return Collections.emptyList();
        }
        return submissionDAO.findByIds(allowedIds);
    }
}
