"""Run the new regression modules against the exact upstream production module."""
import subprocess
import unittest

from agentuniverse.agent.action.knowledge.store import pgvector_store

baseline = '254ecd280f54c2d2de654bbe5373e9f947d2dedf'
source = subprocess.check_output([
    'git', 'show', baseline + ':agentuniverse/agent/action/knowledge/store/pgvector_store.py'
], text=True)
exec(compile(source, '<upstream-pgvector-store-' + baseline + '>', 'exec'), pgvector_store.__dict__)
suite = unittest.defaultTestLoader.loadTestsFromNames([
    'tests.test_agentuniverse.unit.agent.action.knowledge.store.test_pgvector_store',
    'tests.test_agentuniverse.integration.test_pgvector_store_permissions',
])
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() else 1)
