package aura;

import aura.config.DatabaseConfig;
import aura.util.PasswordUtil;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.sql.Connection;
import java.sql.DatabaseMetaData;
import java.sql.ResultSet;
import java.sql.Statement;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class SupabaseConnectionTest {

    @Test
    @DisplayName("Verify live Supabase PostgreSQL database connectivity and tables")
    public void testSupabaseConnection() throws Exception {
        org.junit.jupiter.api.Assumptions.assumeTrue(DatabaseConfig.isReachable(),
                "Skipping live DB integration test: Supabase database is not configured or reachable");

        try (Connection conn = DatabaseConfig.getConnection()) {
            assertNotNull(conn, "Connection should not be null");
            System.out.println("SUCCESSFULLY CONNECTED TO SUPABASE POSTGRESQL!");

            DatabaseMetaData meta = conn.getMetaData();
            System.out.println("Database Product Name: " + meta.getDatabaseProductName());
            System.out.println("Database Product Version: " + meta.getDatabaseProductVersion());

            // Check existing tables in public schema
            System.out.println("\n--- Existing Tables in 'public' schema ---");
            int tableCount = 0;
            try (ResultSet rs = meta.getTables(null, "public", "%", new String[]{"TABLE"})) {
                while (rs.next()) {
                    String tableName = rs.getString("TABLE_NAME");
                    System.out.println("Found table: " + tableName);
                    tableCount++;
                }
            }
            assertTrue(tableCount >= 6, "Expected at least 6 application tables in public schema");

            // Verify users and BCrypt credentials (for seeded demo accounts)
            try (Statement stmt = conn.createStatement();
                 ResultSet rs = stmt.executeQuery("SELECT user_id, email, password_hash, role FROM users")) {
                int userCount = 0;
                while (rs.next()) {
                    userCount++;
                    String hash = rs.getString("password_hash");
                    String role = rs.getString("role");

                    // OAuth-provisioned accounts use OAUTH_GOOGLE token placeholder instead of BCrypt password
                    if ("OAUTH_GOOGLE".equals(hash)) {
                        continue;
                    }

                    boolean matches = "STUDENT".equals(role)
                            ? PasswordUtil.checkPassword("password123", hash)
                            : PasswordUtil.checkPassword("admin123", hash);
                    assertTrue(matches, "Password hash must match demo password for " + rs.getString("email"));
                }
                assertTrue(userCount >= 5, "Expected at least 5 seeded users");
            }
        }
    }
}
