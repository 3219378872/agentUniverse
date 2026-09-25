# ContextBudgetCompressor Unicode truncation evidence

Source commit `e4491465bd6e75b2bb8b5439cb987d149786c37f`.
Upstream baseline `254ecd280f54c2d2de654bbe5373e9f947d2dedf`.
Issue https://github.com/agentuniverse-ai/agentUniverse/issues/3297

The original token slice can end within a UTF-8 character. Decoding inserts
U+FFFD and can exceed the token budget: cl100k_base turns input ` раб` with
budget 1 into ` ра�`, which requires 3 tokens. The fix drops incomplete UTF-8
suffixes and checks the re-encoded prefix, shortening it when necessary.

## Executed checks

- Python 3.11.15, tiktoken 0.12.0, Ubuntu 24.04.
- 32 related tests pass, including 8 added regression tests.
- The same 32-test suite against original production code reports 33 assertion
  failures including parameterized subcases; this is not 33 separate test methods.
- All 8 new tests also pass with an empty TIKTOKEN_CACHE_DIR and unreachable
  HTTP/HTTPS proxies. The cache remains empty: the tests use actual in-memory
  tiktoken BPE encoders and need no downloaded vocabulary.
- Published cl100k_base / p50k_base encodings: 135 boundaries across 9 strings,
  50 failing boundaries before, none after. See baseline-real.json/fixed-real.json.
- New test Ruff lint and format checks pass. The production module has the same
  11 existing Ruff diagnostics on base and fix, with identical codes/messages.
- git diff --check passes.

The screenshot renders actual captured test output. This validates the document
processor and real tokenizer boundary, not a hosted LLM or complete RAG deployment.

## Replay from the source checkout

Install the repository dependencies (including tiktoken 0.12.0), then run:

```sh
python -m unittest \
  tests.test_agentuniverse.unit.agent.action.knowledge.doc_processor.test_context_budget_unicode \
  tests.test_agentuniverse.unit.agent.action.knowledge.doc_processor.test_context_budget_compressor -v
```

The original test module uses published tiktoken encodings, so its first run may
download vocabularies. The new Unicode regression module is fully offline.
For the published-encoding matrix, run `reproduce.py` with PYTHONPATH=. from
the source checkout, and add `--baseline` for the exact original source.
`run_baseline_tests.py` similarly runs the current tests against upstream source
loaded in a fresh process; neither script overwrites the checkout.
A shallow clone must fetch the baseline commit before those red comparisons.
