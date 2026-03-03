# API Development TODO List

> **Last Updated:** 2026-02-28
> **Status:** Phases 1-5 COMPLETE. Auth system fully implemented and tested. Testing suite in place (81 tests).

---

## Completed Phases (Summary)

- **Phase 1: Critical Bug Fixes** - 5/5 COMPLETE
- **Phase 2: Extract 60+ Endpoints** - 58/58 COMPLETE
- **Phase 2.5: Migrate Old API to v1** - 11/11 COMPLETE
- **Phase 3: High-Value New Endpoints** - 16/16 COMPLETE
- **Phase 4: Model Serialization** - 27 models COMPLETE
- **API Hardening (5A-5E)** - COMPLETE (null safety, input validation, pagination, error responses, N+1 fixes)
- **Phase 5: Auth & Authorization** - COMPLETE (decorators, 37 scopes, all 137 endpoints protected, audit logging, rate limiting, APP2 bootstrap key)
- **Testing Suite** - 81 tests across 4 test files (auth, models, security API, endpoint coverage)
- **Bug Fix: Double-tuple returns** - Fixed in security.py, gamification.py, notifications.py, reintroduction.py, integrations.py

---

## API Endpoints: **137 Total**

```
routes/api_v1/
├── diary.py           # 9 endpoints
├── recipes.py         # 15 endpoints (incl. meals, search, transform, share)
├── foods.py           # 14 endpoints (incl. compendium, batch, links, boosters)
├── analytics.py       # 27 endpoints
├── usda.py            # 4 endpoints (incl. foods list)
├── ausnut.py          # 2 endpoints
├── settings.py        # 10 endpoints
├── education.py       # 9 endpoints
├── chat.py            # 5 endpoints
├── fodmap.py          # 2 endpoints
├── search.py          # 3 endpoints
├── export.py          # 3 endpoints
├── realtime.py        # 8 endpoints (SSE + webhooks)
├── gamification.py    # 3 endpoints
├── reintroduction.py  # 3 endpoints
├── notifications.py   # 7 endpoints
├── security.py        # 4 endpoints
├── integrations.py    # 3 endpoints
├── billing.py         # 2 endpoints (status + inbound webhook)
└── multi_user.py      # 3 endpoints
```

---

## Remaining TODO Items

### 1. Documentation Gaps
- [ ] Document pagination format in API docs (standard format already implemented)
- [ ] Document error codes in API docs (codes defined in `utils/api_helpers.py`)
- [ ] Verify N+1 query count improvement with testing (eager loading already applied)

### 2. Testing Suite — COMPLETE (81 tests)
Initial suite implemented with `pytest`, `pytest-flask`, `pytest-cov`.

**Current test files:**
```
tests/
├── conftest.py              # Shared fixtures (app, client, API keys)
├── test_auth.py             # Auth decorators, scope validation, rate limiting, audit logging (25 tests)
├── test_models.py           # ApiKey, ApiAccessLog serialization (8 tests)
├── test_security_api.py     # Key CRUD, audit log, rate limit endpoints (15 tests)
└── test_api_endpoints.py    # Endpoint coverage across all route files (33 tests)
├── test_analytics_api.py    # Analytics endpoint tests
└── test_realtime_api.py     # SSE/webhook tests
```

### 3. Old API Deprecation
Add deprecation warnings to legacy `/api/*` endpoints and plan migration.

- [ ] Add deprecation headers to all `/api/*` responses
- [ ] Log deprecation warnings for monitoring
- [ ] Create migration guide document
- [ ] Set sunset date for old API
- [ ] Eventually remove `routes/api.py`

### 4. Recipe URL Import
Enhance `POST /api/v1/recipes/import` to support web scraping from recipe URLs.

- [ ] Parse common recipe schema formats (JSON-LD, microdata)
- [ ] Extract ingredients, instructions, metadata
- [ ] Handle various recipe website formats

**Requirements:** `beautifulsoup4`, `requests`

### 5. Authentication & Authorization — APP2 Readiness Plan

> **Goal**: Implement permission enforcement in APP1 so APP2 can securely consume the API
> from day one. Based on `part_2/ANALYTICS_PERMISSIONS_REPORT.xlsx` (55 endpoints, 3 tiers).
>
> **Current state**: `ApiKey` model exists, keys can be created/listed/revoked, but
> NO validation middleware exists. All 137 API endpoints are completely open.

#### Phase 5A: Auth Decorators (utils/auth.py) — COMPLETE
Two decorators created that enforce authentication and authorization:

- [x] **`require_api_key`** decorator
  - Reads `X-API-Key` header (or `Authorization: Bearer <key>`)
  - Hashes incoming key with SHA-256 and looks up `ApiKey` by `key_hash`
  - Rejects if: key not found, `is_active=False`, `expires_at` has passed
  - Updates `last_used` timestamp on successful validation
  - Stores validated `ApiKey` on `g.api_key` for downstream use
  - Returns 401 UNAUTHORIZED with standard error response on failure
  - **Bypass**: Skip auth for web browser requests (no API key header = web user)

- [x] **`require_scope(scope_string)`** decorator
  - Takes scope like `'read:diary'` or `'write:recipes'`
  - Checks `g.api_key.scopes` (CSV) contains the required scope
  - Returns 403 FORBIDDEN if scope missing
  - Must be used AFTER `require_api_key`

#### Phase 5B: Permission Level Mapping — ALL 136 ENDPOINTS
Apply `@require_api_key` and `@require_scope(...)` to every route in `routes/api_v1/`.
Endpoints marked with (R) = from the xlsx report. Unmarked = gap that needs classifying.

**Summary by permission level:**
| Level | Count | Description |
|-------|-------|-------------|
| HIGH | ~50 | Personal health data, analytics, exports, chat, admin |
| MEDIUM | ~48 | Personal non-health (food/recipe CRUD, gamification, notifications, integrations) |
| LOW | ~35 | Public reference data (FODMAP, USDA, AUSNUT, education, help, search) |
| SPECIAL | 2 | Inbound webhooks (signature-verified, no API key) |

##### diary.py — 9 endpoints → ALL HIGH
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/diary/entries` | GET | READ | `read:diary` | (R) |
| `/diary/day/{date}` | GET | READ | `read:diary` | (R) |
| `/diary/trends` | GET | READ | `read:diary` | (R) |
| `/diary/weekly` | GET | READ | `read:diary` | (R) |
| `/diary/meals` | POST | WRITE | `write:diary` | (R) |
| `/diary/meals/{id}` | PUT | WRITE | `write:diary` | (R) |
| `/diary/entries/bulk` | POST | WRITE | `write:diary` | (R) |
| `/diary/meal-plan` | POST | WRITE | `write:diary` | — |
| `/diary/meal-plan/{id}` | GET | READ | `read:diary` | — |

- [x] Apply decorators to diary.py (9 endpoints)

##### analytics.py — 27 endpoints → ALL HIGH
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/dashboard` | GET | READ | `read:analytics` | (R) |
| `/foods/risk-rating` | POST | READ* | `read:analytics` | (R) |
| `/analytics/symptom-patterns` | GET | READ | `read:analytics` | (R) |
| `/analytics/food-reactions` | GET | READ | `read:analytics` | (R) |
| `/analytics/symptom-trends` | GET | READ | `read:analytics` | (R) |
| `/analytics/food-frequency` | GET | READ | `read:analytics` | (R) |
| `/analytics/trigger-foods` | GET | READ | `read:analytics` | (R) |
| `/analytics/nutrition-summary` | GET | READ | `read:analytics` | (R) |
| `/analytics/fodmap-exposure` | GET | READ | `read:analytics` | (R) |
| `/analytics/histamine-exposure` | GET | READ | `read:analytics` | — |
| `/analytics/fodmap-stacking` | GET | READ | `read:analytics` | — |
| `/analytics/correlations` | GET | READ | `read:analytics` | — |
| `/analytics/gut-stability-score` | GET | READ | `read:analytics` | — |
| `/analytics/tolerance-curves` | GET | READ | `read:analytics` | — |
| `/analytics/nutrient-rdi-status` | GET | READ | `read:analytics` | — |
| `/analytics/nutrient-gaps` | GET | READ | `read:analytics` | — |
| `/analytics/nutrient-heatmap` | GET | READ | `read:analytics` | — |
| `/analytics/nutrient-sources` | GET | READ | `read:analytics` | — |
| `/analytics/nutrient-symptom-correlation` | GET | READ | `read:analytics` | — |
| `/analytics/correlation-matrix` | GET | READ | `read:analytics` | — |
| `/analytics/bristol-trends` | GET | READ | `read:analytics` | — |
| `/analytics/hydration` | GET | READ | `read:analytics` | — |
| `/analytics/meal-timing` | GET | READ | `read:analytics` | — |
| `/analytics/dietary-diversity` | GET | READ | `read:analytics` | — |
| `/analytics/flare-prediction` | GET | READ | `read:analytics` | — |
| `/analytics/gut-health-score` | GET | READ | `read:analytics` | — |
| `/analytics/interactions` | GET | READ | `read:analytics` | — |

- [x] Apply decorators to analytics.py (27 endpoints)

##### recipes.py — 15 endpoints → MIXED LOW/MEDIUM
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/recipes` | GET | LOW | READ | `read:recipes` | (R) |
| `/recipes/search` | GET | LOW | READ | `read:recipes` | — |
| `/recipes/category/{cat}` | GET | LOW | READ | `read:recipes` | — |
| `/recipes/{id}` | GET | LOW | READ | `read:recipes` | (R) |
| `/recipes/{id}/context` | GET | LOW | READ | `read:recipes` | (R) |
| `/recipes` | POST | MEDIUM | WRITE | `write:recipes` | (R) |
| `/recipes/{id}` | PUT | MEDIUM | WRITE | `write:recipes` | (R) |
| `/recipes/{id}` | DELETE | MEDIUM | WRITE | `write:recipes` | (R) |
| `/meals` | GET | MEDIUM | READ | `read:recipes` | — |
| `/meals` | POST | MEDIUM | WRITE | `write:recipes` | — |
| `/meals/{id}` | PUT | MEDIUM | WRITE | `write:recipes` | — |
| `/meals/{id}` | DELETE | MEDIUM | WRITE | `write:recipes` | — |
| `/recipes/import` | POST | MEDIUM | WRITE | `write:recipes` | (R) |
| `/recipes/{id}/transform` | POST | MEDIUM | WRITE | `write:recipes` | — |
| `/recipes/share` | POST | MEDIUM | WRITE | `write:recipes` | — |

- [x] Apply decorators to recipes.py (15 endpoints)

##### foods.py — 14 endpoints → MIXED LOW/MEDIUM/HIGH
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/compendium/search` | GET | LOW | READ | `read:compendium` | (R) |
| `/compendium/foods/{id}` | GET | LOW | READ | `read:compendium` | (R) |
| `/compendium/compare` | GET | LOW | READ | `read:compendium` | (R) |
| `/compendium/foods` | POST | MEDIUM | WRITE | `write:foods` | (R) |
| `/compendium/foods/{id}` | PUT | MEDIUM | WRITE | `write:foods` | (R) |
| `/compendium/foods/{id}` | DELETE | MEDIUM | WRITE | `write:foods` | (R) |
| `/foods/quick-add` | POST | MEDIUM | WRITE | `write:foods` | (R) |
| `/compendium/foods/{id}/link-ausnut` | POST | MEDIUM | WRITE | `write:foods` | — |
| `/foods/batch` | GET | LOW | READ | `read:foods` | — |
| `/foods/substitutes` | GET | MEDIUM | READ | `read:foods` | — |
| `/foods/unified-search` | GET | LOW | READ | `read:foods` | — |
| `/foods/scan-menu` | POST | MEDIUM | WRITE | `write:foods` | — |
| `/compendium/foods/{id}/link-usda` | POST | MEDIUM | WRITE | `write:foods` | — |
| `/foods/nutrient-boosters` | GET | MEDIUM | READ | `read:foods` | — |

- [x] Apply decorators to foods.py (14 endpoints)

##### export.py — 3 endpoints → ALL HIGH
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/export/diary` | GET | READ | `read:export` | (R) |
| `/export/report/pdf` | GET | READ | `read:export` | (R) |
| `/export/shopping-list` | GET | READ | `read:export` | (R) |

- [x] Apply decorators to export.py (3 endpoints)

##### chat.py — 5 endpoints → ALL HIGH
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/chat` | POST | WRITE | `write:chat` | (R) |
| `/chat/conversations` | GET | READ | `read:chat` | (R) |
| `/chat/conversations/{id}` | GET | READ | `read:chat` | (R) |
| `/chat/conversations/{id}` | DELETE | WRITE | `write:chat` | — |
| `/chat/conversations/{id}/rename` | POST | WRITE | `write:chat` | — |

- [x] Apply decorators to chat.py (5 endpoints)

##### realtime.py — 9 endpoints → MIXED HIGH/MEDIUM/SPECIAL
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/events/stream` | GET | HIGH | READ | `stream:realtime` | (R) |
| `/webhooks/register` | POST | MEDIUM | WRITE | `write:webhooks` | (R) |
| `/webhooks` | GET | MEDIUM | READ | `read:webhooks` | — |
| `/webhooks/{id}` | GET | MEDIUM | READ | `read:webhooks` | — |
| `/webhooks/{id}` | PUT | MEDIUM | WRITE | `write:webhooks` | — |
| `/webhooks/{id}` | DELETE | MEDIUM | WRITE | `write:webhooks` | — |
| `/webhooks/{id}/test` | POST | MEDIUM | WRITE | `write:webhooks` | — |
| `/webhooks/external/receive` | POST | SPECIAL | WRITE | *signature-verified* | — |
| `/billing/webhook`* | POST | SPECIAL | WRITE | *signature-verified* | — |

*Note: `/billing/webhook` is in billing.py but listed here for webhook grouping.
SPECIAL endpoints use HMAC signature verification instead of API keys (inbound from external services).

- [x] Apply decorators to realtime.py (7 endpoints + 2 SPECIAL bypass)

##### settings.py — 10 endpoints → MIXED LOW/MEDIUM/HIGH
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/settings/backup` | GET | HIGH | READ | `admin:backup` | (R) |
| `/settings/integrity-check` | GET | MEDIUM | READ | `admin:settings` | (R) |
| `/settings/integrity-check/fix` | POST | MEDIUM | WRITE | `admin:settings` | (R) |
| `/help` | GET | LOW | READ | `read:help` | (R) |
| `/help/{id}` | GET | LOW | READ | `read:help` | (R) |
| `/help/upload` | POST | MEDIUM | WRITE | `write:help` | — |
| `/help` | POST | MEDIUM | WRITE | `write:help` | — |
| `/help/{id}` | PUT | MEDIUM | WRITE | `write:help` | — |
| `/help/{id}` | DELETE | MEDIUM | WRITE | `write:help` | — |
| `/help/preview-markdown` | POST | LOW | READ | `read:help` | — |

- [x] Apply decorators to settings.py (10 endpoints)

##### education.py — 9 endpoints → MIXED LOW/MEDIUM
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/education` | GET | LOW | READ | `read:education` | (R) |
| `/education/{id}` | GET | LOW | READ | `read:education` | (R) |
| `/education/upload` | POST | MEDIUM | WRITE | `write:education` | — |
| `/education` | POST | MEDIUM | WRITE | `write:education` | — |
| `/education/{id}` | PUT | MEDIUM | WRITE | `write:education` | — |
| `/education/{id}` | DELETE | MEDIUM | WRITE | `write:education` | — |
| `/education/reorder` | POST | MEDIUM | WRITE | `write:education` | — |
| `/education/images` | POST | MEDIUM | WRITE | `write:education` | — |
| `/education/preview-markdown` | POST | LOW | READ | `read:education` | — |

- [x] Apply decorators to education.py (9 endpoints)

##### search.py — 3 endpoints → MIXED LOW/MEDIUM
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/search/global` | GET | LOW | READ | `read:search` | (R) |
| `/foods/recommendations` | GET | MEDIUM | READ | `read:foods` | (R) |
| `/recipes/suitable` | GET | MEDIUM | READ | `read:recipes` | (R) |

- [x] Apply decorators to search.py (3 endpoints)

##### usda.py — 4 endpoints → ALL LOW
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/usda/search` | GET | READ | `read:usda` | (R) |
| `/usda/foods` | GET | READ | `read:usda` | — |
| `/usda/foods/{id}` | GET | READ | `read:usda` | (R) |
| `/usda/categories` | GET | READ | `read:usda` | — |

- [x] Apply decorators to usda.py (4 endpoints)

##### ausnut.py — 2 endpoints → ALL LOW
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/ausnut/search` | GET | READ | `read:ausnut` | (R) |
| `/ausnut/foods/{id}` | GET | READ | `read:ausnut` | (R) |

- [x] Apply decorators to ausnut.py (2 endpoints)

##### fodmap.py — 2 endpoints → ALL LOW
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/fodmap/categories` | GET | READ | `read:fodmap` | (R) |
| `/fodmap/foods` | GET | READ | `read:fodmap` | (R) |

- [x] Apply decorators to fodmap.py (2 endpoints)

##### reintroduction.py — 3 endpoints → ALL HIGH
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/reintroduction/protocol` | POST | WRITE | `write:reintroduction` | — |
| `/reintroduction/schedule` | GET | READ | `read:reintroduction` | — |
| `/reintroduction/evaluate` | POST | WRITE | `write:reintroduction` | — |

- [x] Apply decorators to reintroduction.py (3 endpoints)

##### gamification.py — 3 endpoints → ALL MEDIUM
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/gamification/challenges` | GET | READ | `read:gamification` | — |
| `/gamification/challenges` | POST | WRITE | `write:gamification` | — |
| `/gamification/badges` | GET | READ | `read:gamification` | — |

- [x] Apply decorators to gamification.py (3 endpoints)

##### notifications.py — 7 endpoints → ALL MEDIUM
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/notifications/settings` | GET | READ | `read:notifications` | — |
| `/notifications/send` | POST | WRITE | `write:notifications` | — |
| `/notifications/rules` | POST | WRITE | `write:notifications` | — |
| `/notifications/rules` | GET | READ | `read:notifications` | — |
| `/notifications/rules/{id}` | PUT | WRITE | `write:notifications` | — |
| `/notifications/rules/{id}` | DELETE | WRITE | `write:notifications` | — |
| `/notifications/schedule` | POST | WRITE | `write:notifications` | — |

- [x] Apply decorators to notifications.py (7 endpoints)

##### security.py — 5 endpoints → MIXED HIGH/LOW
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/auth/api-keys` | POST | HIGH | WRITE | `admin:security` | — |
| `/auth/api-keys` | GET | HIGH | READ | `admin:security` | — |
| `/auth/api-keys/{id}` | DELETE | HIGH | WRITE | `admin:security` | — |
| `/auth/rate-limit` | GET | LOW | READ | `read:security` | — |
| `/auth/audit-log` | GET | HIGH | READ | `admin:security` | — |

- [x] Apply decorators to security.py (5 endpoints)

##### integrations.py — 3 endpoints → ALL MEDIUM
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/wearables/connect` | POST | WRITE | `write:integrations` | — |
| `/wearables/sync` | POST | WRITE | `write:integrations` | — |
| `/voice/log` | POST | WRITE | `write:integrations` | — |

- [x] Apply decorators to integrations.py (3 endpoints)

##### billing.py — 2 endpoints → MIXED MEDIUM/SPECIAL
| Endpoint | Method | Level | R/W | Scope | Report |
|----------|--------|-------|-----|-------|--------|
| `/billing/status` | GET | MEDIUM | READ | `read:billing` | — |
| `/billing/webhook` | POST | SPECIAL | WRITE | *signature-verified* | — |

- [x] Apply decorators to billing.py (2 endpoints)

##### multi_user.py — 3 endpoints → ALL HIGH
| Endpoint | Method | R/W | Scope | Report |
|----------|--------|-----|-------|--------|
| `/users/cohort-analysis` | GET | READ | `admin:users` | — |
| `/users/compare` | GET | READ | `admin:users` | — |
| `/users/phenotypes` | GET | READ | `admin:users` | — |

- [x] Apply decorators to multi_user.py (3 endpoints)

#### Phase 5B-2: APP2 Build Priority — WHICH ENDPOINTS TO CONSUME FIRST
> **Separate from permission levels.** This maps which endpoints APP2 should call
> first (Primary) vs later (Secondary), based on the "Analytics & Charts" sheet and
> logical dependencies. Permission level = security. Build priority = development order.

##### Primary Endpoints (APP2 needs these from day one)
These power the 20 Primary analytics/visualisations from the report, plus their
data source dependencies.

**Data Sources (must work first — everything else depends on these):**
- [ ] `GET /diary/entries` — core health records (powers almost every analytic)
- [ ] `GET /diary/day/{date}` — daily aggregated view
- [ ] `GET /diary/trends` — symptom trend data
- [ ] `GET /diary/weekly` — weekly summaries
- [ ] `GET /compendium/search` — food lookups
- [ ] `GET /compendium/foods/{id}` — food details
- [ ] `GET /fodmap/categories` — FODMAP reference
- [ ] `GET /fodmap/foods` — FODMAP food data
- [ ] `GET /usda/search` — USDA nutrient lookups
- [ ] `GET /usda/foods/{id}` — USDA food details

**Primary Analytics (20 charts — build these first in APP2):**
| APP2 Chart | Chart Type | Endpoint(s) Consumed |
|------------|-----------|---------------------|
| Daily Nutrient Dashboard | Gauge/Radial | `/analytics/nutrient-rdi-status` |
| Nutrient Gap Analysis | Stacked Bar | `/analytics/nutrient-gaps` |
| Nutrient Trend Lines | Multi-line | `/analytics/nutrition-summary` |
| Macronutrient Balance | Donut/Pie | `/analytics/nutrition-summary` |
| Micronutrient Heatmap | Heatmap Grid | `/analytics/nutrient-heatmap` |
| Nutrient-Food Source Breakdown | Stacked Bar | `/analytics/nutrient-sources` |
| Safe Food Suggestions | Ranked List | `/foods/nutrient-boosters` |
| Symptom Timeline | Timeline | `/analytics/symptom-patterns` |
| Symptom Severity Trend | Line + Zones | `/analytics/symptom-trends` |
| Food-Symptom Correlation | Heatmap | `/analytics/correlation-matrix` |
| FODMAP Exposure Gauge | Gauge | `/analytics/fodmap-exposure` |
| FODMAP Category Radar | Radar/Spider | `/analytics/fodmap-exposure` |
| Trigger Food Ranked List | Bar Chart | `/analytics/trigger-foods` |
| Symptom-Free Streaks | Calendar | `/analytics/symptom-trends` |
| Bristol Stool Tracker | Line + Zone | `/analytics/bristol-trends` |
| Nutrient-Symptom Cross | Scatter | `/analytics/nutrient-symptom-correlation` |
| Hydration Tracker | Progress Bar | `/analytics/hydration` |
| Dietary Diversity Score | Score + Radar | `/analytics/dietary-diversity` |
| AI Weekly Summary | Narrative | `/analytics/*` (multiple) + `/chat` |
| Predictive Flare Risk | Gauge | `/analytics/flare-prediction` |

**Primary Write Endpoints (APP2 needs to push data back):**
- [ ] `POST /diary/meals` — APP2 creates diary entries from meal plans
- [ ] `POST /webhooks/register` — APP2 registers to receive real-time events
- [ ] `GET /events/stream` — APP2 listens for real-time health events

**Primary Reference Endpoints:**
- [ ] `GET /dashboard` — personal watch list + risk overview
- [ ] `GET /export/diary` — full diary export for batch analysis
- [ ] `GET /export/report/pdf` — generated health reports
- [ ] `GET /export/shopping-list` — derived from dietary needs

##### Secondary Endpoints (APP2 builds these later)
These power the 9 Secondary analytics/visualisations, plus supporting features.

**Secondary Analytics (9 charts — build after Primary):**
| APP2 Chart | Chart Type | Endpoint(s) Consumed |
|------------|-----------|---------------------|
| Sleep/Stress x Gut Health | Dual-axis Line | `/analytics/correlations` |
| Meal Timing Analysis | Distribution | `/analytics/meal-timing` |
| Histamine Load Tracker | Gauge + Trend | `/analytics/histamine-exposure` |
| Comparative Period Report | Side-by-side | `/analytics/symptom-trends` + `/analytics/nutrition-summary` |
| Gut Health Composite Score | Composite Gauge | `/analytics/gut-health-score` |
| Energy Balance Tracker | Area Chart | `/analytics/nutrition-summary` |
| Medication Interactions | Alert List | `/analytics/interactions` |
| Elimination Protocol | Phase Tracker | `/reintroduction/*` endpoints |
| Personal Tolerance Map | Traffic Light | `/analytics/tolerance-curves` |

**Secondary Data Endpoints:**
- [ ] `GET /analytics/gut-stability-score` — composite stability metric
- [ ] `GET /analytics/fodmap-stacking` — cumulative FODMAP load
- [ ] `GET /foods/substitutes` — food swap suggestions
- [ ] `GET /foods/recommendations` — personalised food recs
- [ ] `GET /recipes/suitable` — dietary-filtered recipes
- [ ] `GET /chat/conversations` — AI conversation history
- [ ] `GET /chat/conversations/{id}` — individual conversations
- [ ] `GET /reintroduction/schedule` — elimination protocol schedule
- [ ] `GET /gamification/challenges` — user challenges
- [ ] `GET /gamification/badges` — achievement badges

##### Not Needed by APP2 (admin/management only)
These endpoints are for APP1 admin use only — APP2 doesn't consume them:
- `/auth/api-keys` (POST/GET/DELETE) — key management
- `/auth/rate-limit` (GET) — rate limit status
- `/settings/backup` (GET) — database backup
- `/settings/integrity-check` (GET/POST) — DB health
- `/help/*` write endpoints — help content management
- `/education/*` write endpoints — education content management
- `/compendium/foods` write endpoints — food data management
- `/recipes` write endpoints (except diary meal creation)
- `/webhooks/external/receive` — inbound from external services
- `/billing/webhook` — inbound from payment providers
- `/users/*` — multi-user admin endpoints
- `/notifications/*` — notification management
- `/integrations/*` — wearable/voice integration management

#### Phase 5C: Audit Logging — COMPLETE
Track all API access for security review:

- [x] Create `ApiAccessLog` model (key_id, endpoint, method, status_code, timestamp, ip_address)
- [x] Log every authenticated API request in `@require_api_key`
- [x] Add `GET /api/v1/auth/audit-log` endpoint (admin scope) to query access logs

#### Phase 5D: Rate Limiting Enforcement — COMPLETE
Counter-based per-key rate limiting implemented in `@require_api_key`:

- [x] Implement simple counter-based limiting (via ApiAccessLog counts)
- [x] Apply rate limits per API key (not global) — e.g., 60/min for LOW, 120/min for MEDIUM/HIGH
- [x] Return `429 Too Many Requests` with `Retry-After` header when exceeded
- [x] Update `GET /api/v1/auth/rate-limit` to reflect actual enforcement

#### Phase 5E: APP2 Bootstrap Key — COMPLETE
Management script created at `scripts/create_app2_key.py`:

- [x] Create `scripts/create_app2_key.py` — generates key with all needed scopes
- [x] Key scopes for APP2 (Primary features): `read:diary,read:analytics,read:export,read:chat,read:compendium,read:fodmap,read:usda,read:ausnut,read:foods,read:recipes,read:search,read:webhooks,write:diary,write:webhooks,stream:realtime`
- [x] Key scopes for APP2 (Secondary features, add later): `read:gamification,read:reintroduction,read:notifications,read:billing,read:education,read:help`
- [x] Do NOT give APP2: `admin:*` scopes, `write:foods`, `write:recipes`, `write:education`, `write:help`, `admin:security`, `admin:users`
- [x] Print key once, store in APP2's config/environment
- [ ] Document the key exchange process in `api_endpoints.md`

#### Phase 5F: Scope Constants & Validation
Ensure scopes are well-defined and validated. Updated to cover ALL 20 route files:

```
VALID_SCOPES = [
    # ── Read scopes (22) ──────────────────────────────────
    # diary.py
    'read:diary',
    # analytics.py
    'read:analytics',
    # export.py
    'read:export',
    # chat.py
    'read:chat',
    # foods.py + compendium endpoints
    'read:compendium',        # public food lookups
    'read:foods',             # personalised food features
    # recipes.py
    'read:recipes',
    # search.py
    'read:search',
    # fodmap.py
    'read:fodmap',
    # usda.py
    'read:usda',
    # ausnut.py
    'read:ausnut',
    # education.py
    'read:education',
    # settings.py (help)
    'read:help',
    'read:settings',
    # realtime.py (webhooks)
    'read:webhooks',
    # gamification.py
    'read:gamification',
    # reintroduction.py
    'read:reintroduction',
    # notifications.py
    'read:notifications',
    # integrations.py
    'read:integrations',
    # billing.py
    'read:billing',
    # security.py
    'read:security',
    # multi_user.py — no read scope (admin only, uses admin:users)

    # ── Write scopes (13) ─────────────────────────────────
    'write:diary',
    'write:foods',
    'write:recipes',
    'write:chat',
    'write:webhooks',
    'write:help',
    'write:education',
    'write:gamification',
    'write:reintroduction',
    'write:notifications',
    'write:integrations',
    # billing — no write scope (inbound webhook only, signature-verified)
    # search — no write scope (read-only)

    # ── Special scopes (5) ────────────────────────────────
    'stream:realtime',        # SSE event stream
    'admin:backup',           # database backup
    'admin:settings',         # integrity check + fix
    'admin:security',         # API key management
    'admin:users',            # multi-user/cohort endpoints
]
# Total: 40 scopes (22 read + 13 write + 5 special)
```

- [x] Validate scopes on API key creation (reject unknown scopes)
- [x] Update `POST /api/v1/auth/api-keys` to validate against `VALID_SCOPES`

#### Implementation Order
```
5A (decorators) → 5F (40 scope constants) → 5B (apply to all 137 endpoints) → 5B-2 (verify priority map) → 5C (audit) → 5D (rate limit) → 5E (app2 key)
```

#### How APP2 Will Authenticate
```
# APP2 sends this header on every request to APP1:
GET /api/v1/diary/entries?date=2026-03-01
X-API-Key: <64-char-hex-key-from-phase-5E>

# APP1 validates:
1. Hash the key → lookup in api_keys table
2. Check is_active=True, expires_at not passed
3. Check scopes contain 'read:diary'
4. Log access, update last_used
5. Return data (or 401/403)
```

### 6. Rate Limiting
Prevent API abuse using `flask-limiter`. (See Phase 5D above for implementation plan.)

### 7. API Documentation (Swagger/OpenAPI) — ✅ COMPLETE
Auto-generated interactive API documentation using `flasgger`.
- Integrated `flasgger==0.9.7.1` for Swagger UI at `/api/docs`
- Created comprehensive OpenAPI 2.0 spec (`utils/swagger_config.py`) covering all 137 endpoints
- Full spec available at `/api/v1/apispec.json`
- Supports X-API-Key authentication in Swagger UI

### 7.5. API Documentation Strategy — Medium-term Plan (OpenAPI Canonical Spec)
**Goal:** Convert to OpenAPI 3.0 as the single canonical source of truth for all API metadata.

**Why:** Eliminates documentation drift by auto-generating Postman collections, HTML docs, and client SDKs from one source.

**Benefits:**
- [ ] Single source of truth — endpoint metadata defined once
- [ ] Auto-generate Postman collection (no manual sync)
- [ ] Auto-generate HTML/Redoc documentation
- [ ] Enable client SDK generation (Python, JavaScript, Go, etc.)
- [ ] Reduce maintenance burden — update spec, everything updates
- [ ] Machine-readable format for tooling/validation

**Implementation Steps:**
1. Convert existing endpoint specs to OpenAPI 3.0 YAML format (`openapi.yaml`)
   - Document all 137 endpoints with full request/response schemas
   - Include all 40 scopes and permission levels
   - Add examples for common use cases
2. Set up auto-generation pipeline:
   - Use `openapi-generator` to generate Postman collection
   - Use `redoc-cli` or `swagger-ui` to generate HTML docs
   - Optionally generate Python/JS client SDKs
3. Update CI/CD to regenerate docs on every spec change
4. Deprecate manual doc updates — spec is now the source

**Tools:**
- `openapi-generator-cli` — auto-generate Postman, clients, docs
- `redoc` — beautiful auto-generated OpenAPI documentation
- `swagger-ui` — interactive API exploration
- `openapi-spec-validator` — validate spec correctness

**Timeline:** Lower priority (medium-term), implement after current API stabilizes.

### 8. Database Migrations — ✅ COMPLETE
Formal migration system using `Flask-Migrate` + Alembic.
- Initialized Alembic migrations in `migrations/` folder
- Created initial migration `6d82e00ff8d9_initial_schema.py` capturing current schema
- Preserved old scripts in `migrations_legacy/` folder
- Usage: `flask db migrate -m "description"` then `flask db upgrade`
- Database stamped to current migration head

### 9. Monitoring & Logging
Production-grade logging with `sentry-sdk`.

### 10. Caching Layer
Performance improvement with `flask-caching` + Redis.

---

## Priority Recommendations

**High Priority (Production Essentials):**
1. Testing Suite
2. Authentication & Authorization
3. API Documentation
4. Database Migrations

**Medium Priority (Performance & Reliability):**
5. Rate Limiting
6. Monitoring & Logging
7. Caching Layer

**Low Priority (Nice to Have):**
8. Old API Deprecation
9. Recipe URL Import
10. Documentation Gaps

---

## Optional Future Documentation Items

These are useful additions that can be created later based on user feedback:

- [ ] **OpenAPI Schema (YAML)** — Machine-readable OpenAPI 3.0 spec for auto-generating client SDKs (Python, JS, Go, etc.)
- [ ] **Docker API Documentation** — Setup and deployment guide for containerized API deployments
- [ ] **Performance Tuning Guide** — Optimization tips, caching strategies, query optimization examples
- [ ] **Advanced Security Guide** — CORS configuration, SSL/HTTPS setup, rate limit tuning for production
- [ ] **Monitoring & Alerting Setup** — Integration with Sentry/DataDog, tracking API health metrics, error rate alerts

---

## Related Documentation

- **[CLAUDE.md](CLAUDE.md)** - Project guidelines, color scheme, design patterns
- **[Version_History.md](Version_History.md)** - Detailed change history with dates
- **[api_endpoints.md](api_endpoints.md)** - API endpoint reference (136 endpoints)

---

**End of TODO.md**
