const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const path = require('node:path');
const { PGlite } = require('@electric-sql/pglite');

test('portal migration enforces verified roles, persists operations, and isolates receipts', async () => {
  const database = new PGlite();
  const root = path.resolve(__dirname, '..');
  const sql = async (relativePath) => database.exec(await fs.readFile(path.join(root, relativePath), 'utf8'));
  const studentId = 'b7f35d0a-44ef-4a7e-90c2-8d060b0b8601';
  const secondStudentId = 'c8f35d0a-44ef-4a7e-90c2-8d060b0b8602';
  const adminId = 'd9f35d0a-44ef-4a7e-90c2-8d060b0b8603';
  const outsiderId = 'eaf35d0a-44ef-4a7e-90c2-8d060b0b8604';
  const unapprovedStudentId = 'faf35d0a-44ef-4a7e-90c2-8d060b0b8605';

  try {
    await database.exec(`
      CREATE ROLE anon;
      CREATE ROLE authenticated;
      CREATE SCHEMA auth;
      CREATE TABLE auth.users (
        id uuid PRIMARY KEY,
        email text NOT NULL,
        email_confirmed_at timestamptz,
        raw_user_meta_data jsonb NOT NULL DEFAULT '{}'::jsonb
      );
      CREATE FUNCTION auth.uid() RETURNS uuid
      LANGUAGE sql STABLE
      AS $$ SELECT NULLIF(current_setting('request.jwt.claim.sub', true), '')::uuid $$;
      GRANT EXECUTE ON FUNCTION auth.uid() TO PUBLIC;
    `);
    await sql('sql/schema.sql');
    await sql('sql/seed.sql');
    await sql('sql/web_portal.sql');

    await database.query(
      `INSERT INTO auth.users (id, email, email_confirmed_at, raw_user_meta_data)
       VALUES ($1, $2, now(), $3::jsonb), ($4, $5, now(), $6::jsonb),
              ($7, $8, now(), $9::jsonb), ($10, $11, now(), $12::jsonb),
              ($13, $14, now(), $15::jsonb)`,
      [
        studentId, 'student1@tkmce.ac.in', '{"full_name":"Student One"}',
        secondStudentId, 'student2@tkmce.ac.in', '{"name":"Student Two"}',
        adminId, 'admin@tkmce.ac.in', '{"name":"Admin"}',
        outsiderId, 'outsider@gmail.com', '{"name":"Outsider"}',
         unapprovedStudentId, 'new.student@tkmce.ac.in', '{"full_name":"New Student"}'
      ]
    );

    const unapproved = await database.query(
      `SELECT name, email, role FROM public.users WHERE email = 'new.student@tkmce.ac.in'`
    );
    assert.deepEqual(unapproved.rows, []);
    const preservedAdmin = await database.query(
      `SELECT role FROM public.users WHERE email = 'admin@tkmce.ac.in'`
    );
    assert.equal(preservedAdmin.rows[0].role, 'ADMIN');

    const asIdentity = async (identityId, operation) => {
      await database.exec(`SET ROLE authenticated; SELECT set_config('request.jwt.claim.sub', '${identityId}', false);`);
      try {
        return await operation();
      } finally {
        await database.exec('RESET ROLE; SELECT set_config(\'request.jwt.claim.sub\', \'\', false);');
      }
    };

    await asIdentity(unapprovedStudentId, async () => {
      await assert.rejects(
        database.query('SELECT * FROM public.portal_current_profile()'),
        /not approved/
      );
    });

    const newSubmissionId = await asIdentity(studentId, async () => {
      const profile = await database.query('SELECT * FROM public.portal_current_profile()');
      assert.equal(profile.rows[0].role, 'STUDENT');

      const feed = await database.query('SELECT * FROM public.portal_list_submissions()');
      assert.ok(feed.rows.some((row) => row.id === 104));
      assert.equal(Object.hasOwn(feed.rows[0], 'student_id'), false);

      const myReceipts = await database.query('SELECT * FROM public.portal_list_my_submissions()');
      assert.deepEqual(myReceipts.rows.map((row) => row.id).sort((a, b) => a - b), [98, 104]);

      const created = await database.query(
        `SELECT public.portal_create_submission($1, $2, $3, $4, $5, $6) AS id`,
        ['New test ticket', 'A broken light requires repair.', 'ISSUE', 'ELECTRICAL', 'Main Block', 'HIGH']
      );
      const submissionId = created.rows[0].id;
      const toggledOff = await database.query('SELECT public.portal_toggle_hype($1) AS is_hyped', [submissionId]);
      assert.equal(toggledOff.rows[0].is_hyped, false);
      const toggledOn = await database.query('SELECT public.portal_toggle_hype($1) AS is_hyped', [submissionId]);
      assert.equal(toggledOn.rows[0].is_hyped, true);
      await assert.rejects(
        database.query('SELECT * FROM public.submissions'),
        /permission denied/
      );
      await assert.rejects(
        database.query('SELECT public.portal_admin_update_submission($1, $2, $3)', [submissionId, 'RESOLVED', 'No'])
      );
      return submissionId;
    });

    await asIdentity(secondStudentId, async () => {
      const secondReceipts = await database.query('SELECT * FROM public.portal_list_my_submissions()');
      assert.equal(secondReceipts.rows.some((row) => row.id === newSubmissionId), false);
    });

    await asIdentity(adminId, async () => {
      const profile = await database.query('SELECT * FROM public.portal_current_profile()');
      assert.equal(profile.rows[0].role, 'ADMIN');
      await assert.rejects(database.query('SELECT * FROM public.portal_list_my_submissions()'));
      await assert.rejects(
        database.query('SELECT public.portal_create_submission($1, $2, $3, $4, $5, $6)',
          ['Blocked', 'Admins cannot file student reports.', 'ISSUE', 'GENERAL', 'Office', 'LOW'])
      );
      await database.query(
        'SELECT public.portal_admin_update_submission($1, $2, $3)',
        [newSubmissionId, 'RESOLVED', 'Repair completed and verified.']
      );
      const updatedFeed = await database.query('SELECT status, resolution_note FROM public.portal_list_submissions() WHERE id = $1', [newSubmissionId]);
      assert.deepEqual(updatedFeed.rows[0], { status: 'RESOLVED', resolution_note: 'Repair completed and verified.' });
    });

    const history = await database.query('SELECT old_status, new_status FROM public.submission_history WHERE submission_id = $1', [newSubmissionId]);
    assert.deepEqual(history.rows, [{ old_status: 'PENDING', new_status: 'RESOLVED' }]);

    await asIdentity(outsiderId, async () => {
      await assert.rejects(database.query('SELECT * FROM public.portal_current_profile()'));
    });
  } finally {
    await database.close();
  }
});
