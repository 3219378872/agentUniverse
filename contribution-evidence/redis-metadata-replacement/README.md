Evidence for agentUniverse #3293

Tested implementation: 631f152 (fix/redis-vector-stale-metadata).

The screenshot renders the actual unittest stdout/stderr from fixed-tests.log. Both Redis Search integration tests fail with the original production file and pass with the patch. This evidence branch is separate from the code PR. Redis 8 + Search was used on a dedicated disposable local instance. Full application and external model providers were not tested.
