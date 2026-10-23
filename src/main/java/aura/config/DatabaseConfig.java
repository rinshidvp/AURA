package aura.config;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

/**
 * Reads db.properties from the classpath and supplies JDBC Connections to the DAO layer.
 * Enforces single-use connections per operation using try-with-resources.
 */
public final class DatabaseConfig {

    private static final String URL;
    private static final String USER;
    private static final String PASSWORD;
    private static final String DRIVER;
    private static volatile Boolean reachable;

    static {
        // Cache DNS lookups for pooler host to prevent intermittent DNS resolution drops
        java.security.Security.setProperty("networkaddress.cache.ttl", "300");
        java.security.Security.setProperty("networkaddress.cache.negative.ttl", "0");

        Properties props = new Properties();
        try (InputStream in = DatabaseConfig.class.getResourceAsStream("/db.properties")) {
            if (in != null) {
                props.load(in);
            } else {
                try (InputStream exIn = DatabaseConfig.class.getResourceAsStream("/db.properties.example")) {
                    if (exIn != null) {
                        props.load(exIn);
                    }
                }
            }
        } catch (IOException ignored) {
            // Handled via environment variable fallback below
        }

        // Environment variables take precedence (standard for CI/CD and production containers)
        String envUrl = System.getenv("DB_URL");
        String envUser = System.getenv("DB_USER");
        String envPassword = System.getenv("DB_PASSWORD");
        String envDriver = System.getenv("DB_DRIVER");

        URL = (envUrl != null && !envUrl.isBlank()) ? envUrl : props.getProperty("db.url", "");
        USER = (envUser != null && !envUser.isBlank()) ? envUser : props.getProperty("db.user", "");
        PASSWORD = (envPassword != null && !envPassword.isBlank()) ? envPassword : props.getProperty("db.password", "");
        DRIVER = (envDriver != null && !envDriver.isBlank()) ? envDriver : props.getProperty("db.driver", "org.postgresql.Driver");

        try {
            Class.forName(DRIVER);
        } catch (ClassNotFoundException e) {
            throw new ExceptionInInitializerError("PostgreSQL JDBC Driver not found on classpath: " + e.getMessage());
        }
    }

    private DatabaseConfig() {
        // Utility class
    }

    /**
     * Checks whether valid database credentials are configured (i.e. not the unreplaced example template).
     */
    public static boolean isConfigured() {
        return URL != null && !URL.isBlank() && !URL.contains("[YOUR_PROJECT_REF]") && !USER.isBlank();
    }

    /**
     * Checks whether the configured database can be reached without exposing
     * connection failures as false-positive integration test failures.
     */
    public static boolean isReachable() {
        if (!isConfigured()) {
            return false;
        }
        if (reachable != null) {
            return reachable;
        }
        synchronized (DatabaseConfig.class) {
            if (reachable != null) {
                return reachable;
            }
            try (Connection ignored = getConnection()) {
                reachable = true;
            } catch (SQLException e) {
                reachable = false;
            }
        }
        return reachable;
    }

    /**
     * Obtains a new live JDBC Connection to Supabase PostgreSQL with retry resilience.
     * Callers MUST close the connection using try-with-resources.
     */
    public static Connection getConnection() throws SQLException {
        SQLException lastEx = null;
        for (int attempt = 1; attempt <= 3; attempt++) {
            try {
                return DriverManager.getConnection(URL, USER, PASSWORD);
            } catch (SQLException e) {
                lastEx = e;
                try {
                    Thread.sleep(400);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new SQLException("Connection attempt interrupted: " + ie.getMessage(), ie);
                }
            }
        }
        throw lastEx;
    }
}
