-- AURA browser portal security and live operations.
-- Apply after schema.sql and seed.sql. Does not delete or rewrite existing data.
BEGIN;

-- Only RPCs below are exposed to the browser. Direct table access is denied,
-- while the Java application continues using its privileged JDBC connection.
REVOKE ALL ON TABLE
    public.users,
    public.submissions,
    public.student_submission_receipts,
    public.submission_hype,
    public.resolution_notes,
    public.submission_history
FROM PUBLIC, anon, authenticated;

REVOKE ALL ON SEQUENCE
    public.users_user_id_seq,
    public.submissions_submission_id_seq,
    public.student_submission_receipts_receipt_id_seq,
    public.submission_hype_hype_id_seq,
    public.resolution_notes_note_id_seq,
    public.submission_history_history_id_seq
FROM PUBLIC, anon, authenticated;

-- Auth accounts and application profiles are provisioned separately by an admin.
-- This prevents any confirmed institutional Auth account from gaining portal access
-- before it has an explicit public.users role assignment.

-- Private identity resolver used by the portal RPCs; never granted directly
-- to anon/authenticated clients.
CREATE OR REPLACE FUNCTION public.portal_request_user_id()
RETURNS integer
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    identity_email text;
    resolved_user_id integer;
BEGIN
    SELECT lower(u.email)
      INTO identity_email
      FROM auth.users AS u
     WHERE u.id = auth.uid()
       AND u.email_confirmed_at IS NOT NULL;

    IF identity_email IS NULL OR identity_email !~ '^[^@]+@tkmce\.ac\.in$' THEN
        RAISE EXCEPTION 'Institutional account verification required.' USING ERRCODE = '42501';
    END IF;

    SELECT u.user_id
      INTO resolved_user_id
      FROM public.users AS u
     WHERE lower(u.email) = identity_email
       AND u.role IN ('STUDENT', 'ADMIN');

    IF resolved_user_id IS NULL THEN
        RAISE EXCEPTION 'This account is not approved for AURA.' USING ERRCODE = '42501';
    END IF;

    RETURN resolved_user_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.portal_request_role()
RETURNS text
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $$
    SELECT u.role
      FROM public.users AS u
     WHERE u.user_id = public.portal_request_user_id()
$$;

CREATE OR REPLACE FUNCTION public.portal_current_profile()
RETURNS TABLE (user_id integer, name text, email text, role text)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
    RETURN QUERY
    SELECT u.user_id, u.name::text, u.email::text, u.role::text
      FROM public.users AS u
     WHERE u.user_id = public.portal_request_user_id();
END;
$$;

CREATE OR REPLACE FUNCTION public.portal_list_submissions()
RETURNS TABLE (
    id integer,
    title text,
    description text,
    type text,
    category text,
    location text,
    priority text,
    status text,
    created_at timestamptz,
    hype_count bigint,
    is_hyped boolean,
    resolution_note text
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    viewer_id integer;
    viewer_role text;
BEGIN
    viewer_id := public.portal_request_user_id();
    viewer_role := public.portal_request_role();
    IF viewer_role NOT IN ('STUDENT', 'ADMIN') THEN
        RAISE EXCEPTION 'Portal access denied.' USING ERRCODE = '42501';
    END IF;

    RETURN QUERY
    SELECT s.submission_id,
           s.title::text,
           s.description::text,
           s.type::text,
           s.category::text,
           s.location::text,
           s.priority::text,
           s.status::text,
           s.created_at,
           (SELECT count(*) FROM public.submission_hype AS h WHERE h.submission_id = s.submission_id),
           EXISTS (
               SELECT 1 FROM public.submission_hype AS h
                WHERE h.submission_id = s.submission_id AND h.student_id = viewer_id
           ),
           (SELECT n.note::text FROM public.resolution_notes AS n
             WHERE n.submission_id = s.submission_id
             ORDER BY n.created_at DESC, n.note_id DESC LIMIT 1)
      FROM public.submissions AS s
     ORDER BY s.created_at DESC, s.submission_id DESC;
END;
$$;

CREATE OR REPLACE FUNCTION public.portal_list_my_submissions()
RETURNS TABLE (
    id integer,
    title text,
    description text,
    type text,
    category text,
    location text,
    priority text,
    status text,
    created_at timestamptz,
    hype_count bigint,
    is_hyped boolean,
    resolution_note text
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    viewer_id integer;
BEGIN
    viewer_id := public.portal_request_user_id();
    IF public.portal_request_role() <> 'STUDENT' THEN
        RAISE EXCEPTION 'Only students may view private submission receipts.' USING ERRCODE = '42501';
    END IF;

    -- This student-only routine is the sole web path into the anonymity vault.
    RETURN QUERY
    SELECT s.submission_id,
           s.title::text,
           s.description::text,
           s.type::text,
           s.category::text,
           s.location::text,
           s.priority::text,
           s.status::text,
           s.created_at,
           (SELECT count(*) FROM public.submission_hype AS h WHERE h.submission_id = s.submission_id),
           EXISTS (
               SELECT 1 FROM public.submission_hype AS h
                WHERE h.submission_id = s.submission_id AND h.student_id = viewer_id
           ),
           (SELECT n.note::text FROM public.resolution_notes AS n
             WHERE n.submission_id = s.submission_id
             ORDER BY n.created_at DESC, n.note_id DESC LIMIT 1)
      FROM public.student_submission_receipts AS r
      JOIN public.submissions AS s ON s.submission_id = r.submission_id
     WHERE r.student_id = viewer_id
     ORDER BY r.created_at DESC, s.submission_id DESC;
END;
$$;

CREATE OR REPLACE FUNCTION public.portal_create_submission(
    p_title text,
    p_description text,
    p_type text,
    p_category text,
    p_location text,
    p_priority text
)
RETURNS integer
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    viewer_id integer;
    new_submission_id integer;
BEGIN
    viewer_id := public.portal_request_user_id();
    IF public.portal_request_role() <> 'STUDENT' THEN
        RAISE EXCEPTION 'Only students may submit campus reports.' USING ERRCODE = '42501';
    END IF;

    IF length(trim(COALESCE(p_title, ''))) NOT BETWEEN 1 AND 200
       OR length(trim(COALESCE(p_description, ''))) = 0
       OR length(trim(COALESCE(p_location, ''))) NOT BETWEEN 1 AND 150
       OR p_type IS NULL OR p_type NOT IN ('ISSUE', 'SUGGESTION')
       OR p_category IS NULL OR p_category NOT IN ('IT_INFRASTRUCTURE', 'ELECTRICAL', 'CIVIL_MAINTENANCE', 'ACADEMIC_LABS', 'HOSTEL_MESS', 'GENERAL')
       OR p_priority IS NULL OR p_priority NOT IN ('LOW', 'MEDIUM', 'HIGH') THEN
        RAISE EXCEPTION 'Report fields are invalid.' USING ERRCODE = '22023';
    END IF;

    INSERT INTO public.submissions (title, description, type, category, location, priority, status)
    VALUES (trim(p_title), trim(p_description), p_type, p_category, trim(p_location), p_priority, 'PENDING')
    RETURNING submission_id INTO new_submission_id;

    INSERT INTO public.student_submission_receipts (student_id, submission_id)
    VALUES (viewer_id, new_submission_id);

    INSERT INTO public.submission_hype (submission_id, student_id)
    VALUES (new_submission_id, viewer_id);

    RETURN new_submission_id;
END;
$$;

CREATE OR REPLACE FUNCTION public.portal_toggle_hype(p_submission_id integer)
RETURNS boolean
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    viewer_id integer;
BEGIN
    viewer_id := public.portal_request_user_id();
    IF public.portal_request_role() <> 'STUDENT' THEN
        RAISE EXCEPTION 'Only students may upvote campus reports.' USING ERRCODE = '42501';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM public.submissions WHERE submission_id = p_submission_id) THEN
        RAISE EXCEPTION 'Campus report not found.' USING ERRCODE = 'P0002';
    END IF;

    DELETE FROM public.submission_hype
     WHERE submission_id = p_submission_id AND student_id = viewer_id;
    IF FOUND THEN
        RETURN false;
    END IF;

    INSERT INTO public.submission_hype (submission_id, student_id)
    VALUES (p_submission_id, viewer_id)
    ON CONFLICT (submission_id, student_id) DO NOTHING;
    RETURN true;
END;
$$;

CREATE OR REPLACE FUNCTION public.portal_admin_update_submission(
    p_submission_id integer,
    p_status text,
    p_resolution_note text
)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
DECLARE
    admin_id integer;
    previous_status text;
BEGIN
    admin_id := public.portal_request_user_id();
    IF public.portal_request_role() <> 'ADMIN' THEN
        RAISE EXCEPTION 'Administrator access is required.' USING ERRCODE = '42501';
    END IF;
    IF p_status IS NULL OR p_status NOT IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'RESOLVED', 'REJECTED') THEN
        RAISE EXCEPTION 'Ticket status is invalid.' USING ERRCODE = '22023';
    END IF;

    SELECT status INTO previous_status
      FROM public.submissions
     WHERE submission_id = p_submission_id
     FOR UPDATE;
    IF previous_status IS NULL THEN
        RAISE EXCEPTION 'Campus report not found.' USING ERRCODE = 'P0002';
    END IF;

    UPDATE public.submissions SET status = p_status WHERE submission_id = p_submission_id;
    IF previous_status <> p_status THEN
        INSERT INTO public.submission_history (submission_id, old_status, new_status, changed_by)
        VALUES (p_submission_id, previous_status, p_status, admin_id);
    END IF;

    IF length(trim(COALESCE(p_resolution_note, ''))) > 0 THEN
        INSERT INTO public.resolution_notes (submission_id, admin_id, note)
        VALUES (p_submission_id, admin_id, trim(p_resolution_note));
    END IF;
END;
$$;

-- Helper functions are callable only from functions owned by the database owner.
REVOKE ALL ON FUNCTION public.portal_request_user_id() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.portal_request_role() FROM PUBLIC, anon, authenticated;

REVOKE ALL ON FUNCTION public.portal_current_profile() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.portal_list_submissions() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.portal_list_my_submissions() FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.portal_create_submission(text, text, text, text, text, text) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.portal_toggle_hype(integer) FROM PUBLIC, anon, authenticated;
REVOKE ALL ON FUNCTION public.portal_admin_update_submission(integer, text, text) FROM PUBLIC, anon, authenticated;

GRANT EXECUTE ON FUNCTION public.portal_current_profile() TO authenticated;
GRANT EXECUTE ON FUNCTION public.portal_list_submissions() TO authenticated;
GRANT EXECUTE ON FUNCTION public.portal_list_my_submissions() TO authenticated;
GRANT EXECUTE ON FUNCTION public.portal_create_submission(text, text, text, text, text, text) TO authenticated;
GRANT EXECUTE ON FUNCTION public.portal_toggle_hype(integer) TO authenticated;
GRANT EXECUTE ON FUNCTION public.portal_admin_update_submission(integer, text, text) TO authenticated;

COMMIT;
