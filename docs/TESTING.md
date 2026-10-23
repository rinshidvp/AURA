# Testing Strategy & Verification Plan — AURA

**Autonomous University Response and Action**  
Department of Computer Science & Engineering, TKM College of Engineering (TKMCE)  
Testing Framework: JUnit 5 (Jupiter) • Presentation Reference: [`docs/AURA.pdf`](AURA.pdf) (Slide 15, 28)

---

## 1. Testing Philosophy & Definition of Done

In accordance with [`AGENT.md`](../AGENT.md), every class created in `aura.dao` and `aura.service` must be accompanied by an automated JUnit 5 test class. A feature is only considered "Done" when its corresponding test suite passes cleanly.

### Testing Objectives:
1. **Data Integrity:** Verify that database constraints (`UNIQUE`, `CHECK`, foreign keys) are strictly enforced.
2. **Business Rules:** Ensure duplicate votes are blocked, invalid emails are rejected, and state transitions follow the 5-state lifecycle.
3. **Anonymity Boundary Verification:** Execute automated regression tests proving that administrative code paths cannot access student identities.

---

## 2. Test Suite Structure

```
src/test/java/aura/
├── AuthServiceTest.java                    # Domain + blank-credential rejection, no user enumeration (offline)
├── ValidationAndPasswordUtilTest.java      # @tkmce.ac.in gate, submission bounds, BCrypt salt/work factor (offline)
├── ReportAndTrackingServiceTest.java       # Dashboard counts, RFC 4180 CSV, status audit trail, notes (offline, in-memory DAOs)
├── StatusColorContrastTest.java            # Every status badge meets WCAG AA 4.5:1 contrast (offline)
├── AdminAnonymityRegressionTest.java       # Submission model has no author field + admin queue leaks no identity (DB)
├── security/AdminAnonymityRegressionTest.java # Reflection scan: Submission exposes no student/user accessor (offline)
├── SubmissionAndHypeServiceTest.java       # Submission pipeline, receipts, single-vote hype enforcement (DB)
└── SupabaseConnectionTest.java             # Live Supabase connectivity smoke test (DB)

tests/                                      # Web portal (Node + Playwright)
├── config-api.test.js                      # /api/config exposes only public URL + anon key; rejects bad origins
├── db-portal.test.js                       # sql/web_portal.sql on in-memory Postgres: roles, RPC grants, receipt isolation
└── portal.spec.js                          # 13 browser flows: sign-in gate, student/admin, no-demo checks, mobile, session expiry
```

**Current result (2026-10-18):** Java 24/24 pass against the live Supabase database (offline, the 8 database tests skip and 16 pass). Web 17/17 pass.

---

## 3. Key Regression Tests

### 3.1 Duplicate Hype Prevention (`SubmissionAndHypeServiceTest`)
A second hype by the same student on the same submission is rejected; the composite `UNIQUE (submission_id, student_id)` constraint backs this at the database level.

### 3.2 Institutional Domain Gate (`AuthServiceTest`, `ValidationAndPasswordUtilTest`)
`student@gmail.com`, `student@tkmce.ac.in.evil.com`, `student@fake-tkmce.ac.in` and sub-domain addresses are rejected before any database lookup:
```java
assertThrows(IllegalArgumentException.class,
        () -> authService.authenticate("student@gmail.com", "password"));
assertFalse(ValidationUtil.isValidTkmceEmail("student@tkmce.ac.in.evil.com"));
```

### 3.3 Status Audit Trail (`ReportAndTrackingServiceTest`)
Every real status change writes a `submission_history` row with old and new state; a no-op change writes nothing and an unknown ticket is rejected, matching the web portal's `portal_admin_update_submission` RPC.

### 3.4 Admin Anonymity Regression (`AdminAnonymityRegressionTest`)
Reflection proves `Submission` has no student/user field or accessor, and the admin queue returned from the database carries no identity metadata. The web equivalent (`db-portal.test.js`) proves an ADMIN session gets a permission error from the receipt RPC.

---

## 4. Test Environment Isolation

Tests run against an isolated test database configured in `src/test/resources/db.properties`. Maven Surefire places `target/test-classes` ahead of `target/classes` on the test classpath, ensuring that production or dev database tables are never modified during test execution:

```bash
# Run the complete automated test suite
mvn test
```

Database integration tests use `DatabaseConfig.isReachable()` and are skipped when no usable Supabase database is available; they run when valid, reachable credentials are supplied. The source/model regression tests still run offline.

---

## 5. Web Portal Authentication and Interaction Tests

The web suite runs the portal SQL migration against an isolated in-memory PostgreSQL instance, verifying profile provisioning, student/admin authorization, denied direct table access, report/upvote persistence, status/history/note writes, and receipt isolation. Its Playwright suite mocks the external Supabase/Auth boundary while exercising the real page, handlers, and user-visible results: signed-out gate, unapproved identity handling, student/admin controls, navigation/search/filtering, report creation and receipts, upvote toggling, admin status/resolution updates, CSV export, QR/copy behavior, mobile navigation, session expiry, and missing configuration. It also covers the public home page (section links, FAQ, theme toggle), the absence of any demo or sample-data path (including the retired `#/demo` link) and no horizontal scrolling at phone widths.

```bash
npm ci
npx playwright install chromium
npm run test:web
```

The test adapter does not verify real Supabase credentials, SQL permissions, or deployment variables. Complete the real-account human acceptance checklist in [`WEB_PORTAL_AUTH.md`](WEB_PORTAL_AUTH.md) after applying [`../sql/web_portal.sql`](../sql/web_portal.sql) and configuring Vercel/Supabase.
