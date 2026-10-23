# Live Web Portal Authentication Setup

The hosted AURA portal uses email/password sign-in through Supabase Auth and narrowly scoped Postgres RPCs. The browser receives only the Supabase URL and publishable/anon key. It never receives the database password or service-role key.

## 1. Apply the database setup

For a new database, apply `sql/schema.sql`, then optionally `sql/seed.sql` to a clean demo database, and finally `sql/web_portal.sql` in the Supabase SQL Editor. **Do not run `sql/seed.sql` against a database with real data:** it truncates all AURA tables.

Auth accounts and AURA profiles are provisioned separately by an administrator. A confirmed Auth identity must have a matching `public.users` row before it can enter the portal; existing roles, including `ADMIN`, are preserved and role is never accepted from the browser.

The migration revokes direct browser access to the application tables and grants `authenticated` only the portal RPCs. The privileged JDBC path used by the Java desktop application remains separate. Private student receipts are read only through the student-only receipt RPC; public submissions do not gain an author column.

## 2. Configure Email Auth in Supabase

1. In Supabase, open **Authentication → Providers → Email** and keep email/password sign-in enabled.
2. Keep public sign-up disabled. Create or invite student/admin accounts from Supabase Auth or a protected admin process.
3. Confirm each account’s email and insert a matching `public.users` row with the intended role. Only existing rows may be `ADMIN`.
4. In Supabase **Authentication → URL Configuration**, set the production Site URL to `https://aura-campus-three.vercel.app`. Redirect URLs are not needed for the password flow, but add local/preview URLs if password recovery is later enabled.
5. Apply `sql/web_portal.sql`, then provision each approved Auth account in `public.users` using the protected admin process.

## 3. Configure Vercel runtime variables

In the Vercel project settings, set these variables for Production (and Preview/Development only if those environments are intentionally enabled):

| Variable | Value |
|---|---|
| `SUPABASE_URL` | Supabase project URL, such as `https://<project-ref>.supabase.co` |
| `SUPABASE_ANON_KEY` | Supabase anon/publishable key (safe for browser use) |
| `AURA_ALLOWED_ORIGIN` | Optional exact site origin, e.g. `https://aura-campus-three.vercel.app`; leave unset for Vercel preview origins if needed |

The `/api/config` endpoint returns only the URL and publishable key. **Never configure `SUPABASE_SERVICE_ROLE_KEY` or the database password for this endpoint.** Redeploy after setting variables.

## 4. Home page and sign-in

Visitors land on a public home page (`#/`) that explains AURA, then choose **Sign in** (`#/signin`). There is no demo mode or sample data: every portal screen reads the live database through the RPCs in `sql/web_portal.sql`. While `/api/config` reports that sign-in is not configured, the sign-in page says so and the form stays disabled; once the Vercel variables above are set and the site is redeployed, real sign-in switches on with no code change.

Deployments upload only the files allow-listed in `.vercelignore` (`index.html`, `sw.js`, `manifest.json`, `vercel.json`, `api/`). Keep it that way: any uploaded file is publicly served, and the repository root contains local credentials such as `src/main/resources/db.properties`.

## 5. Human live acceptance test

Use real Supabase Auth email/password accounts with confirmed `@tkmce.ac.in` addresses. Use a pre-approved admin email already present in `public.users` with `role = 'ADMIN'`; an Auth account without a matching profile must be rejected.

### Signed out and denied identities

- Open the deployed portal in a private/incognito window: the sign-in gate appears and the portal cannot be interacted with.
- Change the URL to `?role=admin` or `#admin`, refresh, or edit browser storage: no admin view or application data is granted.
- Try a non-`@tkmce.ac.in` address or invalid password: access is rejected and the session is cleared.
- Sign out: the gate returns and student/admin data is cleared from the page.

### Student account

- Sign in with an approved student email/password account; confirm the Student role badge and absence of admin controls.
- Exercise Feed, Trending, My Receipts, category filters, search, accordion expansion, and mobile tabs.
- Hype/unhype a report, refresh, and confirm the count/state persists; confirm repeated requests do not create duplicate votes.
- Submit a report; verify success feedback, its pending ticket in the feed, and its private receipt in My Receipts after refresh.
- Sign in as another student and verify that the new report is not in that account's My Receipts.
- Try direct navigation to admin and invoke admin-only controls from the browser console: the view/action remains denied by the database.

### Administrator account

- Sign in with an existing approved admin account; confirm Admin Console and CSV export are available, while report submission, upvoting, and My Receipts are unavailable.
- Update a ticket through status transitions and add a resolution note; verify the refreshed ticket, note, and dashboard metrics.
- Export CSV and confirm it contains the live ticket data and no identity/receipt information.
- Try the student receipt RPC as the admin: it must return a permission error and expose no receipt rows.

Also verify QR generation/copy, modal close/cancel, invalid required report fields, network error feedback, password visibility, and invalid credentials. The release should be called live-tested only after these checks are completed with the actual Supabase project and real accounts.
