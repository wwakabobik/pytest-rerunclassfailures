## Design note: reliance on pytest private internals

The plugin drives reruns via `_pytest.runner.runtestprotocol` (a direct import, not a hook) and
by manipulating `item.session._setupstate.stack` / `.teardown_exact()` directly — genuinely
private, underscore-prefixed pytest internals with no compatibility guarantee. Verified stable
across pytest 7.4.3 through 9.1.1 as of this writing.

Ideas for later, if it becomes worth the effort:
1. Isolate all `_pytest.*` private imports into one small internal shim module, so a future
   pytest-internals break is localized to one file instead of scattered across the plugin.
2. Add an explicit pytest-version axis to CI (not just Python versions) — e.g. pytest 7.2
   (floor), 8.x, and 9.x explicitly — to catch a real break the day it happens instead of
   relying on chance.
