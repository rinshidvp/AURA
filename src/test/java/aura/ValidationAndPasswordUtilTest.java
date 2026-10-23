package aura;

import aura.util.PasswordUtil;
import aura.util.ValidationUtil;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/** Offline checks for the institutional domain gate, submission bounds and BCrypt hashing. */
class ValidationAndPasswordUtilTest {

    @Test
    void acceptsOnlyExactTkmceDomain() {
        assertTrue(ValidationUtil.isValidTkmceEmail("b25csb45@tkmce.ac.in"));
        assertTrue(ValidationUtil.isValidTkmceEmail("  Admin.Office@TKMCE.AC.IN  "));

        assertFalse(ValidationUtil.isValidTkmceEmail(null));
        assertFalse(ValidationUtil.isValidTkmceEmail("student@gmail.com"));
        assertFalse(ValidationUtil.isValidTkmceEmail("student@tkmce.ac.in.evil.com"));
        assertFalse(ValidationUtil.isValidTkmceEmail("student@fake-tkmce.ac.in"));
        assertFalse(ValidationUtil.isValidTkmceEmail("student@mail.tkmce.ac.in"));
        assertFalse(ValidationUtil.isValidTkmceEmail("@tkmce.ac.in"));
    }

    @Test
    void submissionBoundsAreEnforced() {
        assertDoesNotThrow(() -> ValidationUtil.validateSubmission(
                "Broken fan", "Ceiling fan in lab 3 is not working", "CSE Lab 3"));

        assertThrows(IllegalArgumentException.class,
                () -> ValidationUtil.validateSubmission("Fan", "Ceiling fan is not working", "CSE Lab 3"));
        assertThrows(IllegalArgumentException.class,
                () -> ValidationUtil.validateSubmission("x".repeat(201), "Ceiling fan is not working", "CSE Lab 3"));
        assertThrows(IllegalArgumentException.class,
                () -> ValidationUtil.validateSubmission("Broken fan", "short", "CSE Lab 3"));
        assertThrows(IllegalArgumentException.class,
                () -> ValidationUtil.validateSubmission("Broken fan", "Ceiling fan is not working", "   "));
    }

    @Test
    void passwordHashIsSaltedAndVerifiable() {
        String first = PasswordUtil.hashPassword("Aura@2026");
        String second = PasswordUtil.hashPassword("Aura@2026");

        assertNotEquals("Aura@2026", first);
        assertNotEquals(first, second, "each hash must use a fresh salt");
        assertTrue(first.startsWith("$2a$10$"), "work factor 10 is required");
        assertTrue(PasswordUtil.checkPassword("Aura@2026", first));
        assertFalse(PasswordUtil.checkPassword("aura@2026", first));
    }

    @Test
    void malformedPasswordInputsFailClosed() {
        assertThrows(IllegalArgumentException.class, () -> PasswordUtil.hashPassword(""));
        assertFalse(PasswordUtil.checkPassword(null, "$2a$10$abc"));
        assertFalse(PasswordUtil.checkPassword("secret", null));
        assertFalse(PasswordUtil.checkPassword("secret", "not-a-bcrypt-hash"));
    }
}
