# AURA Final Evaluation: Speaker Run-Sheet

Deck: [`index.html`](index.html) (open in Chrome, press `F` for fullscreen), also online at https://aura-campus-three.vercel.app/final-presentation. PDF backup: [`../AURA_Final_Evaluation.pdf`](../AURA_Final_Evaluation.pdf).
Keys: `→`/`Space` next · `←` back · `G` jump to any slide · `S` speaker notes · click ⏱ to start the 20-minute countdown. Every slide's word-for-word notes are in the `S` drawer.

## Running order (≈20 min)

| # | Slide | Speaker | Rubric | Time |
|---|---|---|---|---|
| 1 | Title | Rinshid | — | 0:30 |
| 2 | Problem recap | Rinshid | — | 0:45 |
| 3 | Two front doors, one DB | Rinshid | PO3 | 1:00 |
| 4 | Five modules, one pipeline | Rinshid | PO3 | 0:40 |
| 5 | Anonymity vault | Nafih | PO3, PO7 | 1:00 |
| 6 | **Live demo** | Rinshid drives, owners narrate | PO3 | 3:00 |
| 7–11 | Individual contributions | Rinshid, Nirmal, Nafih, Rahandeep, Athil | PO3, PO8 | 5 × 1:00 |
| 12 | 41 automated tests | Athil | PO3, PO5 | 0:45 |
| 13 | Tools per phase | Rahandeep | PO5 | 0:50 |
| 14 | Impact on society | Nirmal | PO6 | 1:00 |
| 15 | Ethics & inclusivity | Nafih | PO7 | 1:00 |
| 16 | Team structure | Athil | PO8 | 0:45 |
| 17 | Plan vs actual | Athil | PO10 | 0:45 |
| 18 | Cost specification | Rinshid | PO10 | 0:45 |
| 19 | Self-learning | Rahandeep | PO11 | 0:50 |
| 20 | Limitations & future | Nirmal | — | 0:40 |
| 21 | Conclusion & Q&A | Rinshid | — | 0:30 |

PO9 (presentation) is scored on delivery: face the evaluators, not the screen; one sentence per card, not every word on it.

## Before you walk in

- [ ] **Restore the Supabase project first.** On 17 Oct 2026 the database was not reachable (the project address did not resolve), which is what happens when a free project pauses after about a week idle. Sign in at supabase.com, open the project and choose *Restore*. Do it the day before, then open the desktop app on the morning of the evaluation so it doesn't pause again.
- [ ] Confirm the hours on slide 18 (5 × 10 weeks × ~8 h) match what the team actually spent, and re-check Supabase Pro / Vercel Pro prices on their pricing pages.
- [ ] Desktop app: `run-admin.bat` signs in against the live Supabase DB (needs `src/main/resources/db.properties`).
- [ ] Phone: open https://aura-campus-three.vercel.app and sign in with a provisioned student account. The portal has no demo mode, so live sign-in must be configured (Vercel variables, `sql/web_portal.sql`, accounts; see `docs/WEB_PORTAL_AUTH.md`).
- [ ] One test report title ready to type (e.g. "Projector flickering in CSE Seminar Hall").
- [ ] Second student account (or second phone) for the upvote step.
- [ ] Screen recording of the full slide 6 run, made the day before, as the fallback if the database is unreachable.
- [ ] PDF copy on a USB stick.

## Likely viva questions

| Question | Who | Short answer |
|---|---|---|
| Can the admin find out who filed a report? | Nafih | No. `submissions` has no author column; only the student's own receipt links them, and the receipt RPC rejects ADMIN sessions. Tested three ways (slide 5). |
| What stops a student voting twice? | Nirmal | `UNIQUE (submission_id, student_id)` in Postgres. A Java check alone could race; the database constraint cannot. |
| What if the receipt insert fails after the report is saved? | Rahandeep | The three inserts (submission, receipt, history) run in one JDBC transaction and roll back together. The web RPC is atomic for the same reason. |
| How do you prevent SQL injection? | Rahandeep | Every query is a `PreparedStatement`; user text is bound as a parameter, never concatenated. |
| Why did you drop Google OAuth? | Nafih | A desktop JAR is distributed to users, so any client secret inside it is public. Email/password with BCrypt (desktop) and Supabase Auth (web) avoids shipping a secret. |
| Why does the login give the same error for wrong email and wrong password? | Nafih | So nobody can use the form to find out which emails are registered (user enumeration). Covered by `AuthServiceTest`. |
| Does the browser have the database password? | Rinshid | No. It gets only the public anon key, which can call just six RPCs; each re-checks identity, domain and role. Direct table access is revoked. |
| Why are 8 Java tests skipped? | Athil | They need the live Supabase database. They skip when it isn't reachable and run in CI where credentials are provided as secrets. The 16 offline tests always run. |
| How would you measure social impact? | Nirmal | Median PENDING → RESOLVED time from `submission_history`, resolution rate per category, repeat reports per location. Not measured yet: AURA has not been rolled out. |
| What does it cost to run? | Rinshid | ₹0 to build on free tiers; about ₹4,300/month (US$45 at ₹95) on paid tiers campus-wide, or ₹0 licence cost self-hosted. |
| Why pay at all if the free tier works? | Rinshid | A free Supabase project pauses itself after about a week without activity and has no daily backups. A campus service can't go offline because nobody filed a report that week. |
| How do you know the status colours are readable? | Rahandeep | `StatusColorContrastTest` computes the WCAG contrast ratio of every badge; all are at least 4.5:1 (AA). |
