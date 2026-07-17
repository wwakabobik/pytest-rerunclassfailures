- Call class-scope fixtures while recreating class (and, thus, teardown) — DONE (see CHANGELOG 0.2.0):
  function- and class-scope fixtures are now genuinely torn down (real finalizers run) and
  re-invoked between class reruns. Module/package/session-scope fixtures are still left
  untouched on purpose, since they may be shared beyond the rerun cycle.

- `_remove_non_initial_attributes` enabled (was previously dead code, blocked on the item
  above) — DONE (see CHANGELOG 0.2.0): a class attribute lazily created during a rerun cycle
  (e.g. `if not hasattr(request.cls, "user"): request.cls.user = ...`) is now removed between
  reruns, instead of surviving in whatever state a previous, aborted attempt left it in.

- pytest-rerunfailures compatibility — DONE (see CHANGELOG 0.2.0): both plugins hook
  `pytest_runtest_protocol` (a `firstresult` hookspec), so this plugin previously always
  claimed every item unconditionally, silently disabling pytest-rerunfailures entirely (even
  for tests outside any class). Fixed by deferring (returning `None` instead of `False`,
  and no longer calling the real protocol manually) for items this plugin doesn't manage
  (non-class items, or when disabled) — pytest-rerunfailures now cooperates correctly for
  standalone tests. For a test *method inside a class this plugin reruns*, true cooperation
  isn't possible (the class-level rerun already owns that item's fate), so `pytest_configure`
  now detects `pytest-rerunfailures` and raises a clear `UsageError` unless
  `--allow-rerunfailures` is passed, explaining that class-scoped markers get superseded.

- Known residual limitation: a class attribute set purely as a side effect of a
  *function-scope* fixture whose return value is consumed as a test parameter (not stored on
  `self`) can still leak stale per-test state across reruns. This is because pytest's
  `Function` item permanently memoizes the bound test-class instance on itself
  (`Function.instance`/`Function._instance`), and this plugin reruns the same `Function` item
  objects rather than fresh ones — so a stale *instance*-level attribute set by a previous
  failed attempt's own test body can shadow the class-level attribute a fixture resets. This is
  independent of fixture-cache teardown and is not fixed by the class/function fixture teardown
  above; see `tests/test_class_attributes.py::test_class_attributes_function_fixtures` (kept as
  `xfail`) and the matching note in README.md's "Known limitations".

## Design note: reliance on pytest private internals

The plugin drives reruns via `_pytest.runner.runtestprotocol` (a direct import, not a hook) and
by manipulating `item.session._setupstate.stack` / `.teardown_exact()` directly — genuinely
private, underscore-prefixed pytest internals with no compatibility guarantee.

Verified while working on the fixture-teardown fix above: these APIs are stable across pytest
7.4.3 through 9.1.1 as of this writing, so there is no active breakage today — the risk is
speculative/future, not current. If/when it becomes worth the effort, consider:

1. Isolating all `_pytest.*` private imports into one small internal shim module, so a future
   pytest-internals break is localized to one file instead of scattered across the plugin.
2. Adding an explicit pytest-version axis to CI (not just Python versions) — e.g. pytest 7.2
   (floor), 8.x, and 9.x explicitly — to catch a real break the day it happens instead of
   relying on chance.
3. Capping the `pytest` dependency (e.g. `pytest>=7.2,<10`) so a future major bump can't
   silently break installs before the plugin has been verified against it.

None of the above has been implemented yet — this is a forward-looking note, not a task in
progress.
