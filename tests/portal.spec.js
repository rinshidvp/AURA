const { test, expect } = require('@playwright/test');

// Stand-in for the Supabase browser SDK: same auth/RPC surface, controlled data.
const fakeSupabaseClient = String.raw`
(() => {
  const role = window.__AURA_TEST_ROLE__ || 'STUDENT';
  const profile = {
    user_id: role === 'ADMIN' ? 5 : 1,
    name: role === 'ADMIN' ? 'Campus Maintenance' : 'Test Student',
    email: role === 'EXTERNAL' ? 'outsider@gmail.com' : (role === 'UNAPPROVED' ? 'unapproved@tkmce.ac.in' : (role === 'ADMIN' ? 'admin@tkmce.ac.in' : 'student1@tkmce.ac.in')),
    role: role === 'UNAPPROVED' ? 'STUDENT' : role
  };
  let listener = null;
  let session = null;
  let nextId = 105;
  const ownIds = new Set([104]);
  const hypedIds = new Set();
  const records = [
    { id: 104, title: 'Lab projector fault', description: 'Projector switches off during lectures.', type: 'ISSUE', category: 'IT_INFRASTRUCTURE', location: 'CSE Lab 3', priority: 'HIGH', status: 'IN_PROGRESS', created_at: new Date().toISOString(), hype_count: 2, is_hyped: false, resolution_note: 'Technician assigned.' },
    { id: 103, title: 'Extend library hours', description: 'Keep the reading room open later.', type: 'SUGGESTION', category: 'ACADEMIC_LABS', location: 'Central Library', priority: 'MEDIUM', status: 'PENDING', created_at: new Date(Date.now() - 86400000).toISOString(), hype_count: 1, is_hyped: false, resolution_note: null }
  ];
  window.__auraExpireSession = () => { session = null; listener?.('SIGNED_OUT', null); };

  const client = {
    auth: {
      onAuthStateChange(callback) { listener = callback; return { data: { subscription: { unsubscribe() {} } } }; },
      async getSession() { return { data: { session }, error: null }; },
      async signInWithPassword() {
        if (role === 'INVALID') return { data: { session: null }, error: { message: 'Invalid login credentials' } };
        session = { access_token: 'test-session-token', user: { email: profile.email } };
        setTimeout(() => listener?.('SIGNED_IN', session), 0);
        return { data: { session }, error: null };
      },
      async signOut() { session = null; listener?.('SIGNED_OUT', null); return { error: null }; }
    },
    async rpc(name, args = {}) {
      if (name === 'portal_current_profile') {
        if (role === 'UNAPPROVED') return { data: null, error: { message: 'This account is not approved for AURA.' } };
        return { data: [profile], error: null };
      }
      if (!session) return { data: null, error: { message: 'Authentication required.' } };
      if (name === 'portal_list_submissions') return { data: records.map(row => ({ ...row, is_hyped: hypedIds.has(row.id) })), error: null };
      if (name === 'portal_list_my_submissions') {
        if (role !== 'STUDENT') return { data: null, error: { message: 'Only students may view private submission receipts.' } };
        return { data: records.filter(row => ownIds.has(row.id)), error: null };
      }
      if (name === 'portal_toggle_hype') {
        if (role !== 'STUDENT') return { data: null, error: { message: 'Only students may upvote campus reports.' } };
        const row = records.find(item => item.id === args.p_submission_id);
        if (hypedIds.has(row.id)) { hypedIds.delete(row.id); row.hype_count--; return { data: false, error: null }; }
        hypedIds.add(row.id); row.hype_count++; return { data: true, error: null };
      }
      if (name === 'portal_create_submission') {
        if (role !== 'STUDENT') return { data: null, error: { message: 'Only students may submit campus reports.' } };
        const id = nextId++;
        const row = { id, title: args.p_title, description: args.p_description, type: args.p_type, category: args.p_category, location: args.p_location, priority: args.p_priority, status: 'PENDING', created_at: new Date().toISOString(), hype_count: 1, is_hyped: true, resolution_note: null };
        records.unshift(row); ownIds.add(id); hypedIds.add(id);
        return { data: id, error: null };
      }
      if (name === 'portal_admin_update_submission') {
        if (role !== 'ADMIN') return { data: null, error: { message: 'Administrator access is required.' } };
        const row = records.find(item => item.id === args.p_submission_id);
        row.status = args.p_status;
        if (args.p_resolution_note) row.resolution_note = args.p_resolution_note;
        return { data: null, error: null };
      }
      return { data: null, error: { message: 'Unknown portal operation.' } };
    }
  };
  window.supabase = { createClient: () => client };
})();
`;

async function useLiveConfig(page) {
  await page.route('**/api/config', route => route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({ supabaseUrl: 'https://example.supabase.co', supabaseAnonKey: 'test-publishable-key' })
  }));
  await page.route('**/@supabase/supabase-js@*/**', route => route.fulfill({
    status: 200,
    contentType: 'application/javascript',
    body: fakeSupabaseClient
  }));
}

test.beforeEach(async ({ page }) => {
  await page.route('https://fonts.googleapis.com/**', route => route.abort());
  await page.route('https://fonts.gstatic.com/**', route => route.abort());
});

function profileEmail(role) {
  return role === 'ADMIN' ? 'admin@tkmce.ac.in' : (role === 'EXTERNAL' ? 'outsider@gmail.com' : (role === 'UNAPPROVED' ? 'unapproved@tkmce.ac.in' : 'student1@tkmce.ac.in'));
}

async function signIn(page, role = 'STUDENT', url = '/#/signin') {
  await useLiveConfig(page);
  await page.addInitScript((testRole) => { window.__AURA_TEST_ROLE__ = testRole; }, role);
  await page.goto(url);
  await expect(page.getByRole('heading', { name: 'Sign in' })).toBeVisible();
  await expect(page.locator('#signin-btn')).toBeEnabled();
  await expect(page.locator('#auth-unavailable')).toBeHidden();
  await page.locator('#auth-email').fill(profileEmail(role));
  await page.locator('#auth-password').fill('password123');
  await page.locator('#signin-btn').click();
}

const card = (page, title) => page.locator('.issue-card', { has: page.getByRole('heading', { name: title }) });

test.describe('live portal (Supabase session)', () => {
  test('student can browse, filter, hype, file a report, see the receipt, and sign out', async ({ page }) => {
    await signIn(page, 'STUDENT', '/?role=admin#/app/admin');
    await expect(page.locator('#view-app')).toBeVisible();
    await expect(page).toHaveURL(/#\/app\/feed$/);
    await expect(page.locator('#role-text')).toHaveText('Student');
    await expect(page.locator('#account-name')).toHaveText('Test Student');
    await expect(page.locator('#dtab-admin')).toBeHidden();
    await expect(page.locator('#btn-export-csv')).toBeHidden();

    // Direct calls and URLs cannot open the admin console for a student.
    await page.evaluate(() => setActiveTab('admin'));
    await expect(page.locator('#toast-message')).toContainText('Administrator access is required');
    await page.evaluate(() => { location.hash = '#/app/admin'; });
    await expect(page).toHaveURL(/#\/app\/feed$/);
    await expect(page.locator('#view-title')).toHaveText('Campus feed');
    await expect(page.locator('#stat-total')).toHaveText('2');

    // Category, search and status filters.
    await page.getByRole('button', { name: /IT infrastructure/ }).click();
    await expect(page.locator('.issue-card')).toHaveCount(1);
    await page.getByRole('button', { name: /All categories/ }).click();
    await page.locator('#search-input').fill('no matching report');
    await expect(page.locator('#empty-state-view')).toBeVisible();
    await expect(page.locator('#empty-state-view')).toContainText('No reports match');
    await page.getByRole('button', { name: 'Clear filters' }).click();
    await expect(page.locator('.issue-card')).toHaveCount(2);
    await page.locator('#status-filter').selectOption('PENDING');
    await expect(page.locator('.issue-card')).toHaveCount(1);
    await expect(page.locator('#result-line')).toHaveText('Showing 1 of 2 reports');
    await page.locator('#status-filter').selectOption('ALL');

    // Trending tab, then back to the feed.
    await page.locator('#dtab-trending').click();
    await expect(page.locator('#view-title')).toHaveText('Trending');
    await page.locator('#dtab-feed').click();
    await expect(page.locator('#view-title')).toHaveText('Campus feed');

    // Accordion details.
    const projector = card(page, 'Lab projector fault');
    await projector.getByRole('heading').click();
    await expect(projector).toHaveClass(/expanded/);
    await expect(projector.locator('.resolution-text')).toHaveText('Technician assigned.');
    await expect(projector.locator('.receipt-pill')).toBeVisible();
    await projector.getByRole('button', { name: /Hide details/ }).click();
    await expect(projector).not.toHaveClass(/expanded/);

    // Hype toggles once per student and persists through the refresh.
    await projector.locator('.hype-btn').click();
    await expect(page.locator('#toast-message')).toContainText('You hyped #104');
    await expect(projector.locator('.hype-count')).toHaveText('3');
    await expect(projector.locator('.hype-btn')).toHaveAttribute('aria-pressed', 'true');
    await projector.locator('.hype-btn').click();
    await expect(page.locator('#toast-message')).toContainText('Hype removed from #104');
    await expect(projector.locator('.hype-count')).toHaveText('2');

    // Report form: close, required validation, then a real submission.
    await page.locator('#btn-header-report').click();
    await expect(page.locator('#report-modal')).toHaveClass(/open/);
    await page.locator('#report-modal .modal-close').click();
    await expect(page.locator('#report-modal')).not.toHaveClass(/open/);
    await page.locator('#btn-header-report').click();
    await page.locator('#report-submit').click();
    await expect(page.locator('#report-modal')).toHaveClass(/open/);
    await expect(page.locator('#report-title')).toHaveJSProperty('validity.valid', false);
    await page.locator('#report-title').fill('New student report');
    await expect(page.locator('#report-title-count')).toHaveText('18/200');
    await page.getByRole('radio', { name: 'Electrical' }).check();
    await page.locator('#report-location').fill('Library ground floor');
    await page.locator('#report-desc').fill('A broken light needs repair.');
    await page.locator('#report-submit').click();
    await expect(page.locator('#toast-message')).toContainText('Report #105 submitted anonymously');
    await expect(page.locator('#report-modal')).not.toHaveClass(/open/);
    await expect(card(page, 'New student report')).toBeVisible();
    await expect(card(page, 'New student report')).toHaveClass(/expanded/);

    await page.locator('#dtab-my').click();
    await expect(page.locator('#view-title')).toHaveText('My reports');
    await expect(card(page, 'New student report')).toBeVisible();
    await expect(page.locator('.issue-card')).toHaveCount(2);

    await page.locator('#signout-btn').click();
    await expect(page.locator('#view-signin')).toBeVisible();
    await expect(page.locator('#view-app')).toBeHidden();
    await expect(page.locator('#auth-message')).toHaveText('You have signed out.');
    await expect(page.locator('#submissions-feed')).toBeEmpty();
  });

  test('administrator triages in the console and exports CSV but cannot use student actions', async ({ page }) => {
    await signIn(page, 'ADMIN');
    await expect(page).toHaveURL(/#\/app\/admin$/);
    await expect(page.locator('#view-title')).toHaveText('Admin console');
    await expect(page.locator('#role-text')).toHaveText('Administrator');
    await expect(page.locator('#dtab-my')).toBeHidden();
    await expect(page.locator('#btn-header-report')).toBeHidden();
    await expect(page.locator('#btn-export-csv')).toBeVisible();
    await expect(page.locator('#stat-pending')).toHaveText('1');

    // Pending reports come first.
    const first = page.locator('.issue-card').first();
    await expect(first.getByRole('heading')).toHaveText('Extend library hours');
    await first.locator('.hype-btn').click();
    await expect(page.locator('#toast-message')).toContainText('Only students can hype');

    await first.getByRole('heading').click();
    await first.getByRole('button', { name: /Update status/ }).click();
    await expect(page.locator('#admin-status-modal')).toHaveClass(/open/);
    await expect(page.locator('#admin-modal-ticket-title')).toHaveText('#103 · Extend library hours');
    await page.locator('#admin-cancel-btn').click();
    await expect(page.locator('#admin-status-modal')).not.toHaveClass(/open/);

    await first.getByRole('button', { name: /Update status/ }).click();
    await page.getByRole('radio', { name: /^Resolved/ }).check();
    await page.locator('#admin-save-btn').click();
    await expect(page.locator('#toast-message')).toContainText('Add a public note');
    await expect(page.locator('#admin-status-modal')).toHaveClass(/open/);
    await page.locator('#admin-resolution-note').fill('Reading room now open until 10 PM during exams.');
    await page.locator('#admin-save-btn').click();
    await expect(page.locator('#toast-message')).toContainText('Ticket #103 moved to Resolved');
    const resolved = card(page, 'Extend library hours');
    await expect(resolved.locator('.status-pill')).toHaveText('Resolved');
    await expect(resolved.locator('.resolution-text')).toHaveText('Reading room now open until 10 PM during exams.');
    await expect(page.locator('#stat-resolved')).toHaveText('1');

    const downloadPromise = page.waitForEvent('download');
    await page.locator('#btn-export-csv').click();
    const download = await downloadPromise;
    expect(download.suggestedFilename()).toMatch(/^AURA_Campus_Audit_\d{4}-\d{2}-\d{2}\.csv$/);

    await page.evaluate(() => setActiveTab('my'));
    await expect(page.locator('#toast-message')).toContainText('Receipts are only kept');
    await page.evaluate(() => openReportModal());
    await expect(page.locator('#toast-message')).toContainText('Only signed-in students');
    await expect(page.locator('#report-modal')).not.toHaveClass(/open/);
  });

  test('unapproved institutional account is rejected without opening the portal', async ({ page }) => {
    await signIn(page, 'UNAPPROVED');
    await expect(page.locator('#auth-message')).toContainText('not approved');
    await expect(page.locator('#view-signin')).toBeVisible();
    await expect(page.locator('#view-app')).toBeHidden();
    await expect(page.locator('#dtab-admin')).toBeHidden();
  });

  test('non-institutional email is rejected before authentication', async ({ page }) => {
    await signIn(page, 'EXTERNAL');
    await expect(page.locator('#auth-message')).toHaveText('Use your @tkmce.ac.in college email address.');
    await expect(page.locator('#view-app')).toBeHidden();
  });

  test('wrong password is rejected and cleared', async ({ page }) => {
    await signIn(page, 'INVALID');
    await expect(page.locator('#auth-message')).toHaveText('Incorrect email or password.');
    await expect(page.locator('#auth-password')).toHaveValue('');
    await expect(page.locator('#view-app')).toBeHidden();
    await expect(page.locator('#submissions-feed')).toBeEmpty();
  });

  test('password visibility toggle', async ({ page }) => {
    await useLiveConfig(page);
    await page.goto('/#/signin');
    await expect(page.locator('#signin-btn')).toBeEnabled();
    await page.locator('#auth-password').fill('secret');
    await page.getByRole('button', { name: 'Show password' }).click();
    await expect(page.locator('#auth-password')).toHaveAttribute('type', 'text');
    await page.getByRole('button', { name: 'Hide password' }).click();
    await expect(page.locator('#auth-password')).toHaveAttribute('type', 'password');
  });

  test('an expired session returns to sign-in and clears portal data', async ({ page }) => {
    await signIn(page, 'STUDENT');
    await expect(page.locator('.issue-card')).toHaveCount(2);
    await page.evaluate(() => window.__auraExpireSession());
    await expect(page.locator('#view-signin')).toBeVisible();
    await expect(page.locator('#auth-message')).toContainText('session ended');
    await expect(page.locator('#submissions-feed')).toBeEmpty();
  });

  test('mobile navigation and phone QR dialog work for a signed-in student', async ({ page, context }) => {
    await context.grantPermissions(['clipboard-read', 'clipboard-write']);
    await page.setViewportSize({ width: 390, height: 844 });
    await signIn(page, 'STUDENT');
    await expect(page.locator('#view-app')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
    await expect(page.locator('#signout-btn')).toBeVisible();
    await expect(page.locator('.app-sidebar')).toBeHidden();
    await page.locator('#mtab-trending').click();
    await expect(page.locator('#view-title')).toHaveText('Trending');
    await page.locator('#mtab-my').click();
    await expect(page.locator('#view-title')).toHaveText('My reports');
    await page.locator('#mtab-report').click();
    await expect(page.locator('#report-modal')).toHaveClass(/open/);
    await page.keyboard.press('Escape');
    await expect(page.locator('#report-modal')).not.toHaveClass(/open/);
    await page.getByRole('button', { name: 'Open on your phone' }).click();
    await expect(page.locator('#qr-modal')).toHaveClass(/open/);
    await expect(page.locator('#current-url-display')).toHaveText('http://127.0.0.1:4173/');
    await page.getByRole('button', { name: 'Copy link' }).click();
    await expect(page.locator('#toast-message')).toContainText('Link copied');
    await page.locator('#qr-modal .modal-close').click();
    await expect(page.locator('#qr-modal')).not.toHaveClass(/open/);
  });
});

test.describe('home page (live sign-in not configured)', () => {
  test('missing configuration keeps sign-in disabled and offers no sample-data fallback', async ({ page }) => {
    await page.goto('/#/signin');
    await expect(page.locator('#auth-unavailable')).toBeVisible();
    await expect(page.locator('#auth-unavailable')).toContainText("isn't available right now");
    await expect(page.locator('#signin-btn')).toBeDisabled();
    await expect(page.locator('#auth-email')).toBeDisabled();
    await expect(page.getByRole('button', { name: /demo/i })).toHaveCount(0);
    await page.evaluate(() => { location.hash = '#/app/feed'; });
    await expect(page.locator('#view-signin')).toBeVisible();
    await expect(page.locator('#submissions-feed')).toBeEmpty();
  });

  test('home page explains AURA and its sections are reachable', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('#view-landing')).toBeVisible();
    await expect(page.getByRole('heading', { level: 1 })).toContainText('Report campus problems.');
    await expect(page.getByRole('heading', { name: /four steps/i })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Anonymous by design, not by promise.' })).toBeAttached();
    await expect(page.getByText(/demo/i)).toHaveCount(0);

    await page.getByRole('navigation', { name: 'Page sections' }).getByRole('link', { name: 'Privacy' }).click();
    await expect(page).toHaveURL(/#privacy$/);
    await expect(page.locator('#privacy')).toBeInViewport();

    const faq = page.locator('.faq details').nth(1);
    await faq.locator('summary').click();
    await expect(faq).toHaveAttribute('open', '');
    await expect(faq.locator('p')).toContainText('@tkmce.ac.in');

    const before = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    await page.locator('#site-nav .theme-toggle').click();
    await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');
    expect(await page.evaluate(() => getComputedStyle(document.body).backgroundColor)).not.toBe(before);

    await page.locator('#site-nav').getByRole('link', { name: 'Sign in' }).click();
    await expect(page.locator('#view-signin')).toBeVisible();
    await page.getByRole('link', { name: 'Home' }).click();
    await expect(page.locator('#view-landing')).toBeVisible();
  });

  test('simplified mobile home keeps actions upfront and extra details collapsed', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 780 });
    await page.goto('/');
    const home = page.locator('#view-landing');
    const ctas = home.locator('.hero-ctas');
    await expect(ctas.getByRole('link', { name: 'Get started' })).toBeInViewport();
    await expect(ctas.getByRole('link', { name: 'How it works' })).toBeInViewport();

    const answers = home.locator('.faq details p');
    for (const answer of await answers.all()) await expect(answer).toBeHidden();
    const privacy = home.locator('.faq details').first();
    await privacy.locator('summary').click();
    await expect(privacy.locator('p')).toBeVisible();
    await expect(privacy.locator('p')).toContainText('stored separately');

    const credits = home.locator('.footer-team');
    await expect(credits.locator('.footer-list')).toBeHidden();
    await credits.getByText('Meet the team').click();
    await expect(credits.locator('.footer-list')).toBeVisible();
    await expect(credits).toContainText('Muhammed Rinshid VP');

    await ctas.getByRole('link', { name: 'How it works' }).click();
    await expect(page.locator('#how')).toBeInViewport();
    await ctas.getByRole('link', { name: 'Get started' }).click();
    await expect(page.locator('#view-signin')).toBeVisible();
  });

  test('the retired demo link opens the home page, not a sample portal', async ({ page }) => {
    await page.goto('/#/demo');
    await expect(page.locator('#view-landing')).toBeVisible();
    await expect(page.locator('.modal-backdrop.open')).toHaveCount(0);
    await expect(page.locator('#view-app')).toBeHidden();
  });

  test('phone layouts have no horizontal scrolling', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 780 });
    await page.goto('/');
    await expect(page.locator('#view-landing')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(360);
    await page.goto('/#/signin');
    await expect(page.locator('#view-signin')).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(360);
    await signIn(page, 'STUDENT', '/?phone=1#/signin');
    await expect(page.locator('.issue-card')).toHaveCount(2);
    expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(360);
  });
});
