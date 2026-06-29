# Review Checklists

## PR review checklist

- [ ] Scope matches work order.
- [ ] No tracking added.
- [ ] No video support added.
- [ ] No segmentation support added.
- [ ] No background jobs added.
- [ ] No database added.
- [ ] No image persistence added.
- [ ] No external URL fetcher added.
- [ ] API key auth enforced on `/v1` endpoints.
- [ ] `/healthz` does not expose sensitive data.
- [ ] Request validation rejects unsupported inputs.
- [ ] Tests are GPU-free unless explicitly marked otherwise.
- [ ] Detector can be mocked in API tests.
- [ ] No real secrets committed.
- [ ] Docs match behavior.
- [ ] Skipped tests are reported honestly.

## Release readiness checklist

- [ ] MVP endpoints implemented.
- [ ] All MVP tests pass.
- [ ] No required tests skipped.
- [ ] README has working example.
- [ ] API contract matches implementation.
- [ ] Compatibility limitations are documented.
- [ ] Security rules are satisfied.
- [ ] CPU operation is verified.
- [ ] Known limitations are documented.
- [ ] Human release approval given.
