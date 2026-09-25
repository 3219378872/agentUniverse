"""Load exact upstream production code before running the current tests."""
import subprocess
import unittest
from agentuniverse.agent.action.knowledge.doc_processor import context_budget_compressor as cbc

base='254ecd280f54c2d2de654bbe5373e9f947d2dedf'
source=subprocess.check_output(['git','show',base+':agentuniverse/agent/action/knowledge/doc_processor/context_budget_compressor.py'],text=True)
exec(compile(source,'<upstream-context-budget-'+base+'>','exec'),cbc.__dict__)
suite=unittest.defaultTestLoader.loadTestsFromNames([
    'tests.test_agentuniverse.unit.agent.action.knowledge.doc_processor.test_context_budget_unicode',
    'tests.test_agentuniverse.unit.agent.action.knowledge.doc_processor.test_context_budget_compressor',
])
r=unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if r.wasSuccessful() else 1)
