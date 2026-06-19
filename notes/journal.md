# learning-μCMZ — journal

A worklog for this hands-on study of the μCMZ primitives (Orrù 2024, ePrint
2024/1552). ISO-dated entries, newest appended at the bottom.

---

## 2026-06-19

Project started. Goal: learn the basic cryptographic components underlying μCMZ
by implementing them myself in Lean 4 (see [`README.md`](../README.md) for the
primitive roadmap and design decisions).

- Scaffolded the Lean 4 + Mathlib project; build is green.
- Settled the setup: Mathlib-backed, concrete group = Schnorr group (order-p
  subgroup of (ℤ_q)ˣ), primitives-only scope, paper as the only source.
- Created the private repo `ZKForAll/learning-muCMZ`. Paper PDF kept locally
  under `resources/` but untracked (`.git/info/exclude`).
- Next: implement Layer 0a — the prime-order group.
