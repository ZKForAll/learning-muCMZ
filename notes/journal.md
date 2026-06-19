# learning-μCMZ — journal (design decisions & rationale)

The internal "why" record: design and formalization decisions, with enough
context to backtrack or explain choices later. ISO-dated entries, newest appended
at the bottom. The reportable study notes live in [`notes.md`](notes.md).

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

### Convention — paper fidelity vs Lean idiom

Decision: **the paper (O24) governs the cryptographic vocabulary; Lean/Mathlib
governs the host-language scaffolding. On a collision, use the idiomatic Lean
construct but keep the paper symbol visible** (via unicode notation and/or a
docstring citing O24 §x.y).

- Object / algorithm / variable names → paper, verbatim: `sk`, `pp`, `crs`,
  `MAC = (S,K,M,V)`, `mᵢ`, `U`, `V`, `x₀`.
- Math notation → paper, in unicode (usually already Lean-idiomatic): `ℤ_p` is
  `ZMod p`; additive `x • P` uses Mathlib's `•`; generator `G` is `𝒢`.
- Typeclass/structure design, generics, namespacing, casing → Lean/Mathlib:
  reuse `Field`/`AddCommGroup`/`ZMod`, monad param `m`, `UpperCamelCase` types,
  `lowerCamelCase` defs.
- Game/advantage function *names* → Lean idiom, paper symbol in the docstring
  (e.g. `advUFCMVA` with `-- O24 Fig 5`).
- Each primitive module opens with a docstring mapping paper ↔ Lean and the
  relevant §.

Most of the time there is no conflict — the paper's `•`, `ℤ_p`, `sk`, `gen` are
also what idiomatic Lean wants; this rule only decides the rare collisions.
