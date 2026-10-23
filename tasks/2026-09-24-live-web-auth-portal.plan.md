# Live Web Authentication and Portal Plan

## Goal

Replace the public static demo behavior in `index.html` with a live web portal where authenticated TKMCE users receive only their database-assigned role, and portal actions persist through Supabase under database-enforced authorization. Verify the user-visible flows for signed-out visitors, students, administrators, and rejected identities.

## Scope

### In scope

- Supabase Auth email/password sign-in/out for the hosted Vercel portal. Google OAuth is not part of the web login surface.
- Institutional domain enforcement and role retrieval from trusted `public.users` data.
- Database authorization for all web reads/writes, including the anonymity receipt boundary.
- Live feed/search/filter/trending, report creation, upvotes, private student receipts, administrative status/resolution updates, statistics, and CSV export.
- Responsive login/signed-out states, action feedback, and human-led live verification instructions.
- Automated web flow checks plus the existing Java regression suite.

### Out of scope

- Replacing the Java desktop application's authentication or data layer.
- Self-service registration or role promotion to ADMIN.
- Exposing a Supabase service-role key or database password to the browser.
- Changing the approved domain or data model's anonymity guarantee.

## Data and authorization contract

- Authenticated identity: Supabase Auth email/password session; account creation remains admin-provisioned outside the portal.
- Institutional identity: verified email must end exactly in `@tkmce.ac.in` (case-insensitive).
- Application role: resolved from the existing `public.users` row matching the authenticated email; only `STUDENT` and `ADMIN` are valid. The client cannot select or change its own role.
- Existing `public.users` rows remain the source of role assignment. Auth accounts are provisioned separately from application profiles; an account without a matching row is denied, and only explicitly managed rows can retain `ADMIN`.
- Submissions remain author-free. The private receipt mapping is accessible only to its owning student. Administrative access must never query or expose `student_submission_receipts`.
- Supabase anon/publishable key may be delivered to the browser; privileged keys remain server-side and are not required for the static portal.

## Orchestration

1. Portal boot reads only public Supabase configuration, restores the Supabase Auth session, and renders a signed-out gate until identity and role are resolved.
2. The user submits an institutional email and password; Supabase Auth validates the credentials and returns a browser session.
3. The client verifies the email domain for UX and loads the matching `public.users` role. Database policies independently enforce identity, domain, role, and ownership for every operation.
4. Portal data loads from Supabase. Search, category filters, tabs, and rendering operate on fetched data; mutations call authorized database operations and refresh affected views.
5. Sign-out clears the session and returns to the signed-out gate. Expired/invalid sessions and permission denials produce a safe message and never retain admin UI state.

## Key decisions

- Use Supabase Auth email/password in the browser, not Google OAuth or the Java loopback flow: the deployed Vercel application needs one direct credential path.
- Keep existing `public.users` roles authoritative; do not trust local storage, URL parameters, or client-side mode controls.
- Use database-side RPCs for all browser data access, including multi-row report creation and status/history/note changes so related writes are atomic. Revoke browser-role table privileges and grant only the narrowly scoped RPCs; keep the existing privileged JDBC data path compatible.
- Do not enable broad anonymous table access. Only signed-in approved students/admins can use application data; student receipt access remains narrowly scoped.
- Provide configuration documentation for Supabase URL, publishable anon key, email provider settings, and migration application. Never commit actual secrets.

## Components and contracts

- `index.html` / portal client: renders authentication, application state, role-specific controls, and user-facing operation results. It does not choose roles or bypass database authorization.
- Supabase browser client/configuration: supplies Auth session management and typed/validated calls. Missing configuration produces a clear setup screen rather than silently reverting to a fake live experience.
- SQL migration under `sql/`: adds required policies, role/profile lookup, authenticated read paths, and narrowly scoped RPCs. Must be safe to apply to the current schema and must preserve Java desktop SQL compatibility.
- Web tests: verify UI outcomes and permission behavior against controlled data; live Supabase credentials and deployed configuration remain human-led integration checks.

## Boundaries and must-follow rules

- Must preserve `AGENT.md` anonymity law: admin code cannot query receipts, and the `submissions` table never gains an author ID.
- Must preserve prepared statements and current Java service/DAO boundaries.
- Must not trust role names supplied by browser state or URL.
- Must not expose service-role credentials, database credentials, OAuth client secrets, or access tokens in client logs/source.
- Must not mark live login complete until Supabase email/password authentication and approved accounts are configured by the project owner.
- Existing seeded demo data must not be truncated or otherwise destructively modified by migrations or tests.

## Failure behavior

- Missing public config: show setup/unavailable state and do not enable the demo role switch.
- Invalid credentials, unverified/non-institutional email, missing user row, or invalid role: deny portal session, clear transient role/data state, and show a clear non-sensitive message.
- Database/network failure: preserve current read-only view where safe, report that the operation did not complete, and do not show false success.
- Permission denial: do not retry with broader privileges; refresh role/session once if stale, then deny.

## Testing strategy

- Add automated feature verification for authenticated role rendering, report persistence, and role-denied operations. Exercise the production client-facing code path, not a duplicate implementation.
- Add browser tests for signed-out gate; mock email/password session boundary; invalid credentials; student/admin role views; direct URL/tab access; form required fields and success/error output; feed/trending/search/category filters; single-vote behavior; own receipt isolation; status/resolution update; CSV export; QR/copy controls; logout and session expiry; desktop/mobile navigation.
- Validate SQL policies/RPCs against actual authenticated JWT claims and two student users plus an admin where local Supabase tooling or a configured test project is available.
- Run `mvn -B clean test` as regression coverage for Java authentication, anonymity, and core services.
- Human live checklist: email/password sign-in with TKMCE student and admin accounts; reject invalid credentials and non-institutional accounts; perform representative student report/upvote/receipt and admin transition/export flows; sign out and verify privileged views disappear.

## Verification checkpoints

| After | Verify | On failure |
|---|---|---|
| SQL migration/permissions | Apply to isolated Supabase schema; confirm role resolution, direct-table denial, and RPC grants for student/admin/outsider | Fix permission or migration before UI integration |
| Auth gate | Browser remains signed out without session; callback yields correct trusted role or explicit denial | Fix callback/session lifecycle before enabling app actions |
| Portal persistence | Student report/upvote/receipt and admin status/history/note writes round-trip | Fix operation boundary; never use localStorage as success fallback |
| Full interaction suite | Browser tests pass at desktop and mobile viewport, covering every visible action | Fix failed action/output before release |
| Regression/live readiness | Maven tests pass; production configuration checklist complete | Report exact remaining owner-supplied setup; do not claim live auth works without it |

## Acceptance criteria

1. The deployed web portal shows a real sign-in gate, and all live application data/actions require an authenticated approved TKMCE user.
2. Students cannot obtain admin access by changing URL, browser storage, DOM, or client state; a genuine ADMIN database role can access admin actions.
3. Invalid domain, unverified email, missing approved profile, expired session, and missing configuration are denied with actionable output and no privileged data.
4. All user-visible portal controls either complete and show accurate results or report a clear failure; none silently updates only local browser state.
5. Database authorization preserves student receipt privacy and author-free public submissions.
6. New automated web feature tests and the full Java Maven test suite pass.
7. Live email/password authentication is marked verified only after owner-supplied Supabase configuration and human use of real student/admin accounts.

## Execution breakdown

1. Inspect current frontend handlers, Supabase client setup/config sources, Java schema assumptions, and available browser-test tooling. (No dependency; orchestrator.)
2. Define/apply additive SQL authorization migration and RPCs, then verify grants/policies. (Depends on 1; orchestrator.)
3. Implement Supabase web config, auth gate/session lifecycle, role lookup, and removal of simulated role switching. (Depends on 1 and 2; orchestrator.)
4. Replace local-only portal reads/mutations with authorized live operations and accurate feedback. (Depends on 2 and 3; orchestrator.)
5. Add automated browser tests for roles, actions, outputs, and denial cases. (Depends on 3 and 4; orchestrator.)
6. Run Java regression checks, web test suite, and browser click-through; document required live Supabase Auth setup and results. (Depends on 2–5; orchestrator.)

## Assumption check

- Assumes user intends the deployed static web/PWA portal, not a redesign of the existing Java desktop login.
- Assumes Supabase is the backend of record and existing `public.users` records are authoritative for approved access and roles.
- Assumes Auth accounts and application profiles are provisioned separately by an administrator; this prevents an otherwise valid institutional identity from entering before it has an explicit role assignment.
- Assumes the project owner can configure Supabase email/password authentication and approved accounts after code is ready; no live secrets are present in the repository.
- Current frontend is a localStorage demo and schema has no browser RLS/API policies, so persistence/security work is part of the requested “live ... and all” scope rather than only a login screen.
