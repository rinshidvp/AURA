package aura.dao;

import aura.config.DatabaseConfig;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Data Access Object for the Decoupled Anonymity Vault (student_submission_receipts).
 * 
 * CRITICAL ANONYMITY LAW:
 * This DAO holds the cryptographic/relational bridge that allows a student to view
 * "My Submissions" without EVER storing student_id in the public submissions table.
 * 
 * Under university safety compliance, NO administrative code path or admin service
 * may ever invoke this DAO.
 */
public class StudentReceiptDAO {

    public void createReceipt(int studentId, int submissionId) {
        try (Connection conn = DatabaseConfig.getConnection()) {
            createReceipt(conn, studentId, submissionId);
        } catch (SQLException e) {
            throw new RuntimeException("Database error storing anonymity receipt: " + e.getMessage(), e);
        }
    }

    /** Inserts on the caller's connection so it can join a wider transaction. */
    public void createReceipt(Connection conn, int studentId, int submissionId) {
        String sql = "INSERT INTO student_submission_receipts (student_id, submission_id) VALUES (?, ?) " +
                     "ON CONFLICT (student_id, submission_id) DO NOTHING";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, studentId);
            ps.setInt(2, submissionId);
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("Database error storing anonymity receipt: " + e.getMessage(), e);
        }
    }

    public List<Integer> findSubmissionIdsByStudentId(int studentId) {
        String sql = "SELECT submission_id FROM student_submission_receipts WHERE student_id = ? ORDER BY receipt_id DESC";
        List<Integer> submissionIds = new ArrayList<>();
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, studentId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    submissionIds.add(rs.getInt("submission_id"));
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error reading student receipts: " + e.getMessage(), e);
        }
        return submissionIds;
    }

    public boolean hasReceipt(int studentId, int submissionId) {
        String sql = "SELECT 1 FROM student_submission_receipts WHERE student_id = ? AND submission_id = ?";
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, studentId);
            ps.setInt(2, submissionId);
            try (ResultSet rs = ps.executeQuery()) {
                return rs.next();
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error verifying student receipt: " + e.getMessage(), e);
        }
    }
}
