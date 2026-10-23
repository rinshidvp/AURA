package aura.dao;

import aura.config.DatabaseConfig;
import aura.enums.SubmissionStatus;
import aura.model.SubmissionHistory;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

/**
 * Data Access Object for submission lifecycle audit events (submission_history).
 */
public class SubmissionHistoryDAO {

    public SubmissionHistory create(SubmissionHistory history) {
        try (Connection conn = DatabaseConfig.getConnection()) {
            return create(conn, history);
        } catch (SQLException e) {
            throw new RuntimeException("Database error recording submission history: " + e.getMessage(), e);
        }
    }

    /** Inserts on the caller's connection so it can join a wider transaction. */
    public SubmissionHistory create(Connection conn, SubmissionHistory history) {
        String sql = "INSERT INTO submission_history (submission_id, changed_by, old_status, new_status) " +
                     "VALUES (?, ?, ?, ?) RETURNING history_id, changed_at";
        try (PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, history.getSubmissionId());
            ps.setInt(2, history.getChangedBy() > 0 ? history.getChangedBy() : 1);
            ps.setString(3, history.getOldStatus() != null ? history.getOldStatus().name() : "NONE");
            ps.setString(4, history.getNewStatus().name());

            try (ResultSet rs = ps.executeQuery()) {
                if (rs.next()) {
                    history.setHistoryId(rs.getInt("history_id"));
                    Timestamp ts = rs.getTimestamp("changed_at");
                    if (ts != null) {
                        history.setChangedAt(ts.toLocalDateTime());
                    }
                    return history;
                }
            }
            throw new SQLException("Failed to retrieve generated history_id");
        } catch (SQLException e) {
            throw new RuntimeException("Database error recording submission history: " + e.getMessage(), e);
        }
    }

    public List<SubmissionHistory> findBySubmissionId(int submissionId) {
        String sql = "SELECT sh.history_id, sh.submission_id, sh.old_status, sh.new_status, sh.changed_by, " +
                     "       COALESCE(u.name, 'System') AS changed_by_name, sh.changed_at " +
                     "FROM submission_history sh " +
                     "LEFT JOIN users u ON sh.changed_by = u.user_id " +
                     "WHERE sh.submission_id = ? " +
                     "ORDER BY sh.changed_at ASC";
        List<SubmissionHistory> list = new ArrayList<>();
        try (Connection conn = DatabaseConfig.getConnection();
             PreparedStatement ps = conn.prepareStatement(sql)) {
            ps.setInt(1, submissionId);
            try (ResultSet rs = ps.executeQuery()) {
                while (rs.next()) {
                    SubmissionHistory history = new SubmissionHistory();
                    history.setHistoryId(rs.getInt("history_id"));
                    history.setSubmissionId(rs.getInt("submission_id"));
                    String oldStatusStr = rs.getString("old_status");
                    if (oldStatusStr != null && !"NONE".equalsIgnoreCase(oldStatusStr)) {
                        try {
                            history.setOldStatus(SubmissionStatus.valueOf(oldStatusStr));
                        } catch (IllegalArgumentException ignored) {}
                    }
                    history.setNewStatus(SubmissionStatus.valueOf(rs.getString("new_status")));
                    history.setChangedBy(rs.getInt("changed_by"));
                    history.setChangedByName(rs.getString("changed_by_name"));
                    Timestamp ts = rs.getTimestamp("changed_at");
                    if (ts != null) {
                        history.setChangedAt(ts.toLocalDateTime());
                    }
                    list.add(history);
                }
            }
        } catch (SQLException e) {
            throw new RuntimeException("Database error finding submission history: " + e.getMessage(), e);
        }
        return list;
    }
}
