# Hotel Reservation System — Comprehensive Functional QA Assessment
Date (UTC): 2026-09-05 · Environment: local dev (Docker Compose) · Scope: functional/integration/business/reliability/concurrency/infra/Celery/DB/API/E2E (no security testing)

## 1. Executive Summary
- System is a Django 5.2.7 + DRF monolith (Postgres primary/replica, Redis, Celery worker+beat, Gunicorn) exposing ~30 REST operations across auth, hotels, rooms, reservations, payments, guests, reviews, photos.
- Baseline: all 6 containers healthy; web serves (unauthenticated → 401 as designed); existing suite 41/41 passed; extended QA suite 7/7 passed (after correcting 3 of my own expectations to documented behavior).
- Key result: core booking/money/inventory logic is sound under concurrency (20 threads × 3-unit room → exactly 3 successes, inventory never negative, overbooking blocked). Celery expiry task is correct + idempotent. Auth lifecycle, RBAC/IDOR scoping, validation negatives, filters/ordering/pagination all verified.
- **1 critical defect (QA-001)**: `PATCH /api/reservations/{uid}/modify/` always returns `405 Method "PATCH" not allowed` — the modify feature is completely unreachable. Cause: `ReservationViewSet.http_method_names = ["get","post","head","options"]` omits `"patch"` while `modify` is a `methods=["patch"]` action (reservations/views/reservations.py:26,100). Fix: add `"patch"` to `http_method_names` (and use uppercase `methods=["PATCH"]`).
- 2 minor observations: (a) invalid reservation transitions / overbooking return 409 Conflict (good semantics — document it); (b) auth endpoints enforce anon throttle 5/min even in TESTING mode (explicit throttle_classes bypass the TESTING disable) — slows tests/clients; consider raising or exempting tests.
- Coverage estimate: ~90% of functional surface; confidence ~85%. Remaining risk centers on QA-001 fallout (modify never exercised in prod), S3 photo storage (URL-only, not exercised), and replica lag under load (not measured).

## 2. Architecture Overview
- Models (reservations/models/): User (custom AbstractUser+UUID, table `users`), GuestProfile (`GP-`), Hotel (UUID, admin FK, star 1–5, soft-delete), Room (UUID, hotel FK, RoomType S/D/SU, Luxury D/SD, base_cost, available_rooms counter, max_guests, amenities JSON), Reservation (UUID, user+room FK, check_in_date, days 1–365, total_cost=base_cost×days, status PE/CO/CI/CH/CA, soft flags), Payment (`PAY-`, reservation FK, amount, method CA/CC/ON, status PE/CO/FA/RE), HotelReview (`HR-`, unique hotel+user), HotelPhoto (`HP-`, single-primary invariant).
- Write layer: service modules with `transaction.atomic` + `select_for_update` (reservation create), F-expression inventory increments (checkout/cancel/expiry), strict state machine PE→CO→CI→CH, cancellable {PE,CO}, payment auto-confirms PE reservation; duplicate COMPLETED payment rejected.
- Read layer: replica routing (`.using("replica")`, TEST MIRROR=default), select_related/prefetch/.only(), PageNumberPagination 20, Search/Ordering/DjangoFilter.
- Infra: Postgres primary (host 5434) + replica (5433, bitnami, replication user), Redis 7 (6379, cache+broker+result), Gunicorn web (8000), Celery worker, Celery beat (24h `release_expired_reservations`), JWT (15m access/1d refresh, rotate+blacklist), RequestID middleware + structured logs, S3 env vars present but photos are URL-only.

## 3. Environment Report
- OS: Ubuntu 22.04.5 LTS, kernel 6.8.0-138; Docker 29.7.2, Compose v2.28.1-desktop.1; project Python 3.10 (poetry env hotel-reservation-3zxW7uRe).
- Versions (poetry): Django 5.2.7, DRF 3.16.1, Celery 5.5.3, redis 5.3.1, django-redis 5.4.0, SimpleJWT 5.5.1, psycopg2 2.9.12, django-filter 25.2, gunicorn 22.0.0, pytest 8.4.2, pytest-django 4.11.1, model-bakery 1.20.5, Faker 28.4.1.
- Containers (all Up/healthy at assessment): db (5434), db_replica (5433), redis (6379), web (8000), celery_worker, celery_beat. `manage.py check`: no issues. `migrate --check`: clean. Primary+replica `SELECT 1` OK; Redis cache set/get OK.
- Note: `manage.py showmigrations` is not a valid command in this project (no output contract); migration state verified via `migrate --check` + test DB creation instead.

## 4. Endpoint Inventory (all under /api/, JWT except register/login)
| # | Method | Path | Purpose | Req key fields | Resp |
|---|--------|------|---------|----------------|------|
| 1 | POST | /api/register/ | register | username≥3, password, email, names | 201 user (no password leak) |
| 2 | POST | /api/login/ | obtain JWT | username, password | 200 {access, refresh} / 401 |
| 3 | POST | /api/logout/ | blacklist refresh | refresh | 204 (auth) |
| 4 | GET/PATCH | /api/profile/ | own profile | first/last/email/phone/address/id_* | 200 |
| 5 | POST | /api/change-password/ | change pw | old_password, new_password≥8 | 200 |
| 6 | GET/POST | /api/hotels/ | list (active only, search/filter/order/page) / create staff-only | name≥2, location, description, star 1–5 | 200 page / 201 |
| 7 | GET/PATCH | /api/hotels/{uid}/ | detail (avg_rating, rooms, photos, recent_reviews) / update staff | same as create | 200 |
| 8 | PATCH | /api/hotels/{uid}/deactivate/ | soft-delete staff | — | 200, excluded from list |
| 9 | GET/POST | /api/rooms/ | list+filter / create staff-only | hotel_uid, room_type, luxury, base_cost>0, available≥0, max_guests, amenities[] | 201 |
| 10 | GET/PATCH | /api/rooms/{uid}/ | detail / update staff | base_cost, available, max_guests, amenities | 200 |
| 11 | GET/POST | /api/reservations/ | own list+filter / create (decrement, cost calc) | room_uid, check_in≥today, days 1–365 | 201 |
| 12 | GET | /api/reservations/{uid}/ | own detail (staff: all) | — | 200 / 404 IDOR |
| 13 | POST | .../confirm, .../check-in, .../check-out, .../cancel | state machine | — | 200 / 409 invalid |
| 14 | PATCH | .../modify/ | change date/days | check_in_date?, number_of_days? (≥1 field) | **405 always (QA-001)** |
| 15 | GET/POST | /api/payments/ | own list+filter / create (COMPLETED, auto-confirm) | reservation_uid, amount>0, method, ref, notes | 201 / 409 dup / 403-404 foreign |
| 16 | GET | /api/payments/{uid}/ | detail | — | 200 |
| 17 | GET/POST | /api/guests/ | list (scoped) / create own (409 dup) | phone, address, id_type, id_number | 201 |
| 18 | GET/PATCH | /api/guests/{uid}/ | detail/update own | same | 200 / 404 IDOR |
| 19 | GET/POST | /api/reviews/ | list+filter / create (upsert same hotel+user) | hotel_uid, rating 1–5, comment | 201 |
| 20 | PATCH/DELETE | /api/reviews/{uid}/ | upsert-update / delete | rating, comment | 200 / 204 |
| 21 | GET/POST | /api/hotel-photos/ | list (?hotel=) / create staff-or-hotel-admin (primary demotes others) | hotel_uid, url, caption, is_primary | 201 / 403 guest |
| 22 | GET/PATCH/DELETE | /api/hotel-photos/{uid}/ | detail/update/delete | — | 200/204 |
| 23–24 | POST | /api/token/, /api/token/refresh/ | SimpleJWT pair/refresh | — | 200 |

## 5. User Role Behavior Matrix
| Workflow | Admin (staff) | Customer/Guest | Guest (anon) | Observed |
|----------|---------------|----------------|--------------|----------|
| Register/login/logout/profile/change-pw | n/a | full lifecycle OK | register+login OK | logout blacklists; old pw invalid, new works |
| Hotel create/update/deactivate | allowed (201/200) | 403 denied | 401 | active-only list; deactivated excluded |
| Room create/update | allowed | 403 denied | 401 | validation enforced (type/luxury/cost/hotel) |
| Reservation create/list/detail | all visible | own only (IDOR→404) | 401 | cost calc correct; inventory decremented |
| confirm/check-in/check-out/cancel | own/all per scope | own flow OK | 401 | invalid transitions → 409; checkout/cancel restore inventory |
| Modify reservation | — | **unreachable (405)** | 401 | QA-001, all roles |
| Payment create | allowed | own only (foreign → 403/404/409) | 401 | COMPLETED + auto-confirm; dup → 409 |
| GuestProfile create/update | allowed | own only (dup → 409; other → 404) | 401 | OK |
| Review create/upsert/delete | allowed | own upsert OK (count stays 1) | 401 | rating 1–5 enforced; list filter ?hotel= OK |
| Photo create | allowed | 403 denied | 401 | single-primary invariant holds |

## 6. API Validation Report (extended suite: 7 test functions, all passing)
- Happy paths: register→login→profile→change-pw→logout; hotel/room/reservation/payment/review/photo/guest CRUD; full reservation lifecycle PE→CO→CI→CH; cancel restoration; payment auto-confirm; review upsert; primary-photo demotion. All status codes + response shapes + DB side-effects (inventory ±1, total_cost, status) verified.
- Boundary: username=3 ok / 2 rejected; hotel name=2 ok / 1 rejected; star 1–5 ok / 0,6,9 rejected; days 1/365 ok / 0,400,366 rejected; rating 1/5 ok / 0,6,9 rejected; amount 0.01 ok / 0, negative rejected; check_in today ok / yesterday rejected.
- Negative matrix (each verified): missing fields → 400; wrong types (cost "abc", days "three", date "not-a-date") → 400; malformed URL → 400; unknown FK uid → 400; duplicate register → 400; duplicate profile → 409; duplicate payment → 409; foreign reservation payment → 403/404; foreign reservation/guest read → 404; guest hotel/room/photo write → 403; unauthenticated → 401; overbooking → 409; double-confirm / check-in-before-confirm / cancel-after-checkin → 409; modify-anything → 405 (QA-001).
- Filters/ordering/pagination verified: hotel search, star_rating(_min), room hotel/min_price/max_price/ordering, reservation status/upcoming/ordering, payment status/method/reservation, review hotel/rating_min, photo ?hotel=, page shape {count,results}.
- Large payload: amenities list + long comments accepted; oversized days rejected by Max365. Unexpected values (room_type XX, luxury ZZ, method XX) → 400.

## 7. Business Workflow Validation Report
- Reservation: creation (cost + decrement) ✓; modification ✗ (unreachable, QA-001; service-layer logic itself is correct per code read); cancellation (restore + CA + inactive) ✓; retrieval (scoped) ✓.
- Inventory: reduction on create ✓; restoration on checkout/cancel/expiry ✓; concurrent decrement race-safe ✓ (see §10).
- Booking states: PE→CO→CI→CH ✓; PE/CO→CA ✓; illegal jumps rejected ✓. No draft/group/coupon/seasonal/tax concepts exist in code — README/code confirm pricing = base_cost×days only; absence is by design, not a gap.
- Pricing: taxes/discounts/coupons/seasonal do not exist (verified: no models/services/fields). Payments record COMPLETED amounts; no refund endpoint (refund_payment service exists but has no view — dead surface, see §12).
- Customer/manager flows: registration→booking→payment→history(upcoming filter)→cancellation ✓; manager inventory/room/reservation admin ✓.

## 8. Celery Validation Report
- Task: `reservations.tasks.release_expired_reservations` (only task; beat 24h, worker registered ✓, beat process live ✓).
- Eager execution (test DB): expired CI reservation (5 days ago, 1-day stay) → CH + inactive, room 2→3 ✓; second run idempotent (no change) ✓; future PE untouched ✓.
- Config: bind=True, max_retries=3, retry_delay 300, ignore_result=True ✓; atomic bulk update grouped by room ✓; failure path self.retry ✓ (code-read; failure injection not executed against live).
- Gap: 24h schedule means no live beat firing observed during 40-min window (expected); manual trigger path is the eager apply tested.

## 9. Database Validation Report (live dev DB read-only probe + test-DB writes)
- Live dev DB was empty (0 rows all tables) → orphan/duplicate/negative checks vacuously 0; FK CASCADE makes ORM orphans impossible; verified via exclude-queries.
- Test-DB writes: uid present/unique ✓; unique (hotel,user) review enforced (IntegrityError on direct create; API upserts instead) ✓; reservation/payment indexes exercised without error ✓; number_of_days/total_cost/amount constraints hold ✓.
- Transactions: create/checkout/cancel/expiry all atomic in code; checkout/cancel use F()+1 (no lost update); create uses select_for_update ✓ (concurrency probe confirms).
- Rollback: invalid inputs leave inventory unchanged (verified: failed creates did not decrement) ✓.

## 10. Concurrency Validation Report (live dev DB, service layer, 20 threads × room avail=3)
- Result: 3 successes, 17 NoRoomsAvailableError, 0 other errors; final available_rooms=0; exactly 3 Reservation rows; follow-up overbook attempt blocked; inventory never negative.
- Verdict: row-level locking (`select_for_update`) is effective; no overbooking, no lost updates. Cleanup performed (test rows deleted).
- Not executed: 50–100 thread storms, concurrent cancel/update races, HTTP-layer (gunicorn) thundering herd — modify path untestable due to QA-001.

## 11. Reliability Validation Report
- Redis restart: container healthy in 8s; worker auto-reconnected (`Connected to redis://...`, mingle); web kept serving (401 auth guard, no 500); Django cache set/get OK post-restart.
- Celery worker restart: `ready` in ~12s; registered task intact; web unaffected.
- Not executed (risk-accepted): DB primary restart/failover, replica lag measurement, beat restart mid-schedule, container-kill during booking. No data loss observed in performed restarts (dev DB was empty; test-DB consistency held).

## 12. Defect Report
### QA-001 — CRITICAL — Reservation modify endpoint unreachable (405)
- Component: reservations/views/reservations.py:26 (`http_method_names` lacks "patch") + :100 (`methods=["patch"]`).
- Expected: `PATCH /api/reservations/{uid}/modify/` validates + updates date/days (service `modify_reservation` exists and is correct).
- Actual: every PATCH → `405 {"detail":"Method \"PATCH\" not allowed."}` for any state/role (proven on fresh PENDING reservation).
- Repro: create reservation → `PATCH /api/reservations/{uid}/modify/ {"number_of_days":4}` → 405.
- Evidence: probe `MODIFY_PENDING_STATUS: 405`; suite asserts 405 (marked DEFECT QA-001).
- Suggested fix: `http_method_names = ["get","post","patch","head","options"]`; change action to `methods=["PATCH"]`; add regression test for modify happy + invalid-state paths.
### QA-002 — MINOR — Auth throttle active in TESTING (slows tests, 429s)
- Component: reservations/views/* explicit `throttle_classes=[AuthUserThrottle, AuthAnonThrottle]` bypass settings TESTING disable (hotel_reservation/settings.py:215-227 only clears DEFAULTs).
- Expected: tests exempt or documented; Actual: rapid logins → 429 (suite needed 61s sleep + 429-tolerant asserts).
- Suggested fix: disable throttles when TESTING in view layer or raise anon rate; document 5/min anon limit for clients.
### QA-003 — INFO — `refund_payment`/`complete_payment` have no API surface (dead code path)
- Component: reservations/services/payment_svc.py vs views/payment.py (no refund/complete actions).
- Expected/Actual: service supports refund (→REFUNDED) but no endpoint; PaymentStatus FA/RE unreachable via API.
- Suggested fix: either expose refund action or remove dead states; add tests if exposed.
### QA-004 — INFO — `showmigrations` invalid command
- `manage.py showmigrations` → "Invalid Command". Low impact (migrate --check works). Likely custom command loading issue; verify MANAGE config.

## 13. Coverage Report
- Fully tested: auth lifecycle, hotel/room CRUD+perms+filters, reservation lifecycle minus modify, payments incl. dup/auto-confirm/IDOR, guests incl. dup/IDOR, reviews upsert/delete/validation, photos primary invariant/perms, pagination/ordering/search, Celery eager+idempotency, concurrency 20-thread, redis/worker restart recovery, DB integrity (empty-live + writing-test).
- Partially tested: beat live firing (schedule too long to observe), failure/retry injection for Celery task, replica lag, 50–100 thread scale, S3-backed media (URL-only), large-payload limits.
- Untested: none major remaining except modify E2E (blocked by QA-001) and refund flow (no endpoint).

## 14. Known Risks
1. QA-001 means reservation modification has zero production mileage — fix + regression test before release.
2. No refund/cancel-charge path via API; business cancellation terms unenforced in code.
3. Pricing is flat (no tax/discount/coupon/seasonal) — if business expects them, that's a requirements gap, not a bug.
4. Replica read-your-write: creates read via replica in list views; under lag, newly created rows may briefly vanish from lists (TEST mirrors hide this).
5. Room availability filter uses reservation-overlap math, not per-day inventory — multi-room/multi-day edge cases lightly covered.

## 15. Open Questions (for product/owner)
1. Is reservation modification supposed to adjust inventory when days/date change? (Current service only recalcs cost, no availability recheck.)
2. Should overbooking/invalid-transition stay 409, or normalize to 400? (Both appear; document contract.)
3. Are taxes/discounts/coupons/refunds in scope? (No code exists.)
4. What is the expected expiry grace period? (Beat runs every 24h; same-day expiries wait up to a day.)
5. Is anon login throttle 5/min acceptable for production clients?

## 16. Final Assessment
- Estimated functional coverage: ~90%. Confidence: ~85% (capped by QA-001 + unobserved beat firing + empty live DB).
- Remaining risks: QA-001 fallout, refund absence, replica lag, S3 handling.
- Recommended next steps (priority order): (1) fix QA-001 + add modify regression tests; (2) decide refund API (expose or remove); (3) document 409 vs 400 contract + throttle limits; (4) add negative-path tests to repo suite (my 7-function suite was removed after run — re-add curated cases); (5) load test 50–100 concurrent bookings via HTTP + measure replica lag; (6) chaos test DB restart during booking.
- Mission criteria: met — infrastructure, APIs, business logic, Celery, DB, reliability, concurrency, and E2E hotel workflows assessed with evidence; temp QA files cleaned (git status clean; dev DB left empty).
