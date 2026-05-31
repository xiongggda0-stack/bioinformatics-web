# Unified Search Center Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the temporary frontend search aggregation with a backend `/api/search` service, migrate database resources and tutorials into PostgreSQL, and add a complete `/search` results page.

**Architecture:** Keep the existing FastAPI Controller-Service-Repository pattern. Add PostgreSQL-backed database resource and tutorial modules, then add a search module that queries all five resource types and applies explicit field weights. On the frontend, keep the header preview but route all searches through `/api/search`; use server-rendered pages for database navigation, tutorial details, and complete search results.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, PostgreSQL 15, pytest, httpx, Next.js App Router, React, TypeScript, TailwindCSS, Docker Compose.

---

## Environment Baseline

Use Docker for implementation. Local Python, Node.js, npm, PostgreSQL, and `psql` installations are not required.

Verified container runtime versions:

```text
Backend Python: 3.12.13
Frontend Node.js: 20.20.2
Frontend npm: 10.8.2
PostgreSQL: 15.18
Docker Compose standalone: v5.1.3
```

In the current Codex terminal, prefer:

```powershell
docker-compose ...
```

The installed `docker-compose` standalone command works. The `docker compose` plugin lookup currently fails in this terminal because access to `C:\Users\yhpeng\.docker\config.json` is restricted. This does not block implementation.

Before execution, initialize Git so each migration stage has a rollback point:

```powershell
cd D:\Bioinformatics_Web\Bioinformatics_Web
git init
git add .
git commit -m "chore: capture bioinformatics platform baseline"
```

If Git identity is not configured:

```powershell
git config user.name "Your Name"
git config user.email "you@example.com"
```

---

## File Map

### Backend files to create

```text
backend/app/models/database_resource.py
backend/app/models/database_tutorial.py
backend/app/schemas/database_resource.py
backend/app/schemas/search.py
backend/app/repositories/database_repository.py
backend/app/repositories/search_repository.py
backend/app/services/database_service.py
backend/app/services/search_service.py
backend/app/api/v1/controllers/database_controller.py
backend/app/api/v1/controllers/search_controller.py
backend/app/seed_data/databases.py
backend/app/seed_data/database_tutorials.py
backend/tests/conftest.py
backend/tests/test_database_repository.py
backend/tests/test_database_seed.py
backend/tests/test_database_api.py
backend/tests/test_search_service.py
backend/tests/test_search_api.py
```

### Backend files to modify

```text
backend/requirements.txt
backend/app/models/__init__.py
backend/app/seed_data/__init__.py
backend/app/main.py
backend/init_db.py
```

### Frontend files to create

```text
frontend/lib/databaseTypes.ts
frontend/lib/databaseApi.ts
frontend/lib/searchTypes.ts
frontend/lib/searchApi.ts
frontend/components/SearchResults.tsx
frontend/app/search/page.tsx
```

### Frontend files to modify

```text
frontend/components/GlobalSearch.tsx
frontend/components/DatabaseBrowser.tsx
frontend/app/databases/page.tsx
frontend/app/databases/tutorials/[id]/page.tsx
frontend/app/page.tsx
```

### Frontend file to remove after migration

```text
frontend/lib/databaseResources.ts
```

---

### Task 0: Establish rollback and backend test tooling

**Files:**
- Modify: `backend/requirements.txt`
- Create: `backend/tests/conftest.py`

- [ ] **Step 1: Initialize Git and capture the baseline**

Run:

```powershell
cd D:\Bioinformatics_Web\Bioinformatics_Web
git init
git add .
git commit -m "chore: capture bioinformatics platform baseline"
```

- [ ] **Step 2: Add backend test dependencies**

Append pinned dependencies:

```text
pytest==8.3.4
httpx==0.28.1
```

- [ ] **Step 3: Rebuild the backend image**

Run:

```powershell
docker-compose build backend
docker-compose up -d backend
```

- [ ] **Step 4: Verify pytest is available**

Run:

```powershell
docker-compose exec backend pytest --version
```

Expected: pytest reports version `8.3.4`.

- [ ] **Step 5: Add isolated test database fixtures**

Create `backend/tests/conftest.py`:

- Use an in-memory SQLite engine with `StaticPool`.
- Create and drop SQLAlchemy metadata per test session.
- Provide a `db_session` fixture.
- Build a FastAPI test app with `create_app()`.
- Override `get_db` so API tests never write to development PostgreSQL.

- [ ] **Step 6: Commit test tooling**

```powershell
git add backend
git commit -m "test: add backend pytest foundation"
```

---

### Task 1: Add database resource and tutorial models

**Files:**
- Create: `backend/app/models/database_resource.py`
- Create: `backend/app/models/database_tutorial.py`
- Create: `backend/app/schemas/database_resource.py`
- Modify: `backend/app/models/__init__.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_database_repository.py`

- [ ] **Step 1: Write failing model persistence tests**

Test:

- A `DatabaseResource` can be persisted with JSON fields.
- A `DatabaseTutorial` can be persisted with a resource foreign key.
- Tutorials can be loaded through the resource relationship.
- Deleting a resource cascades to its tutorials.

- [ ] **Step 2: Run the focused test and confirm RED**

```powershell
docker-compose exec backend pytest tests/test_database_repository.py -q
```

Expected: import errors because models do not exist.

- [ ] **Step 3: Implement `DatabaseResource`**

Add:

- Integer primary key.
- Unique indexed `slug`.
- Navigation metadata fields.
- JSON list fields for use cases, data types, species, and tags.
- Optional download and API URLs.
- `created_at`.
- `tutorials` relationship with `cascade="all, delete-orphan"`.

- [ ] **Step 4: Implement `DatabaseTutorial`**

Add:

- Integer primary key.
- Unique indexed `slug`.
- Foreign key to `database_resources.id` with `ondelete="CASCADE"`.
- Tutorial metadata, JSON steps, Markdown content, and timestamps.
- Relationship back to `DatabaseResource`.

- [ ] **Step 5: Add Pydantic schemas**

Create:

- `DatabaseTutorialResponse`
- `DatabaseResourceResponse`
- `DatabaseTutorialDetailResponse`

Expose nested tutorials in resource list responses because the current navigation cards display tutorial entry links.

- [ ] **Step 6: Register models before metadata creation**

Update:

- `backend/app/models/__init__.py`
- model imports in `backend/app/main.py`

- [ ] **Step 7: Run focused tests and confirm GREEN**

```powershell
docker-compose exec backend pytest tests/test_database_repository.py -q
```

- [ ] **Step 8: Commit models**

```powershell
git add backend/app backend/tests
git commit -m "feat: add database resource and tutorial models"
```

---

### Task 2: Migrate database navigation content into backend seeds

**Files:**
- Create: `backend/app/seed_data/databases.py`
- Create: `backend/app/seed_data/database_tutorials.py`
- Modify: `backend/app/seed_data/__init__.py`
- Modify: `backend/init_db.py`
- Test: `backend/tests/test_database_seed.py`
- Source reference: `frontend/lib/databaseResources.ts`

- [ ] **Step 1: Write failing idempotency test**

Test:

- First seed inserts all database resources.
- Second seed inserts no duplicates.
- Tutorial slugs remain unique.
- Each tutorial references its expected resource.

- [ ] **Step 2: Run focused test and confirm RED**

```powershell
docker-compose exec backend pytest tests/test_database_seed.py -q
```

- [ ] **Step 3: Move database category and resource data**

Create `backend/app/seed_data/databases.py`.

Rules:

- Preserve stable frontend resource IDs as backend `slug`.
- Preserve category keys.
- Use UTF-8 Chinese text directly.
- Use `slug` lookup before insert.
- Do not delete existing user-edited rows during seed.

- [ ] **Step 4: Move tutorial data**

Create `backend/app/seed_data/database_tutorials.py`.

Rules:

- Preserve tutorial IDs as backend `slug`.
- Resolve resource IDs by resource slug.
- Seed only missing tutorial slugs.

- [ ] **Step 5: Register seed functions**

Update:

- `backend/app/seed_data/__init__.py`
- `backend/init_db.py`

Call database resource seed before tutorial seed.

- [ ] **Step 6: Run focused tests and confirm GREEN**

```powershell
docker-compose exec backend pytest tests/test_database_seed.py -q
```

- [ ] **Step 7: Initialize development PostgreSQL**

```powershell
docker-compose exec backend python init_db.py
```

- [ ] **Step 8: Commit seed migration**

```powershell
git add backend
git commit -m "feat: seed database resources and tutorials"
```

---

### Task 3: Add database navigation backend API

**Files:**
- Create: `backend/app/repositories/database_repository.py`
- Create: `backend/app/services/database_service.py`
- Create: `backend/app/api/v1/controllers/database_controller.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_database_api.py`

- [ ] **Step 1: Write failing API tests**

Cover:

```text
GET /api/databases
GET /api/databases?keyword=GEO
GET /api/databases?category_key=expression
GET /api/databases/tutorials/{slug}
GET /api/databases/tutorials/missing-slug
```

Expected missing tutorial response:

```json
{
  "code": 404,
  "message": "数据库教程不存在",
  "data": null
}
```

- [ ] **Step 2: Run focused test and confirm RED**

```powershell
docker-compose exec backend pytest tests/test_database_api.py -q
```

- [ ] **Step 3: Implement repository filters**

Support:

- `keyword`
- `category_key`
- `data_type`
- `species`
- `limit`

Use SQL filtering for plain text fields. For MVP JSON array filters, use a small Python post-filter after the SQL query, matching the existing Pipeline metadata filtering style.

- [ ] **Step 4: Implement service not-found behavior**

Raise `HTTPException(status_code=404)` for missing resource or tutorial.

- [ ] **Step 5: Register controller**

Add:

```text
GET /api/databases
GET /api/databases/{slug}
GET /api/databases/tutorials/{slug}
```

Register router in `backend/app/main.py`.

- [ ] **Step 6: Run focused tests and confirm GREEN**

```powershell
docker-compose exec backend pytest tests/test_database_api.py -q
```

- [ ] **Step 7: Probe development endpoints**

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/databases
Invoke-WebRequest -UseBasicParsing http://localhost:8000/api/databases/tutorials/sra-fastq-download
```

- [ ] **Step 8: Commit database API**

```powershell
git add backend
git commit -m "feat: expose database navigation api"
```

---

### Task 4: Add weighted unified backend search

**Files:**
- Create: `backend/app/schemas/search.py`
- Create: `backend/app/repositories/search_repository.py`
- Create: `backend/app/services/search_service.py`
- Create: `backend/app/api/v1/controllers/search_controller.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_search_service.py`
- Test: `backend/tests/test_search_api.py`

- [ ] **Step 1: Write failing scoring tests**

Create fixtures where:

- One title exactly matches `RNA-seq`.
- One title contains `RNA-seq`.
- One summary contains `RNA-seq`.
- One Markdown body contains `RNA-seq`.

Assert score order:

```text
exact title > title contains > category/tag > summary > Markdown body
```

- [ ] **Step 2: Write failing type-filter and stable-order tests**

Assert:

- `type=algorithm` returns only algorithm results.
- Equal-score results sort by resource type priority.
- Equal-score results of the same type sort by primary key.
- Counts are calculated before `limit`.

- [ ] **Step 3: Run service tests and confirm RED**

```powershell
docker-compose exec backend pytest tests/test_search_service.py -q
```

- [ ] **Step 4: Implement search schemas**

Create:

- `SearchResourceType`
- `SearchResultItem`
- `SearchResultCounts`
- `SearchResponse`

- [ ] **Step 5: Implement repository candidate queries**

Query candidates from:

- `Pipeline`
- `Algorithm`
- `DatabaseResource`
- `DatabaseTutorial`
- `Literature`

Use `ILIKE` expressions to fetch possible matches. Calculate the maximum score per resource using explicit Python functions after candidate retrieval. Keep scoring readable and testable.

- [ ] **Step 6: Implement service validation and sorting**

Rules:

- Trim whitespace.
- Reject keywords shorter than 2 characters with `HTTPException(status_code=400)`.
- Validate resource type.
- Sort by score descending, resource priority, then numeric primary key.
- Apply `limit` after counts are calculated.

- [ ] **Step 7: Write failing API tests**

Cover:

```text
GET /api/search?q=RNA-seq
GET /api/search?q=RNA-seq&type=pipeline
GET /api/search?q=a
GET /api/search?q=missing-keyword
```

- [ ] **Step 8: Register search controller**

Expose:

```text
GET /api/search?q=RNA-seq&type=all&limit=20
```

- [ ] **Step 9: Run search tests and confirm GREEN**

```powershell
docker-compose exec backend pytest tests/test_search_service.py tests/test_search_api.py -q
```

- [ ] **Step 10: Run all backend tests**

```powershell
docker-compose exec backend pytest -q
```

- [ ] **Step 11: Commit unified search backend**

```powershell
git add backend
git commit -m "feat: add weighted unified search api"
```

---

### Task 5: Add frontend API types and adapters

**Files:**
- Create: `frontend/lib/databaseTypes.ts`
- Create: `frontend/lib/databaseApi.ts`
- Create: `frontend/lib/searchTypes.ts`
- Create: `frontend/lib/searchApi.ts`

- [ ] **Step 1: Add frontend DTO types**

Define backend DTOs using snake_case fields.

- [ ] **Step 2: Add UI database types**

Retain the current camelCase UI contract used by `DatabaseBrowser`:

```text
categoryKey
categoryName
useCases
dataTypes
downloadUrl
apiUrl
```

- [ ] **Step 3: Implement database adapters**

Add:

```text
fetchDatabaseResources()
fetchDatabaseTutorial(slug)
mapDatabaseResource(dto)
mapDatabaseTutorial(dto)
```

- [ ] **Step 4: Implement search API client**

Add:

```text
fetchSearchResults({ query, type, limit })
```

Support both server-side and browser-side base URLs:

```text
BACKEND_API_URL
NEXT_PUBLIC_BACKEND_API_URL
```

- [ ] **Step 5: Type-check**

```powershell
docker-compose exec frontend npx tsc --noEmit --pretty false
```

- [ ] **Step 6: Commit adapters**

```powershell
git add frontend/lib
git commit -m "feat: add frontend database and search api adapters"
```

---

### Task 6: Migrate database navigation pages to backend data

**Files:**
- Modify: `frontend/components/DatabaseBrowser.tsx`
- Modify: `frontend/app/databases/page.tsx`
- Modify: `frontend/app/databases/tutorials/[id]/page.tsx`
- Modify: `frontend/app/page.tsx`

- [ ] **Step 1: Derive categories from API resources**

Remove `databaseCategories` static imports from `DatabaseBrowser.tsx`.

Build category options from:

```text
resource.categoryKey
resource.categoryName
```

- [ ] **Step 2: Fetch database navigation data on the server**

Make `frontend/app/databases/page.tsx` async.

Fetch resources with `fetchDatabaseResources()`.

Calculate:

- resource count
- tutorial count
- unique category count

- [ ] **Step 3: Fetch tutorial details from the backend**

Make `frontend/app/databases/tutorials/[id]/page.tsx` async.

Replace static lookup with `fetchDatabaseTutorial(params.id)`.

Remove `generateStaticParams()` because tutorials are now runtime database content.

- [ ] **Step 4: Update homepage metrics**

Replace static database resource imports in `frontend/app/page.tsx` with backend API counts.

- [ ] **Step 5: Type-check**

```powershell
docker-compose exec frontend npx tsc --noEmit --pretty false
```

- [ ] **Step 6: Probe migrated pages**

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:3000/databases
Invoke-WebRequest -UseBasicParsing http://localhost:3000/databases/tutorials/sra-fastq-download
Invoke-WebRequest -UseBasicParsing http://localhost:3000/
```

- [ ] **Step 7: Commit navigation migration**

```powershell
git add frontend
git commit -m "feat: load database navigation from backend"
```

---

### Task 7: Add complete search results page

**Files:**
- Create: `frontend/components/SearchResults.tsx`
- Create: `frontend/app/search/page.tsx`

- [ ] **Step 1: Build presentational search result cards**

`SearchResults.tsx` displays:

- type badge
- title
- description
- tags
- score-independent UI
- destination link

Do not expose internal score values to users.

- [ ] **Step 2: Build server-rendered search page**

Use URL parameters:

```text
/search?q=RNA-seq&type=all
```

Render:

- PageHeader
- GET search form
- total result count
- type tabs with counts
- results list
- empty state with recommended keywords

- [ ] **Step 3: Keep filters URL-driven**

Use `<Link>` tabs:

```text
全部 / 分析流程 / 软件与算法 / 数据库 / 教程 / 文献
```

Each tab preserves `q` and updates `type`.

- [ ] **Step 4: Type-check**

```powershell
docker-compose exec frontend npx tsc --noEmit --pretty false
```

- [ ] **Step 5: Probe search page**

```powershell
Invoke-WebRequest -UseBasicParsing "http://localhost:3000/search?q=RNA-seq"
Invoke-WebRequest -UseBasicParsing "http://localhost:3000/search?q=RNA-seq&type=pipeline"
```

- [ ] **Step 6: Commit search results page**

```powershell
git add frontend
git commit -m "feat: add complete search results page"
```

---

### Task 8: Point header search preview at `/api/search`

**Files:**
- Modify: `frontend/components/GlobalSearch.tsx`

- [ ] **Step 1: Remove temporary aggregation**

Remove:

- static database resource imports
- separate Pipeline request
- separate Algorithm request
- Literature full-list request
- frontend ranking logic

- [ ] **Step 2: Request unified backend search**

Keep the existing 250ms debounce.

Request:

```text
GET /api/search?q={keyword}&limit=8
```

- [ ] **Step 3: Add keyboard navigation baseline**

Support:

- `Enter`: navigate to `/search?q=...`
- `Escape`: close preview panel

Use `useRouter()` from `next/navigation`.

- [ ] **Step 4: Replace preview footer**

Replace the current Pipeline-only link with:

```text
查看全部结果
```

Destination:

```text
/search?q={keyword}
```

- [ ] **Step 5: Preserve loading, empty, and error states**

The navigation bar must remain usable even if `/api/search` fails.

- [ ] **Step 6: Type-check**

```powershell
docker-compose exec frontend npx tsc --noEmit --pretty false
```

- [ ] **Step 7: Commit header integration**

```powershell
git add frontend/components/GlobalSearch.tsx
git commit -m "feat: connect header preview to unified search"
```

---

### Task 9: Remove migrated frontend static content and update documentation

**Files:**
- Delete: `frontend/lib/databaseResources.ts`
- Modify: `docs/API_REFERENCE.md`
- Modify: `docs/DATABASE_AND_SEED.md`
- Modify: `docs/FRONTEND_GUIDE.md`
- Modify: `docs/DEVELOPMENT_SETUP.md`

- [ ] **Step 1: Confirm no frontend imports remain**

```powershell
rg "databaseResources|getAllDatabaseTutorials|getDatabaseTutorialById|databaseCategories" frontend
```

Expected: no references outside migration notes.

- [ ] **Step 2: Delete static database resource file**

Delete:

```text
frontend/lib/databaseResources.ts
```

- [ ] **Step 3: Document new APIs**

Add:

```text
GET /api/databases
GET /api/databases/{slug}
GET /api/databases/tutorials/{slug}
GET /api/search
```

- [ ] **Step 4: Document seed initialization**

Update initialization instructions to mention database resources and tutorials.

- [ ] **Step 5: Document Docker command compatibility**

Explain:

- Prefer `docker compose` in a normal Docker Desktop terminal.
- Use `docker-compose` if Compose plugin discovery is unavailable.

- [ ] **Step 6: Commit cleanup and docs**

```powershell
git add frontend docs
git commit -m "docs: document unified search and database migration"
```

---

### Task 10: Final verification

**Files:**
- Verify only

- [ ] **Step 1: Rebuild and restart**

```powershell
docker-compose up -d --build
```

- [ ] **Step 2: Run backend tests**

```powershell
docker-compose exec backend pytest -q
```

- [ ] **Step 3: Run frontend type check**

```powershell
docker-compose exec frontend npx tsc --noEmit --pretty false
```

- [ ] **Step 4: Initialize the development database twice**

```powershell
docker-compose exec backend python init_db.py
docker-compose exec backend python init_db.py
```

Expected: both runs succeed without duplicate data.

- [ ] **Step 5: Probe backend endpoints**

```powershell
$paths = @(
  "/api/health",
  "/api/databases",
  "/api/databases/tutorials/sra-fastq-download",
  "/api/search?q=RNA-seq",
  "/api/search?q=RNA-seq&type=pipeline"
)

foreach ($path in $paths) {
  $response = Invoke-WebRequest -UseBasicParsing "http://localhost:8000$path"
  "$path $($response.StatusCode)"
}
```

Expected: every endpoint returns `200`.

- [ ] **Step 6: Probe frontend routes**

```powershell
$paths = @(
  "/",
  "/pipelines",
  "/algorithms",
  "/databases",
  "/literatures",
  "/search?q=RNA-seq",
  "/databases/tutorials/sra-fastq-download"
)

foreach ($path in $paths) {
  $response = Invoke-WebRequest -UseBasicParsing "http://localhost:3000$path"
  "$path $($response.StatusCode)"
}
```

Expected: every route returns `200`.

- [ ] **Step 7: Check logs**

```powershell
docker-compose logs backend --tail=100
docker-compose logs frontend --tail=100
```

Expected: no unhandled exceptions or TypeScript compilation errors.

- [ ] **Step 8: Commit verified implementation**

```powershell
git status --short
git add .
git commit -m "feat: complete unified search center"
```

