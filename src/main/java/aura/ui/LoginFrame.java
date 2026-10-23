package aura.ui;

import aura.enums.Role;
import aura.model.User;
import aura.service.AuthService;
import aura.ui.admin.AdminDashboardFrame;
import aura.ui.common.ModernButton;
import aura.ui.common.UITheme;
import aura.ui.student.StudentDashboardFrame;

import javax.swing.*;
import javax.swing.border.EmptyBorder;
import java.awt.*;

/**
 * Modern login window for AURA.
 * Provides institutional email/password sign-in.
 */
public class LoginFrame extends JFrame {
    private final AuthService authService;

    private final JTextField emailField = new JTextField("student1@tkmce.ac.in");
    private final JPasswordField passwordField = new JPasswordField("password123");

    public LoginFrame() {
        this(new AuthService());
    }

    public LoginFrame(AuthService authService) {
        super("AURA — Institutional Sign In | TKMCE");
        this.authService = authService;

        setSize(500, 600);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);
        getContentPane().setBackground(UITheme.BG_BASE);

        initUI();
    }

    private void initUI() {
        JPanel root = new JPanel(new GridBagLayout());
        root.setOpaque(false);
        root.setBorder(new EmptyBorder(16, 20, 16, 20));

        JPanel card = new JPanel();
        card.setLayout(new BoxLayout(card, BoxLayout.Y_AXIS));
        card.setBackground(UITheme.BG_CARD);
        card.setBorder(UITheme.createCardBorder());
        card.setPreferredSize(new Dimension(420, 530));

        // Logo & Heading
        JLabel logo = new JLabel("⚡ AURA", SwingConstants.CENTER);
        logo.setFont(new Font("Segoe UI", Font.BOLD, 28));
        logo.setForeground(UITheme.PRIMARY_LIGHT);
        logo.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel subTitle = new JLabel("Autonomous University Response & Action");
        subTitle.setFont(UITheme.FONT_SMALL_BOLD);
        subTitle.setForeground(UITheme.TEXT_MUTED);
        subTitle.setAlignmentX(Component.CENTER_ALIGNMENT);

        JLabel collegeBadge = new JLabel("TKM College of Engineering");
        collegeBadge.setFont(UITheme.FONT_SMALL);
        collegeBadge.setForeground(UITheme.TEXT_SUBTLE);
        collegeBadge.setAlignmentX(Component.CENTER_ALIGNMENT);

        card.add(Box.createVerticalStrut(12));
        card.add(logo);
        card.add(Box.createVerticalStrut(4));
        card.add(subTitle);
        card.add(collegeBadge);
        card.add(Box.createVerticalStrut(18));

        // Inputs
        card.add(createInputSection("Email", emailField));
        card.add(Box.createVerticalStrut(10));
        card.add(createInputSection("Password", passwordField));
        card.add(Box.createVerticalStrut(16));

        // Sign In Button
        ModernButton loginBtn = new ModernButton("Sign In", ModernButton.Style.PRIMARY);
        loginBtn.setMaximumSize(new Dimension(Integer.MAX_VALUE, 38));
        loginBtn.setAlignmentX(Component.CENTER_ALIGNMENT);
        loginBtn.addActionListener(e -> handleLogin());
        card.add(loginBtn);
        card.add(Box.createVerticalStrut(16));

        // Quick Fill Demo Bar
        JLabel demoLabel = new JLabel("Quick Viva Demo Logins:");
        demoLabel.setFont(UITheme.FONT_SMALL_BOLD);
        demoLabel.setForeground(UITheme.TEXT_SUBTLE);
        demoLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        card.add(demoLabel);
        card.add(Box.createVerticalStrut(6));

        JPanel demoRow = new JPanel(new FlowLayout(FlowLayout.CENTER, 6, 0));
        demoRow.setOpaque(false);

        ModernButton demoStudent = new ModernButton("Student 1", ModernButton.Style.GHOST);
        demoStudent.setFont(UITheme.FONT_SMALL);
        demoStudent.addActionListener(e -> {
            emailField.setText("student1@tkmce.ac.in");
            passwordField.setText("password123");
        });

        ModernButton demoStudent2 = new ModernButton("Student 2", ModernButton.Style.GHOST);
        demoStudent2.setFont(UITheme.FONT_SMALL);
        demoStudent2.addActionListener(e -> {
            emailField.setText("student2@tkmce.ac.in");
            passwordField.setText("password123");
        });

        ModernButton demoAdmin = new ModernButton("Admin", ModernButton.Style.GHOST);
        demoAdmin.setFont(UITheme.FONT_SMALL);
        demoAdmin.addActionListener(e -> {
            emailField.setText("admin@tkmce.ac.in");
            passwordField.setText("admin123");
        });

        ModernButton demoEstate = new ModernButton("Estate", ModernButton.Style.GHOST);
        demoEstate.setFont(UITheme.FONT_SMALL);
        demoEstate.addActionListener(e -> {
            emailField.setText("estate@tkmce.ac.in");
            passwordField.setText("admin123");
        });

        demoRow.add(demoStudent);
        demoRow.add(demoStudent2);
        demoRow.add(demoAdmin);
        demoRow.add(demoEstate);
        card.add(demoRow);

        root.add(card);
        setContentPane(root);
    }

    private JPanel createInputSection(String labelText, JTextField field) {
        JPanel p = new JPanel(new BorderLayout(0, 4));
        p.setOpaque(false);
        p.setMaximumSize(new Dimension(Integer.MAX_VALUE, 58));

        JLabel lbl = new JLabel(labelText);
        lbl.setFont(UITheme.FONT_SMALL_BOLD);
        lbl.setForeground(UITheme.TEXT_MUTED);

        field.setFont(UITheme.FONT_BODY);
        field.setBackground(UITheme.BG_INPUT);
        field.setForeground(UITheme.TEXT_MAIN);
        field.setCaretColor(Color.WHITE);
        field.setBorder(BorderFactory.createCompoundBorder(
                UITheme.createSubtleBorder(),
                new EmptyBorder(8, 10, 8, 10)
        ));

        p.add(lbl, BorderLayout.NORTH);
        p.add(field, BorderLayout.CENTER);
        return p;
    }

    private void handleLogin() {
        String email = emailField.getText().trim();
        String pass = new String(passwordField.getPassword());

        try {
            User user = authService.authenticate(email, pass);
            routeToDashboard(user);
        } catch (IllegalArgumentException ex) {
            JOptionPane.showMessageDialog(this, ex.getMessage(), "Validation Notice", JOptionPane.WARNING_MESSAGE);
        } catch (SecurityException ex) {
            JOptionPane.showMessageDialog(this, ex.getMessage(), "Authentication Failed", JOptionPane.ERROR_MESSAGE);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Login error: " + ex.getMessage(), "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void routeToDashboard(User user) {
        dispose();
        SwingUtilities.invokeLater(() -> {
            if (user.getRole() == Role.ADMIN) {
                AdminDashboardFrame adminFrame = new AdminDashboardFrame();
                adminFrame.setVisible(true);
            } else {
                StudentDashboardFrame studentFrame = new StudentDashboardFrame();
                studentFrame.setVisible(true);
            }
        });
    }
}
