# Findings from the streaming CLI wave

- **Fixed, standard library/runtime:** files lacked a common bounded `readLine`.
  D101 separates stdin/file line handling, limits each line and preserves the
  shared alias cursor. Applications do not read the entire file into `[]byte`.
- **Fixed, native:** JSON encoding fresh records inside a loop read the first
  record's fields. Minimal case: create `Row { value: key, count }` from a Map
  and call `json.encode`; VM changed pairs while native repeated the first.
  The backend now checks the current managed reference and refreshes child-array
  hints. The original count workload checks the fix; application code was not
  changed to avoid the failure.
- **Open, checker, blocks correct diagnostics:**
  `fn f(r: Result<void,int>):int { return match r { Ok(value)=>0, Err(e)=>e, }; }`
  exits with internal status 70 without T0002. Void cannot be stored in a named
  binding; the expected result is the same diagnostic rejection as an ordinary
  named binding. This application uses the normative `Ok(_)`. Owner:
  enum-pattern binding.
- **Source ergonomics observation:** a Map loop accepts one tuple name:
  `for pair in values { match pair { (key, value) => ... } }`. Generalized
  binding in the `for` header is not implemented. Extending that syntax needs
  coordinated parser/checker/formatter work.
- **Intentional:** put/add returns a bool already known after the limit check.
  `const _ = operation(...).mapError(...) ?` discards only the bool; errors
  remain handled and reach the user.
- **Open:** the D098 escaping-mutable-capture warning, CLI0 named budgets,
  claimed-platform evidence and an ordinary installed build on every Tier 1.

Ideas and pages from Vladimirov's book were not used for this change. These
are historical findings; their recorded status is not a new compiler audit.
