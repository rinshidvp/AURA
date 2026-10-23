package aura;

import aura.dao.UserDAO;
import aura.enums.Role;
import aura.model.User;
import aura.service.AuthService;
import aura.util.PasswordUtil;
import aura.util.SessionContext;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

/** Validates the desktop email/password authentication boundary. */
class AuthServiceTest {

    private AuthService authService;

    @BeforeEach
    void setUp() {
        authService = new AuthService();
        SessionContext.clear();
    }

    @Test
    void rejectsNonInstitutionalEmailBeforeDatabaseLookup() {
        assertThrows(IllegalArgumentException.class,
                () -> authService.authenticate("student@gmail.com", "password"));
    }

    @Test
    void rejectsMissingEmailOrPasswordBeforeDatabaseLookup() {
        assertThrows(IllegalArgumentException.class,
                () -> authService.authenticate("", "password"));
        assertThrows(IllegalArgumentException.class,
                () -> authService.authenticate("student@tkmce.ac.in", ""));
    }

    @Test
    void unknownEmailAndWrongPasswordAreIndistinguishable() {
        User known = new User(1, "Student", "student@tkmce.ac.in", PasswordUtil.hashPassword("Correct#1"), Role.STUDENT);
        AuthService service = new AuthService(new UserDAO() {
            @Override
            public Optional<User> findByEmail(String email) {
                return email.equalsIgnoreCase(known.getEmail()) ? Optional.of(known) : Optional.empty();
            }
        });

        String unknown = assertThrows(SecurityException.class,
                () -> service.authenticate("nobody@tkmce.ac.in", "Correct#1")).getMessage();
        String wrong = assertThrows(SecurityException.class,
                () -> service.authenticate("student@tkmce.ac.in", "Wrong#1")).getMessage();

        assertEquals(unknown, wrong, "login errors must not reveal which emails are registered");
        assertNull(SessionContext.getCurrentUser());
        assertEquals(1, service.authenticate("student@tkmce.ac.in", "Correct#1").getUserId());
    }
}
