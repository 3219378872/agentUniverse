# PGVectorStore schema creation regression evidence

Source commit: `dc701a720d91d64a449821b167eec023aa29031c`.
Upstream baseline: `254ecd280f54c2d2de654bbe5373e9f947d2dedf`.
Issue: https://github.com/agentuniverse-ai/agentUniverse/issues/3295

`create_table=False` previously still issued CREATE EXTENSION / TABLE / INDEX.
Actual store queries failed for a DML-only application role and for read-only
connections even when the required extension and table already existed.

The fixed source passes 25 unit tests and 4 real database tests (29 total).
The asynchronous integration test covers restricted-role CRUD, read-only queries,
and default automatic provisioning. The same suite against the original source
has 6 assertion failures and 4 database-error subcases. `baseline-real.log` and
`fixed-real.log` also show the separate four-way sync/async and read/write/read-only
query reproduction. `test-results.png` renders the captured test output; it is
not a screenshot of a production application.

Environment: Ubuntu 24.04, Python 3.11.15, psycopg 3.3.4, pgvector Python 0.5.0,
PostgreSQL 16.15, server pgvector 0.8.6. Docker image:
`pgvector/pgvector@sha256:ccc6e83d6e35e931dc7c5def2022729d5a6c370318d099181995567ff1fb4d6b`.
No embedding provider or business database was used. This is real isolated
store/database integration, not full application or production acceptance.

## Replay

Check out the source commit above and install its store dependencies, including
`psycopg[binary]==3.3.4` and `pgvector==0.5.0`. Provision a disposable PostgreSQL
instance from the pinned image and create a database named `test_au_pgvector`.
Set `AGENTUNIVERSE_PGVECTOR_TEST_URL` to its administrator URL; the test creates
unique schemas and restricted roles and removes them afterwards. It refuses to
mutate databases whose names do not start with `test_`. Do not point it at an
application database. From the source checkout:

```sh
python -m unittest \
  tests.test_agentuniverse.unit.agent.action.knowledge.store.test_pgvector_store \
  tests.test_agentuniverse.integration.test_pgvector_store_permissions -v
```

The integration tests skip when the dedicated URL is absent. To repeat the red
comparison, run `run_baseline_tests.py` from the source checkout with `PYTHONPATH=.`
and the same test URL. It loads the exact upstream production source from Git
in a fresh Python process, without modifying checkout files or mocking SQL.
Fetch the baseline commit first if using a shallow clone that lacks it.

The separate `reproduce.py` uses the specifically named disposable container
`wuzhen-au-pgvector-repro` and database `wuzhen_pgvector_test`; it creates its own
fixture role/table in that container. It is not a general application DB runner.

No additional signing or authorization is implied by these test artifacts.
