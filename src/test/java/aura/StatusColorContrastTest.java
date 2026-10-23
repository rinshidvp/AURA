package aura;

import aura.enums.SubmissionStatus;
import org.junit.jupiter.api.Test;

import java.awt.Color;

import static org.junit.jupiter.api.Assertions.assertTrue;

/** Every status badge must stay readable: WCAG AA requires a 4.5:1 text-to-background contrast ratio. */
class StatusColorContrastTest {

    @Test
    void everyStatusBadgeMeetsWcagAaContrast() {
        for (SubmissionStatus status : SubmissionStatus.values()) {
            double ratio = contrast(status.getForegroundColor(), status.getBackgroundColor());
            assertTrue(ratio >= 4.5, status + " badge contrast is only " + String.format("%.2f", ratio) + ":1");
        }
    }

    private static double contrast(Color a, Color b) {
        double la = luminance(a);
        double lb = luminance(b);
        return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
    }

    private static double luminance(Color c) {
        return 0.2126 * channel(c.getRed()) + 0.7152 * channel(c.getGreen()) + 0.0722 * channel(c.getBlue());
    }

    private static double channel(int value) {
        double v = value / 255.0;
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    }
}
