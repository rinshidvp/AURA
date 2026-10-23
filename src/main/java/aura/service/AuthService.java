package aura.service;

import aura.dao.UserDAO;
import aura.model.User;
import aura.util.PasswordUtil;
import aura.util.SessionContext;
import aura.util.ValidationUtil;

import java.util.Optional;

/**
 * Handles institutional email/password authentication and session lifecycle.
 */
public class AuthService {
    private final UserDAO userDAO;

    public AuthService() {
        this.userDAO = new UserDAO();
    }

    public AuthService(UserDAO userDAO) {
        this.userDAO = userDAO;
    }

    public User authenticate(String email, String password) {
        if (email == null || email.trim().isEmpty()) {
            throw new IllegalArgumentException("Email address is required.");
        }
        if (!ValidationUtil.isValidTkmceEmail(email)) {
            throw new IllegalArgumentException("Institutional login requires a valid @tkmce.ac.in email.");
        }
        if (password == null || password.isEmpty()) {
            throw new IllegalArgumentException("Password is required.");
        }

        // One message for both cases so the login form cannot be used to discover registered emails.
        Optional<User> userOpt = userDAO.findByEmail(email.trim());
        if (userOpt.isEmpty() || !PasswordUtil.checkPassword(password, userOpt.get().getPasswordHash())) {
            throw new SecurityException("Invalid email or password.");
        }

        User user = userOpt.get();

        SessionContext.setCurrentUser(user);
        return user;
    }

    public void logout() {
        SessionContext.clear();
    }
}
