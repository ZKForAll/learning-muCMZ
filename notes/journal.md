# learning-μCMZ journal (design decisions and rationale)

The internal "why" record holds design and formalization decisions, with enough
context to backtrack or explain choices later. ISO-dated entries, newest appended
at the bottom. The reportable study notes live in [`notes.md`](notes.md).

---

## 2026-06-19

Project started. The goal is to learn the basic cryptographic components
underlying μCMZ by implementing them myself in Lean 4 (see [`README.md`](../README.md)
for the primitive roadmap and design decisions).

- Scaffolded the Lean 4 + Mathlib project; build is green.
- Settled the setup as Mathlib-backed, with concrete group = Schnorr group
  (order-p subgroup of (ℤ_q)ˣ), primitives-only scope, and paper as the only
  source.
- Created the private repo `ZKForAll/learning-muCMZ`. Paper PDF kept locally
  under `resources/` but untracked (`.git/info/exclude`).
- Next, implement Layer 0a, the prime-order group.

### Convention on paper fidelity vs Lean idiom

The decision is that **the paper (O24) governs the cryptographic vocabulary; Lean/Mathlib
governs the host-language scaffolding. When the two collide, keep the Lean
notation and add a docstring relating it to the paper** (citing O24 §x.y).

- Object, algorithm, and variable names follow the paper verbatim, such as `sk`,
  `pp`, `crs`, `MAC = (S,K,M,V)`, `mᵢ`, `U`, `V`, `x₀`.
- Math notation follows the paper in unicode, which is usually already
  Lean-idiomatic. `ℤ_p` is `ZMod p`, additive `x • P` uses Mathlib's `•`, and
  generator `G` is `g`.
- Typeclass and structure design, generics, namespacing, and casing follow Lean
  and Mathlib. Reuse `Field`, `AddCommGroup`, `ZMod`, the monad parameter `m`,
  `UpperCamelCase` types, and `lowerCamelCase` defs.
- Game and advantage function *names* follow Lean idiom, with the paper symbol in
  the docstring, for example `advUFCMVA` with `-- O24 Fig 5`.
- Each primitive module opens with a docstring mapping paper ↔ Lean and the
  relevant §.

Most of the time there is no conflict, since the paper's `•`, `ℤ_p`, `sk`, `gen`
are also what idiomatic Lean wants. This rule only decides the rare collisions.

### Group setting binders (Layer 0a)

The group description Γ = (𝔾, p, G) is fixed as ambient typeclass context and is
not modeled as a `GrGen` procedure. For defining and evaluating the primitives
the binders `(p : ℕ) [Fact p.Prime]`, `[AddCommGroup G]`, `[Module (ZMod p) G]`,
and a generator `(g : G)` suffice, since `Module (ZMod p) G` already forces
`p • x = 0`. `[IsAddCyclic G]` and `Nat.card G = p` are added only when a proof
needs the `ZMod p ≃ G` bijection. The discrete logarithm assumption is not a
typeclass. It is a §3.1 experiment, asymptotic in λ.

### Probabilistic monad representation (PMF now, FreeM later)

We represent the randomized MAC algorithms (S, K, M) with Mathlib's `PMF`, the
probability mass function monad, and keep V a plain function. PMF is denotational,
Mathlib-native, and lawful, so the syntax and correctness stay light and the
probabilities are direct.

Later we refactor to a free monad over a polynomial functor (`FreeM`), which
separates the program syntax from its semantics and supports the oracle access
and reinterpretation the game layer needs. At that point we must argue, and
preferably prove, that the two representations agree. The intended statement is
that a probability handler ⟦·⟧ : `FreeM Sig α → PMF α` is a monad morphism and
that the `FreeM` MAC interpreted under it equals the `PMF` MAC. Proving the
handler respects `pure` and `bind` gives the equivalence pointwise as
distributions.

**Superseded on 2026-06-21**, see below. We adopt `FreeM` from the start instead
of staging PMF first.

## 2026-06-21

### Free monad from the start, via VCVio

We reverse the PMF-now/FreeM-later staging. The randomized MAC algorithms become
programs in a free monad over a polynomial functor from the start, and PMF
becomes one semantic domain reached by a handler, not the monad the algorithms
live in.

- **Why.** Correctness alone fits PMF, but unforgeability (UF-CMVA, O24 Fig 5)
  needs adaptive oracle access (Sign, Verify) and the mutable query set Qrs,
  which a PMF cannot express. The free monad separates program syntax from
  handler semantics, so one MAC program runs under a probability handler for
  correctness and under an oracle handler for the game. Committing to `FreeM` up
  front avoids carrying two representations and the equivalence proof between
  them.
- **Reuse VCVio.** We use VCVio's `PFunctor.FreeM` (`ToMathlib.PFunctor.Free`)
  and its `OracleComp` layer rather than hand-rolling. VCVio already supplies the
  `Monad`/`LawfulMonad` instances, monad morphisms, and oracle simulation the
  game layer needs.
- **Build change.** Toolchain `leanprover/lean4:v4.22.0` → `v4.28.0` (VCVio's
  pin; a project and its deps share one toolchain). `lakefile.toml` now requires
  `mathlib @ v4.28.0` and `VCVio @ git v4.28.0`
  (https://github.com/Verified-zkEVM/VCV-io). The local VCVio checkout
  (`learn/vcv-io-exploration`, `37ec339`, `v4.28.0-44-g…`) is unpushed, so we pin
  the `v4.28.0` tag, which already carries `Free.lean` and `OracleComp`. Mathlib
  cache refetched at the new rev.
- **PMF role.** PMF is now the codomain of the handler ⟦·⟧ : `FreeM Sig α → PMF α`,
  a monad morphism. Correctness reads `M`'s program under ⟦·⟧ and checks
  acceptance with probability 1.
- **Notes §4 restructured.** 4.1 monads, 4.2 free monads over polynomial functors
  (with the universe bump `Type (max uA uB v)`), 4.3 probabilistic monads (PMF as
  semantics), 4.4 the MAC structure over `FreeM Sig`. The MAC structure gains a
  `Sig : PFunctor` parameter. The notes checker preamble now imports
  `ToMathlib.PFunctor.Free`.
