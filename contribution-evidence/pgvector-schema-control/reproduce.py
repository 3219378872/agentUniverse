"""Real PGVectorStore reproduction against a dedicated disposable Docker database."""
import asyncio
import json
import subprocess

import psycopg
from psycopg.conninfo import make_conninfo

from agentuniverse.agent.action.knowledge.store.pgvector_store import PGVectorStore
from agentuniverse.agent.action.knowledge.store.query import Query

port = subprocess.check_output(
    ['docker', 'port', 'wuzhen-au-pgvector-repro', '5432'], text=True
).strip().rsplit(':', 1)[1]
admin = make_conninfo(host='127.0.0.1', port=port, dbname='wuzhen_pgvector_test', user='postgres')
with psycopg.connect(admin, autocommit=True) as conn:
    conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
    conn.execute("DO $$ BEGIN CREATE ROLE au_app LOGIN; EXCEPTION WHEN duplicate_object THEN NULL; END $$")
    conn.execute('CREATE TABLE IF NOT EXISTS docs (id TEXT PRIMARY KEY, text TEXT NOT NULL, metadata JSONB NOT NULL, embedding vector(2) NOT NULL)')
    conn.execute("INSERT INTO docs VALUES ('one', 'original', '{}', '[1,0]') ON CONFLICT (id) DO NOTHING")
    conn.execute('GRANT USAGE ON SCHEMA public TO au_app')
    conn.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON docs TO au_app')
    print('server:', conn.execute('SELECT version()').fetchone()[0])
    print('pgvector:', conn.execute("SELECT extversion FROM pg_extension WHERE extname='vector'").fetchone()[0])

results = []
for read_only in [False, True]:
    url = make_conninfo(admin, user='au_app', options='-c default_transaction_read_only=on' if read_only else '')
    store = PGVectorStore(connection_url=url, table_name='docs', dimensions=2, create_table=False)
    try:
        documents = store.query(Query(embeddings=[[1.0, 0.0]]))
        results.append({'mode': 'sync', 'read_only': read_only, 'ids': [d.id for d in documents]})
    except Exception as exc:
        results.append({'mode': 'sync', 'read_only': read_only, 'error': type(exc).__name__, 'detail': str(exc)})
    finally:
        if store.client:
            store.client.close()

async def check_async():
    for read_only in [False, True]:
        url = make_conninfo(admin, user='au_app', options='-c default_transaction_read_only=on' if read_only else '')
        store = PGVectorStore(connection_url=url, table_name='docs', dimensions=2, create_table=False)
        try:
            documents = await store.async_query(Query(embeddings=[[1.0, 0.0]]))
            results.append({'mode': 'async', 'read_only': read_only, 'ids': [d.id for d in documents]})
        except Exception as exc:
            results.append({'mode': 'async', 'read_only': read_only, 'error': type(exc).__name__, 'detail': str(exc)})
        finally:
            if store.async_client:
                await store.async_client.close()
asyncio.run(check_async())
print(json.dumps(results, indent=2))
