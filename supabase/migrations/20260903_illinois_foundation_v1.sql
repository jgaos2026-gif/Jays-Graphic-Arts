/*
=====================================================================
 JGA ENTERPRISE OS - BRICK 1 - ILLINOIS FOUNDATION V1
 Repository staging status: PROTOTYPE EVIDENCE / NOT DEPLOYED
 Certification: NOT GRANTED

 Recovered source basis:
 - Illinois-only core records
 - integer cents
 - 35% deposit gate before production
 - 100% payment gate before delivery
 - append-only fork-safe chained audit ledger
 - emergency write lock
 - record locks
 - controlled enums
 - owner/admin RLS; client sees only own records
 - 10+1 treasury scaffold

 SOURCE BOUNDARY:
 The recovered Library copies end at the declaration of the audit-chain
 trigger. Everything after the recovered audit-chain function is an
 engineering completion of the stated requirements, not recovered text.
=====================================================================
*/

create schema if not exists jga;
create extension if not exists pgcrypto;

-- ------------------------------------------------------------------
-- 1. Controlled vocabularies
-- ------------------------------------------------------------------

do $$
begin
  if not exists (
    select 1 from pg_type
    where typname = 'actor_role' and typnamespace = 'jga'::regnamespace
  ) then
    create type jga.actor_role as enum ('owner','admin','contractor','client');
  end if;

  if not exists (
    select 1 from pg_type
    where typname = 'order_status' and typnamespace = 'jga'::regnamespace
  ) then
    create type jga.order_status as enum (
      'draft',
      'intake_submitted',
      'contract_sent',
      'awaiting_deposit',
      'in_production',
      'qc_review',
      'awaiting_final_payment',
      'ready_for_delivery',
      'delivered',
      'archived',
      'cancelled'
    );
  end if;

  if not exists (
    select 1 from pg_type
    where typname = 'payment_status' and typnamespace = 'jga'::regnamespace
  ) then
    create type jga.payment_status as enum ('pending','succeeded','failed','refunded','void');
  end if;

  if not exists (
    select 1 from pg_type
    where typname = 'payment_kind' and typnamespace = 'jga'::regnamespace
  ) then
    create type jga.payment_kind as enum ('deposit','final','other','refund');
  end if;

  if not exists (
    select 1 from pg_type
    where typname = 'treasury_vault' and typnamespace = 'jga'::regnamespace
  ) then
    create type jga.treasury_vault as enum (
      'business_share_01','business_share_02','business_share_03','business_share_04','business_share_05',
      'business_share_06','business_share_07','business_share_08','business_share_09','business_share_10',
      'angel_share_11'
    );
  end if;
end $$;

-- ------------------------------------------------------------------
-- 2. Utility
-- ------------------------------------------------------------------

create or replace function jga.round_to_cents(p_amount numeric)
returns bigint
language sql
immutable
set search_path = pg_catalog, pg_temp
as $$
  select round(p_amount)::bigint;
$$;

-- ------------------------------------------------------------------
-- 3. Emergency lock
-- ------------------------------------------------------------------

create table if not exists jga.system_config (
  id boolean primary key default true check (id = true),
  emergency_lock boolean not null default false,
  updated_at timestamptz not null default now(),
  updated_by uuid references auth.users(id)
);

insert into jga.system_config (id)
values (true)
on conflict (id) do nothing;

create or replace function jga.assert_not_emergency_locked()
returns void
language plpgsql
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
begin
  if coalesce((select emergency_lock from jga.system_config where id = true), false) then
    raise exception 'JGA EMERGENCY LOCK: writes are disabled.';
  end if;
end;
$$;

create or replace function jga.block_writes_when_emergency()
returns trigger
language plpgsql
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
begin
  perform jga.assert_not_emergency_locked();
  if tg_op = 'DELETE' then
    return old;
  end if;
  return new;
end;
$$;

-- ------------------------------------------------------------------
-- 4. Core Illinois-only records
-- ------------------------------------------------------------------

create table if not exists jga.profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  role jga.actor_role not null default 'client',
  state text not null default 'IL' check (state = 'IL'),
  display_name text,
  is_locked boolean not null default false,
  locked_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists jga.clients (
  id uuid primary key default gen_random_uuid(),
  client_user_id uuid references auth.users(id) on delete set null,
  legal_name text not null check (length(trim(legal_name)) > 0),
  email text,
  state text not null default 'IL' check (state = 'IL'),
  is_locked boolean not null default false,
  locked_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists jga.orders (
  id uuid primary key default gen_random_uuid(),
  client_id uuid not null references jga.clients(id) on delete restrict,
  state text not null default 'IL' check (state = 'IL'),
  status jga.order_status not null default 'draft',
  total_cents bigint not null check (total_cents >= 0),
  description text,
  is_locked boolean not null default false,
  locked_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists jga.payments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid not null references jga.orders(id) on delete restrict,
  state text not null default 'IL' check (state = 'IL'),
  kind jga.payment_kind not null,
  status jga.payment_status not null default 'pending',
  amount_cents bigint not null check (amount_cents >= 0),
  external_reference text,
  is_locked boolean not null default false,
  locked_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists jga.treasury_entries (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references jga.orders(id) on delete restrict,
  payment_id uuid references jga.payments(id) on delete restrict,
  state text not null default 'IL' check (state = 'IL'),
  vault jga.treasury_vault not null,
  amount_cents bigint not null check (amount_cents >= 0),
  note text,
  is_locked boolean not null default false,
  locked_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (order_id is not null or payment_id is not null)
);

create index if not exists clients_client_user_id_idx on jga.clients(client_user_id);
create index if not exists orders_client_id_idx on jga.orders(client_id);
create index if not exists orders_status_idx on jga.orders(status);
create index if not exists payments_order_id_idx on jga.payments(order_id);
create index if not exists payments_status_kind_idx on jga.payments(status, kind);
create index if not exists treasury_entries_order_id_idx on jga.treasury_entries(order_id);
create index if not exists treasury_entries_payment_id_idx on jga.treasury_entries(payment_id);

-- ------------------------------------------------------------------
-- 5. Role and access helpers
-- ------------------------------------------------------------------

create or replace function jga.current_role()
returns jga.actor_role
language sql
stable
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
  select coalesce(
    (select role from jga.profiles where user_id = auth.uid()),
    'client'::jga.actor_role
  );
$$;

create or replace function jga.is_owner_or_admin()
returns boolean
language sql
stable
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
  select jga.current_role() in ('owner'::jga.actor_role, 'admin'::jga.actor_role);
$$;

create or replace function jga.can_access_client(p_client_id uuid)
returns boolean
language sql
stable
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
  select exists (
    select 1
    from jga.clients c
    where c.id = p_client_id
      and c.client_user_id = auth.uid()
  );
$$;

create or replace function jga.can_access_order(p_order_id uuid)
returns boolean
language sql
stable
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
  select exists (
    select 1
    from jga.orders o
    join jga.clients c on c.id = o.client_id
    where o.id = p_order_id
      and c.client_user_id = auth.uid()
  );
$$;

-- ------------------------------------------------------------------
-- 6. Record-lock guard
-- ------------------------------------------------------------------

create or replace function jga.lock_guard()
returns trigger
language plpgsql
set search_path = jga, pg_catalog, pg_temp
as $$
begin
  if old.is_locked = true then
    raise exception 'JGA LAW: record is locked.';
  end if;

  if tg_op = 'DELETE' then
    return old;
  end if;

  if new.is_locked = true and old.is_locked = false then
    new.locked_at := coalesce(new.locked_at, now());
  elsif new.is_locked = false then
    new.locked_at := null;
  end if;

  new.updated_at := now();
  return new;
end;
$$;

-- ------------------------------------------------------------------
-- 7. Append-only fork-safe chained audit ledger
-- ------------------------------------------------------------------

create table if not exists jga.audit_ledger (
  id bigserial primary key,
  occurred_at timestamptz not null default now(),
  action_type text not null check (length(trim(action_type)) > 0),
  actor_id uuid references auth.users(id),
  payload jsonb,
  previous_hash text check (previous_hash is null or char_length(previous_hash) = 64),
  current_hash text not null check (char_length(current_hash) = 64)
);

create index if not exists audit_ledger_occurred_at_idx on jga.audit_ledger(occurred_at desc);
create index if not exists audit_ledger_action_type_idx on jga.audit_ledger(action_type);
create index if not exists audit_ledger_actor_id_idx on jga.audit_ledger(actor_id);

create or replace function jga.prevent_tampering()
returns trigger
language plpgsql
set search_path = jga, pg_catalog, pg_temp
as $$
begin
  raise exception 'JGA LAW: Append-only ledger. Updates and Deletes are forbidden.';
end;
$$;

create or replace function jga.audit_ledger_hash_chain()
returns trigger
language plpgsql
set search_path = jga, pg_catalog, pg_temp
as $$
declare
  last_hash text;
  canonical_payload text;
  material text;
begin
  perform pg_advisory_xact_lock(88199101);
  new.occurred_at := coalesce(new.occurred_at, now());

  select al.current_hash
  into last_hash
  from jga.audit_ledger al
  order by al.id desc
  limit 1;

  new.previous_hash := last_hash;
  canonical_payload := coalesce(new.payload, '{}'::jsonb)::text;

  material := concat_ws('|',
    coalesce(new.previous_hash, ''),
    extract(epoch from new.occurred_at)::text,
    new.action_type,
    coalesce(new.actor_id::text, ''),
    canonical_payload
  );

  new.current_hash := encode(digest(material, 'sha256'), 'hex');
  return new;
end;
$$;

drop trigger if exists block_tamper on jga.audit_ledger;
create trigger block_tamper
before update or delete on jga.audit_ledger
for each row execute function jga.prevent_tampering();

drop trigger if exists set_audit_chain_hashes on jga.audit_ledger;
create trigger set_audit_chain_hashes
before insert on jga.audit_ledger
for each row execute function jga.audit_ledger_hash_chain();

-- ------------------------------------------------------------------
-- ENGINEERING COMPLETION BEGINS HERE
-- ------------------------------------------------------------------

create or replace function jga.verify_audit_ledger()
returns table(ok boolean, checked_rows bigint, first_bad_id bigint, reason text)
language plpgsql
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
declare
  r record;
  expected_previous text := null;
  expected_current text;
  material text;
  n bigint := 0;
begin
  for r in
    select id, occurred_at, action_type, actor_id, payload, previous_hash, current_hash
    from jga.audit_ledger
    order by id
  loop
    n := n + 1;

    if r.previous_hash is distinct from expected_previous then
      return query select false, n, r.id, 'previous_hash_mismatch'::text;
      return;
    end if;

    material := concat_ws('|',
      coalesce(r.previous_hash, ''),
      extract(epoch from r.occurred_at)::text,
      r.action_type,
      coalesce(r.actor_id::text, ''),
      coalesce(r.payload, '{}'::jsonb)::text
    );

    expected_current := encode(digest(material, 'sha256'), 'hex');

    if r.current_hash is distinct from expected_current then
      return query select false, n, r.id, 'current_hash_mismatch'::text;
      return;
    end if;

    expected_previous := r.current_hash;
  end loop;

  return query select true, n, null::bigint, null::text;
end;
$$;

create or replace function jga.audit_row_change()
returns trigger
language plpgsql
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
declare
  p jsonb;
begin
  p := jsonb_build_object(
    'schema', tg_table_schema,
    'table', tg_table_name,
    'operation', tg_op,
    'before', case when tg_op in ('UPDATE','DELETE') then to_jsonb(old) else null end,
    'after', case when tg_op in ('INSERT','UPDATE') then to_jsonb(new) else null end
  );

  insert into jga.audit_ledger(action_type, actor_id, payload)
  values (tg_table_name || ':' || tg_op, auth.uid(), p);

  if tg_op = 'DELETE' then
    return old;
  end if;
  return new;
end;
$$;

-- ------------------------------------------------------------------
-- 8. Deposit and delivery gates
-- ------------------------------------------------------------------

create or replace function jga.succeeded_deposit_cents(p_order_id uuid)
returns bigint
language sql
stable
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
  select coalesce(sum(amount_cents), 0)::bigint
  from jga.payments
  where order_id = p_order_id
    and kind = 'deposit'::jga.payment_kind
    and status = 'succeeded'::jga.payment_status;
$$;

create or replace function jga.cleared_net_cents(p_order_id uuid)
returns bigint
language sql
stable
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
  select coalesce(sum(
    case
      when status <> 'succeeded'::jga.payment_status then 0
      when kind = 'refund'::jga.payment_kind then -amount_cents
      else amount_cents
    end
  ), 0)::bigint
  from jga.payments
  where order_id = p_order_id;
$$;

create or replace function jga.enforce_order_payment_gates()
returns trigger
language plpgsql
security definer
set search_path = jga, pg_catalog, pg_temp
as $$
declare
  required_deposit bigint;
  deposit_paid bigint;
  net_paid bigint;
begin
  perform jga.assert_not_emergency_locked();

  if new.status in (
    'in_production'::jga.order_status,
    'qc_review'::jga.order_status,
    'awaiting_final_payment'::jga.order_status,
    'ready_for_delivery'::jga.order_status,
    'delivered'::jga.order_status,
    'archived'::jga.order_status
  ) then
    required_deposit := ceil((new.total_cents::numeric * 35) / 100)::bigint;
    deposit_paid := jga.succeeded_deposit_cents(new.id);

    if deposit_paid < required_deposit then
      raise exception 'JGA DEPOSIT GATE: 35%% cleared deposit required before production. required=% paid=%',
        required_deposit, deposit_paid;
    end if;
  end if;

  if new.status in (
    'ready_for_delivery'::jga.order_status,
    'delivered'::jga.order_status,
    'archived'::jga.order_status
  ) then
    net_paid := jga.cleared_net_cents(new.id);

    if net_paid < new.total_cents then
      raise exception 'JGA DELIVERY GATE: 100%% cleared balance required before delivery. required=% paid=%',
        new.total_cents, net_paid;
    end if;
  end if;

  return new;
end;
$$;

drop trigger if exists orders_payment_gate on jga.orders;
create trigger orders_payment_gate
before insert or update of status, total_cents on jga.orders
for each row execute function jga.enforce_order_payment_gates();

-- ------------------------------------------------------------------
-- 9. Emergency and record-lock triggers
-- ------------------------------------------------------------------

do $$
declare
  t text;
begin
  foreach t in array array['profiles','clients','orders','payments','treasury_entries']
  loop
    execute format('drop trigger if exists %I on jga.%I', 'emergency_lock_guard', t);
    execute format(
      'create trigger %I before insert or update or delete on jga.%I for each row execute function jga.block_writes_when_emergency()',
      'emergency_lock_guard', t
    );
  end loop;

  foreach t in array array['profiles','clients','orders','payments','treasury_entries']
  loop
    execute format('drop trigger if exists %I on jga.%I', 'record_lock_guard', t);
    execute format(
      'create trigger %I before update or delete on jga.%I for each row execute function jga.lock_guard()',
      'record_lock_guard', t
    );
  end loop;
end $$;

-- ------------------------------------------------------------------
-- 10. Audit all consequential Brick 1 changes
-- ------------------------------------------------------------------

do $$
declare
  t text;
begin
  foreach t in array array['system_config','profiles','clients','orders','payments','treasury_entries']
  loop
    execute format('drop trigger if exists %I on jga.%I', 'append_audit_event', t);
    execute format(
      'create trigger %I after insert or update or delete on jga.%I for each row execute function jga.audit_row_change()',
      'append_audit_event', t
    );
  end loop;
end $$;

-- ------------------------------------------------------------------
-- 11. RLS: owner/admin full; client read-only to own records
--     contractors have no business-table policy in V1.
-- ------------------------------------------------------------------

alter table jga.system_config enable row level security;
alter table jga.profiles enable row level security;
alter table jga.clients enable row level security;
alter table jga.orders enable row level security;
alter table jga.payments enable row level security;
alter table jga.treasury_entries enable row level security;
alter table jga.audit_ledger enable row level security;

grant usage on schema jga to authenticated;

grant select, insert, update, delete on jga.profiles to authenticated;
grant select, insert, update, delete on jga.clients to authenticated;
grant select, insert, update, delete on jga.orders to authenticated;
grant select, insert, update, delete on jga.payments to authenticated;
grant select, insert, update, delete on jga.treasury_entries to authenticated;
grant select, update on jga.system_config to authenticated;
grant select on jga.audit_ledger to authenticated;

revoke insert, update, delete on jga.audit_ledger from authenticated;
revoke all on all sequences in schema jga from authenticated;

revoke all on function jga.assert_not_emergency_locked() from public;
revoke all on function jga.block_writes_when_emergency() from public;
revoke all on function jga.current_role() from public;
revoke all on function jga.is_owner_or_admin() from public;
revoke all on function jga.can_access_client(uuid) from public;
revoke all on function jga.can_access_order(uuid) from public;
revoke all on function jga.audit_row_change() from public;
revoke all on function jga.verify_audit_ledger() from public;
revoke all on function jga.succeeded_deposit_cents(uuid) from public;
revoke all on function jga.cleared_net_cents(uuid) from public;
revoke all on function jga.enforce_order_payment_gates() from public;

grant execute on function jga.current_role() to authenticated;
grant execute on function jga.is_owner_or_admin() to authenticated;
grant execute on function jga.can_access_client(uuid) to authenticated;
grant execute on function jga.can_access_order(uuid) to authenticated;
grant execute on function jga.verify_audit_ledger() to authenticated;

drop policy if exists system_config_owner_admin_select on jga.system_config;
create policy system_config_owner_admin_select on jga.system_config
for select to authenticated
using (jga.is_owner_or_admin());

drop policy if exists system_config_owner_admin_update on jga.system_config;
create policy system_config_owner_admin_update on jga.system_config
for update to authenticated
using (jga.is_owner_or_admin())
with check (jga.is_owner_or_admin());

drop policy if exists profiles_owner_admin_all on jga.profiles;
create policy profiles_owner_admin_all on jga.profiles
for all to authenticated
using (jga.is_owner_or_admin())
with check (jga.is_owner_or_admin());

drop policy if exists profiles_self_read on jga.profiles;
create policy profiles_self_read on jga.profiles
for select to authenticated
using (user_id = auth.uid());

drop policy if exists clients_owner_admin_all on jga.clients;
create policy clients_owner_admin_all on jga.clients
for all to authenticated
using (jga.is_owner_or_admin())
with check (jga.is_owner_or_admin());

drop policy if exists clients_self_read on jga.clients;
create policy clients_self_read on jga.clients
for select to authenticated
using (client_user_id = auth.uid());

drop policy if exists orders_owner_admin_all on jga.orders;
create policy orders_owner_admin_all on jga.orders
for all to authenticated
using (jga.is_owner_or_admin())
with check (jga.is_owner_or_admin());

drop policy if exists orders_client_read on jga.orders;
create policy orders_client_read on jga.orders
for select to authenticated
using (jga.can_access_client(client_id));

drop policy if exists payments_owner_admin_all on jga.payments;
create policy payments_owner_admin_all on jga.payments
for all to authenticated
using (jga.is_owner_or_admin())
with check (jga.is_owner_or_admin());

drop policy if exists payments_client_read on jga.payments;
create policy payments_client_read on jga.payments
for select to authenticated
using (jga.can_access_order(order_id));

drop policy if exists treasury_owner_admin_all on jga.treasury_entries;
create policy treasury_owner_admin_all on jga.treasury_entries
for all to authenticated
using (jga.is_owner_or_admin())
with check (jga.is_owner_or_admin());

drop policy if exists audit_owner_admin_read on jga.audit_ledger;
create policy audit_owner_admin_read on jga.audit_ledger
for select to authenticated
using (jga.is_owner_or_admin());

comment on schema jga is 'JGA Brick 1 Illinois Foundation V1 - staged, not certified';
comment on table jga.audit_ledger is 'Append-only fork-safe chained audit evidence ledger';
comment on table jga.treasury_entries is '10+1 treasury allocation scaffold; allocation policy is not automated in V1';
