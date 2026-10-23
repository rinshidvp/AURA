package aura.dao;

import aura.config.DatabaseConfig;
import aura.enums.Category;
import aura.enums.Priority;
import aura.enums.SubmissionStatus;
import aura.enums.SubmissionType;
import aura.model.Submission;

import java.sql.*;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

/**
 * Data Access Object for campus issues and suggestions.
 * 
 * CRITICAL ANONYMITY LAW:
 * This DAO holds NO references or columns for student_id. Submissions are
 * completely decoupled from author identities.
 */
public class SubmissionDAO {

    public Submission create(Submission submission) {
        try (Connection conn = DatabaseConfig.getConnection()) {
            return create(conn, submission);
        } catch (SQLException e) {
            throw new RuntimeException("Database error creating submission: " + e.getMessage(), e);
        }
    }

    /** Inserts on the caller's connection so it can join a wider transaction. */
    public Submission create(Connection conn, Submission submission) {
        String sql = "INSERT INTO submissions (title, description, type, category, location, priority, status, photo_url) " +
                     "VALUES (?, ?, ?, ?, ?, ?, ?, ?) RETURNING submission_id, created_at";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, submission.getTitle());
            ps.setString(2, submission.getDescription());
            ps.setString(3, submission.getType().name());
            ps.setString(4, submission.getCategory().name());
            ps.setString(5, submission.getLocation());
            ps.setString(6, submission.getPriority().name());
            ps.setString(7, submission.getStatus().name());
            ps.setString(8, submission.getPhotoUrl());

            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    submission.setSubmissionId(rs.getInt("submission_id"));
                    Timestamp ts = rs.getTimestamp("created_at");
                    if (ts != null) {
                        submission.setCreatedAt(ts.toLocalDateTime());
                    }
                    return submission;
                }
            }
            throw new SQLException("Failed to retrieve generated submission_id");
        } catch (SQLException e) {
            throw new RuntimeException("Database error creating submission: " + e.getMessage(), e);
        }
    }

    public Optional<Submission> findById(int submissionId) {
        String sql = "SELECT s.submission_id, s.title, s.description, s.type, s.category, s.location, " +
                     "       s.priority, s.status, s.photo_url, s.created_at, " +
                     "       COUNT(h.hype_id) AS hype_count " +
                     "FROM submissions s " +
                     "LEFT JOIN submission_hype h ON s.submission_id = h.submission_id " +
                     "WHERE s.submission_id = ? " +
                     "GROUP BY s.submission_id";
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, submissionId);
            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    return Optional.of(mapRow(rs));
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error finding submission by id: " + e.getMessage(), e);
        }
        return Optional.empty();
    }

    public List<Submission> findAll() {
        String sql = "SELECT s.submission_id, s.title, s.description, s.type, s.category, s.location, " +
                     "       s.priority, s.status, s.photo_url, s.created_at, " +
                     "       COUNT(h.hype_id) AS hype_count " +
                     "FROM submissions s " +
                     "LEFT JOIN submission_hype h ON s.submission_id = h.submission_id " +
                     "GROUP BY s.submission_id " +
                     "ORDER BY s.created_at DESC";
        List<Submission> list = new ArrayList<>();
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql);
             ResultSet rs = ps.executeQuery()) {
            while (rs.next()) {
                list.add(mapRow(rs));
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error fetching all submissions: " + e.getMessage(), e);
        }
        return list;
    }

    public List<Submission> findByIds(List<Integer> ids) {
        if (ids == null || ids.isEmpty()) {
            return Collections.emptyList();
        }

        // Build parameterized IN (?, ?, ...)
        StringBuilder sql = new StringBuilder(
            "SELECT s.submission_id, s.title, s.description, s.type, s.category, s.location, " +
            "       s.priority, s.status, s.photo_url, s.created_at, " +
            "       COUNT(h.hype_id) AS hype_count " +
            "FROM submissions s " +
            "LEFT JOIN submission_hype h ON s.submission_id = h.submission_id " +
            "WHERE s.submission_id IN ("
        );
        for (int i = 0; i < ids.size(); i++) {
            sql.append(i == 0 ? "?" : ", ?");
        }
        sql.append(") GROUP BY s.submission_id ORDER BY s.created_at DESC");

        List<Submission> list = new ArrayList<>();
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql.toString())) {
            for (int i = 0; i < ids.size(); i++) {
                ps.setInt(i + 1, ids.get(i));
            }
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    list.add(mapRow(rs));
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error finding submissions by ids: " + e.getMessage(), e);
        }
        return list;
    }

    public void updateStatus(int submissionId, SubmissionStatus status) {
        String sql = "UPDATE submissions SET status = ? WHERE submission_id = ?";
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setString(1, status.name());
            ps.setInt(2, submissionId);
            ps.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("Database error updating submission status: " + e.getMessage(), e);
        }
    }

    private Submission mapRow(ResultSet rs) throws SQLException {
        Submission sub = new Submission();
        sub.setSubmissionId(rs.getInt("submission_id"));
        sub.setTitle(rs.getString("title"));
        sub.setDescription(rs.getString("description"));
        sub.setType(SubmissionType.valueOf(rs.getString("type")));
        sub.setCategory(Category.valueOf(rs.getString("category")));
        sub.setLocation(rs.getString("location"));
        sub.setPriority(Priority.valueOf(rs.getString("priority")));
        sub.setStatus(SubmissionStatus.valueOf(rs.getString("status")));
        sub.setPhotoUrl(rs.getString("photo_url"));
        sub.setHypeCount(rs.getInt("hype_count"));

        Timestamp ts = rs.getTimestamp("created_at");
        if (ts != null) {
            sub.setCreatedAt(ts.toLocalDateTime());
        }
        return sub;
    }
}
