# Learning μCMZ

or μCMZ in layman terms...

Study notes on the cryptographic primitives underlying μCMZ
(Orrù 2024, IACR ePrint 2024/1552).

> **This file is the deliverable of the project.** Christiano writes it, and
> Claude writes in it only when explicitly asked. The design rationale lives in
> [`journal.md`](journal.md).

## 1. Preliminaries

Background that μCMZ takes for granted.

### 1.1 Modular arithmetic

Crypto needs operations that run easily one way but resist undoing, and modular
arithmetic supplies that along with a few other properties.

It makes operations easy forward and hard backward. Modular arithmetic wraps
numbers around a fixed size, like a clock that resets after 12. Stepping forward
on the clock runs fast, but the wrap-around hides how many steps you took, so the
final position tells you little about the count. The hard problems crypto rests
on, the discrete logarithm and factoring, only become hard in this wrap-around
setting.

It keeps numbers finite and exact. Every value stays in the range 0 to n − 1, so
a computer stores and computes it exactly and fast, with no rounding and no
values that grow without bound.

It gives a clean number system. Working mod a prime p lets you add, subtract,
multiply, and divide, the same four operations you expect from ordinary numbers,
and protocols lean on this, for example when a proof divides by a challenge.
Working mod a composite gives a different structure tied to factoring.

It spreads values evenly. Residues mod p come out uniform, so a random count
yields a result that looks uniform, and this lets a sender hide a value by adding
a random one, which underlies commitments and blinding.

### 1.2 Groups

A group gives crypto the smallest structure it needs, one operation that you can
repeat and undo.

A group packages one operation with the rules crypto relies on. You combine any
two elements and stay inside the set, the operation has an identity that does
nothing, and every element has an inverse that undoes it. That is enough to
define stepping, the repeated operation, and to reverse it.

Repeating the operation builds the one-way function. Adding g to itself x times
gives x•g, which runs fast, but recovering x stays infeasible, the discrete
logarithm. Groups make this stepping well-defined and quick even for huge counts,
through doubling tricks.

The operation also lets you compute on hidden values. Combining a•g and b•g gives
(a+b)•g, so you add secret counts while they stay hidden in the exponent. This
homomorphism powers key exchange, commitments, and encryption.

An abstract group keeps protocols portable. You state a scheme and its security
once over any group where the discrete logarithm stays hard, then plug in a
concrete instance, a mod-p group or an elliptic curve, without touching the
protocol or its proofs. We do exactly this below, stating the primitives over an
abstract prime-order group and instantiating it with a Schnorr group.

### 1.3 On hardness assumptions

A hardness assumption is a conjecture. A designer picks a problem
that runs easily one way and resists undoing, like the discrete logarithm or
factoring, and conjectures that no efficient algorithm solves it. Nobody proves
this, because a proof would have to rule out every possible fast algorithm.

Attacks test the assumption rather than create it. Cryptanalysts attack the
problem for years, the best algorithm they find fixes the key sizes, and long
survival builds confidence. A successful attack weakens or refutes the assumption
and forces larger parameters or a new design. Cheon's attack is one such case
([Cheon, EUROCRYPT 2006](https://www.iacr.org/archive/eurocrypt2006/40040001/40040001.pdf)),
which weakened the q-type assumptions and explains why we keep q small.

New schemes introduce new assumptions with extra structure, like DDH, q-DL, or
gap-DL. A designer states the weakest assumption the proof needs, and a security
proof reduces breaking the scheme to solving that problem.

## 2. The prime-order group (O24 §3)

Everything in μCMZ builds on one object, a group 𝔾. Picture a fixed collection of
points with one operation that combines two points into a third. We write this
operation as addition. One point, 0, does nothing when we add it, and another
point, G, serves as the starting point, the generator. Adding G to itself x times
gives a point we write x • G. The setup step GrGen hands you this object together
with the number of points p and the generator G, and packages them as
Γ = (𝔾, p, G).

The number of points p is a prime, which has three consequences. Every point
other than 0 also works as a generator, so the group hides no smaller groups
inside it. Exactly one step count reaches each point, so x • G for x = 0, 1, …,
p − 1 lists every point once. And the step counts behave like ordinary arithmetic
with addition, subtraction, multiplication, and division, because a prime p makes
the counts mod p, which we write $ℤ_p$, a field.

The security comes from a one-way effect. Going forward from a count x to the
point x • G is fast. Going backward from a point X to the count that produced it
is infeasible once p is large. That backward problem is the discrete logarithm.

In Lean we do not run GrGen. We assume the group exists and state the following.

```lean
variable (p : ℕ) [Fact p.Prime] {G : Type*} [AddCommGroup G] [Module (ZMod p) G] (g : G)
```

In words, p is a prime, G is a group we write additively, the counts ℤ_p act on
it by repeated addition, and g is the generator. We add two extra facts, that the
group is cyclic and has exactly p points, only when a proof needs them. We do not
state the hardness of the discrete logarithm here, because it is a separate
assumption about attackers.

For experiments we use a small concrete group, a Schnorr group, which we build
inside the whole numbers mod a prime q, with toy values p = 11, q = 23, and
generator 4. It has exactly eleven points and runs in the computer. Real systems
use elliptic curves such as Ristretto255, which run smaller and faster at real
sizes but cost much more to build in Lean. The code we write behaves the same
over either.

## 3. Hardness assumptions (O24 §3.1)

The security rests on problems that we believe are infeasible. An advantage
measures each one, a number for how well an attacker does.

### 3.1 Discrete logarithm (DL)

The generator g is public and so is the stepping rule. Given a random point X,
finding the step count x with x • g = X is infeasible once p is large. Forward,
from x to X, runs fast. Backward, from X to x, has no known shortcut beyond
trying counts one by one over a huge range.

### 3.2 Decisional Diffie–Hellman (DDH)

Pick secret counts a and b. From the points a • g and b • g, the combined point
(a·b) • g is the Diffie–Hellman value. DDH says that even after seeing a • g and
b • g you cannot tell the true combined point from a random point. You can
neither compute it nor recognize it.

### 3.3 Advantage

The advantage measures how much better an attacker does than guessing. For DL it
is the probability of returning the correct x, which stays near zero for a random
guess. For DDH the attacker answers a yes or no question, so guessing already
succeeds half the time, and the advantage is the gap between how often the
attacker outputs "real" in the two cases, which equals zero for a guess. An
assumption holds when the
advantage stays negligible as p and λ grow (negligible means that as the sizes
grow the advantage drops to practically nothing, far too small for any real
attacker to exploit).

### 3.4 q-discrete logarithm (q-DL)

q-DL strengthens DL by handing the attacker a sequence of powers of the secret.
Someone picks a secret count x and shows the attacker g, x•g, x²•g, up to
$x^q•g$, the generator stepped by x, by x squared, and so on to the q-th power.
Even with this sequence, recovering x stays infeasible. The number q counts how
many powers the attacker gets, and its advantage is
$Adv^{q\mathtt{-}dl}_{GrGen,A}(λ)$.

The extra powers help an attacker. In plain DL there is one clue, x•g, and the
best general method tries counts until one matches, about $\sqrt{p}$ attempts.
The powers all come from the same x, so they are related, and that relatedness is
leverage a single point does not give. The concrete payoff is Cheon's attack
([Cheon, EUROCRYPT 2006](https://www.iacr.org/archive/eurocrypt2006/40040001/40040001.pdf)).
When q divides p − 1, having x•g together with $x^q•g$ lets the attacker split
the one big search into two smaller ones and recover x in about $\sqrt{\frac{p}{q}}$
steps instead of $\sqrt{p}$, roughly $\sqrt{q}$ times faster, a loss of about half
the bits of q. So a larger q makes the attacker's job easier and the assumption
weaker, which is why we keep q as small as the application allows.

### 3.5 q-Decisional Diffie–Hellman Inversion (q-DDHI)

q-DDHI is the decision counterpart of q-DL. Someone picks a secret count x and
shows the attacker the sequence x•g, x²•g, up to $x^q•g$. They then show one
extra point, either the inverse point (1/x)•g, where 1/x is the count that undoes
x modulo p, or a fresh random point Z. q-DDHI says the attacker cannot tell which
point they got. The inverse point looks the same as a random point, even with the
whole sequence in hand. Its advantage is $Adv^{q\mathtt{-}ddhi}_{GrGen,A}(λ)$.

q-DL and q-DDHI differ in the task. q-DL asks the attacker to compute the secret
x, a search problem. q-DDHI asks the attacker to recognize the inverse point, a
yes or no problem. Recognition can stay hard even when computation does not help.
This assumption supports a pseudorandom function that rate-limiting and
pseudonyms use (O24 §8), where the outputs take the form of such inverse points
and must look random.

### 3.6 Algebraic group model (AGM)

The AGM is a proof model, not a hardness assumption
([Fuchsbauer–Kiltz–Loss, CRYPTO 2018](https://link.springer.com/chapter/10.1007/978-3-319-96881-0_2)).
In the AGM every attacker is algebraic, meaning that whenever it outputs a group
point X, it also outputs a representation of X as a combination of the points
$Z_1, \dots, Z_n$ it has received, with coefficients $\zeta_1, \dots, \zeta_n$
such that $X = \sum_{i=1}^{n} \zeta_i Z_i$.

A real attacker produces new points only by adding and scaling the points it
holds, so it can always supply the representation. A proof then reads the
coefficients and reduces security to the discrete logarithm. The AGM gives the
prover more than the standard model, where the attacker supplies no
representation, and less than the generic group model, where the attacker cannot
use the group's representation at all. O24 proves μCMZ and μBBS in the AGM, so the
guarantees cover algebraic attackers.

### 3.7 Generic group model (GGM)

The GGM is a proof model, not a hardness assumption
([Shoup, EUROCRYPT 1997](https://link.springer.com/chapter/10.1007/3-540-69053-0_18)).
The attacker never sees the real group elements. It receives only random labels
for them and combines them through an oracle that performs the group operation,
handing the oracle two labels and receiving the label of their sum. The labels
carry no structure, so the attacker cannot use the representation of the group.

This restriction lets one prove lower bounds. Shoup showed that any generic
attacker needs about $\sqrt{p}$ group operations to compute a discrete logarithm,
which justifies key sizes. The GGM forbids using the representation, while the AGM
allows it but requires the attacker to output it, so the GGM is the more
idealized model and its proofs can miss attacks that exploit the real encoding,
such as index calculus on multiplicative groups.

## 4. Algebraic message authentication codes (O24 §3.2)

A message authentication code (MAC) authenticates a message. The same secret key
produces the MAC and verifies it. A signature instead verifies with a public key,
and only its private key produces it. A keyed-verification credential makes the
issuer and the verifier the same party, so a MAC suffices and the scheme avoids
pairings. "Algebraic" means the construction uses only group and scalar
operations, so the user can later prove possession of a MAC in zero knowledge.

Definition 3.1 gives a MAC as four algorithms, MAC = (S, K, M, V). Setup
S($1^λ$, n) fixes the security level and the number of attributes n and outputs
public parameters. Key generation K produces a secret key sk and public
parameters pp, and the issuer holds sk. The MAC algorithm M(sk, $\vec{m}$) takes
the secret key and attributes $\vec{m} = (m_1, \dots, m_n)$ and outputs a tag σ,
the credential on those attributes. Verification V(sk, $\vec{m}$, σ) returns 1
when the tag is valid and needs sk, which is the keyed part.

A MAC must satisfy correctness and unforgeability. Correctness means an honestly
produced tag always verifies. Unforgeability means no efficient attacker produces
a valid tag on a fresh attribute list. The paper uses UF-CMVA, unforgeability
under a chosen-message-and-verification attack (Figure 5), where the attacker
calls a Sign oracle for tags on chosen attributes and a Verify oracle to test
tags. The Verify oracle grants real power, because the secret key both signs and
checks. UF-CMVA is a notion, not a proof model, and a proof reaches it for a
concrete scheme in the generic or algebraic group model.

Remark 3.2 notes that algebraic MACs are randomized. You can de-randomize them in
the random oracle model by deriving the randomness from H($\vec{m}$), so the same
attributes always yield the same tag.

We represent each randomized algorithm in Lean as a program in a free monad over
a polynomial functor, then give it meaning as a probability distribution.
Explaining the choice takes a few steps, the general notion of a monad, the free
monad that turns an operation signature into one, the probability mass functions
that give it meaning, what each of the two solves, and how VCVio packages both as
`OracleComp`.

### 4.1 Monads

A monad describes computations that carry an effect, here randomness, while still
composing cleanly. In Lean a monad is a type constructor `m` that turns a result
type `α` into a computation type `m α`. A value of `m α` is a computation that
produces an `α`, possibly with the effect attached.

The interface has two operations.

- `pure : α → m α` wraps a plain value as a computation that adds no effect and
  returns the value.
- `bind : m α → (α → m β) → m β` runs a computation, takes its result, and feeds
  it to the next step, producing the combined computation. Lean writes `bind` as
  `>>=` and offers `do` notation for chains of binds.

These operations obey three laws, left identity, right identity, and
associativity, which make `pure` a neutral step and `bind` associative, so you
chain steps without surprises. The paper's randomized assignment, crs ← S(…), is
one `bind` step, and the arrow is the `bind`.

### 4.2 Free monads over polynomial functors

A plain monad fixes both the syntax and the meaning of its computations at once.
A free monad keeps only the syntax. It turns a signature of operations into a
monad mechanically, so a value is a tree of operations with no meaning yet
attached. A leaf holds a result, and each inner node names one operation and
branches into the continuations that consume the operation's result. The meaning
comes later, from a separate handler that interprets each operation.

A polynomial functor supplies the signature. In Mathlib a `PFunctor` is a set of
shapes `A` together with a family of positions `B a` for each shape `a`. Read a
shape as the name of an operation and its positions as the results that operation
can return. VCVio builds the free monad on such a functor as the inductive type

```
inductive FreeM (P : PFunctor.{uA, uB}) : Type v → Type (max uA uB v)
  | pure (x : α)                           -- a result, no operation
  | roll (a : P.A) (k : P.B a → FreeM P α) -- run operation `a`, continue with `k`
```

from `ToMathlib.PFunctor.Free`. A program in `FreeM P α` is a finite tree of
operations whose leaves carry an `α`. The monad's `bind` grafts the next program
onto every leaf, and `pure` is a bare leaf, so `do` notation builds these trees.

```lean
open PFunctor

#check @FreeM        -- FreeM : (P : PFunctor) → Type v → Type (max uA uB v)

-- a free-monad program over any signature `Sig`, built with `do`
example (Sig : PFunctor) (p : FreeM Sig ℕ) : FreeM Sig ℕ := do
  let x ← p
  pure (x + 1)
```

The codomain rises one universe. A node stores a function out of the positions
`P.B a`, a type in `Type uB`, into the tree, and the leaves carry a result in
`Type v`, so the tree cannot stay at `Type v`. It lands at `Type (max uA uB v)`,
the universe bump in the signature above. Mathlib keeps the shape universe `uA`
and the position universe `uB` separate, so both appear in the bump. The bump is
what lets `FreeM P` still count as a `Monad`, since Lean's universe polymorphism
accepts the raised codomain.

### 4.3 Probabilistic monads

The free monad gives the syntax. A probability mass function gives one meaning. A
probability mass function (PMF) assigns each value of a type a probability, with
the probabilities summing to 1 over a countable support. Mathlib defines `PMF α`
as a function `α → ℝ≥0∞` with a proof that the values sum to 1. `PMF` is itself a
lawful monad, where `pure x` is the point mass at `x` and `bind` draws from the
first distribution and feeds the draw to the second.

A plain monad sequences operations but cannot sample on its own. The signature
`Sig` therefore carries a sampling operation, for example a uniform draw over a
finite type. A handler ⟦·⟧ sends a program in `FreeM Sig α` to the `PMF α` of its
results. It reads `pure x` as the point mass at `x` and each sampling node as the
matching draw, then composes. The handler is a monad morphism, so it respects
`pure` and `bind` and the distribution of a sequence matches the sequence of
distributions.

### 4.4 What FreeM and PMF each solve

`FreeM` and `PMF` sit at different layers and solve different problems, so the
scheme uses one of them as its definition and reaches the other only for meaning.

`FreeM Sig` is the definition layer. It records an algorithm as syntax, the
operations it performs and their order, and defers their meaning to a handler. It
solves two problems. One program carries several meanings, so the same `M` serves
correctness under one handler and the UF-CMVA game under another. And the
signature `Sig` can hold the oracle operations `Sign` and `Verify` together with
the state they need, the query set Qrs that the game reads. A definition given
straight as a distribution keeps none of this structure, so it cannot host the
oracle layer.

`PMF` is the semantics layer. It is a distribution, the object that carries
probabilities. It solves the quantitative problem. Correctness says a tag
verifies with probability 1, and the advantage is a probability, and both are
statements about a distribution. A `FreeM` program holds no probabilities, since
a sampling node is only a label, so you cannot phrase either claim until you
interpret the program into a `PMF`.

The two are not competing definitions. The MAC is defined once as a free-monad
program, and `PMF` appears downstream as the codomain of a handler ⟦·⟧ that
interprets it, computed when a probability is needed. The handler exists only
when the signature says how each operation becomes a distribution. A bare
`FreeM Sig` carries no such data, so §4.5 uses VCVio's `OracleComp`, the free
monad over an oracle signature that supplies it. The handler is a monad morphism,
so reading the distribution commutes with sequencing.

|        | `FreeM Sig`                                                  | `PMF`                                         |
| ------ | -------------------------------------------------------------- | ----------------------------------------------- |
| Layer  | syntax, the definition                                         | semantics, the meaning                          |
| Holds  | operations and their order                                     | a distribution over results                     |
| Solves | many interpretations of one program; hosts the oracles and Qrs | probabilities for correctness and the advantage |
| Lacks  | any probability                                                | the program structure, meaning fixed early      |

### 4.5 OracleComp in VCVio

VCVio packages this layering, so we reuse it rather than build it. `OracleComp spec α`
is the free monad over an oracle signature `spec`, an `OracleSpec`. It is the
syntax layer, `FreeM` specialized to oracle queries. The randomized algorithms
become `OracleComp` programs, and sampling is the uniform-selection oracle, so a
computation whose only oracle is sampling has type `ProbComp = OracleComp unifSpec`.

`evalDist : OracleComp spec α → SPMF α` is the probability handler. `SPMF` is
`OptionT PMF`, a sub-probability distribution whose mass can fall below 1 to
record a run that fails. It sends each query to the uniform distribution over its
range. The functions `probOutput` and `probEvent` read the probability of an
output or an event off that distribution. The game handlers come from
`SimSemantics`, where `simulateQ` runs a program under a `QueryImpl` that answers
each query, and from `QueryTracking`, which logs the queries, the Qrs the game
accumulates.

```lean
open OracleComp

#check @OracleComp   -- OracleSpec ι → Type → Type _   (the program, a free monad)
#check @ProbComp     -- OracleComp unifSpec            (only a sampling oracle)
#check @evalDist     -- OracleComp spec α → SPMF α     (the probability handler)
#check @probEvent    -- m α → (α → Prop) → ℝ≥0∞        (probability of an event)
```

`OracleComp` does not state correctness. It is the program type. Correctness is a
proposition we write with `evalDist` and `probEvent`, that the honest run accepts
with probability 1, and unforgeability is the advantage read from the game's
distribution. VCVio supplies the machinery to state and prove both, and the
statements stay ours.

### 4.6 The MAC structure in Lean

The four algorithms become the fields of a Lean structure. We write two versions.
The first uses `PMF` directly and reaches correctness but not the game. The second
uses `OracleComp` and reaches both.

#### 4.6.1 A first specification with PMF

The randomized algorithms `S`, `K`, and `M` return a `PMF`, and `V` returns
`Bool`.

```lean
namespace WithPMF

structure MAC (𝕄 : Type) (n : ℕ) (crs sk pp σ : Type) where
  /-- setup `crs ← S(1^λ, n)`; `secParam` is the security parameter λ -/
  S : (secParam : ℕ) → PMF crs
  /-- key generation `(sk, pp) ← K(crs)` -/
  K : crs → PMF (sk × pp)
  /-- the MAC `σ ← M(sk, m)` over attributes `m : Fin n → 𝕄` -/
  M : sk → (Fin n → 𝕄) → PMF σ
  /-- deterministic verification `0/1 := V(sk, m, σ)` -/
  V : sk → (Fin n → 𝕄) → σ → Bool

end WithPMF
```

This states correctness directly, since each algorithm is already a distribution,
so binding `S`, `K`, and `M` and reading the probability that `V` accepts gives
the correctness statement. It cannot state UF-CMVA, for three reasons.

- `M` returns a finished distribution. The `Sign` oracle has to run `M` and also
  record the queried message into Qrs, but a `PMF σ` exposes only the output
  distribution, not the steps, so there is no seam to insert the bookkeeping.
- The signature has no place for the `Sign` and `Verify` oracles or the mutable
  query set Qrs. A `PMF` sequences randomness and nothing else.
- The adversary needs adaptive oracle access, calling `Sign` and `Verify` and
  branching on the answers. A `PMF` value is non-interactive.

So the `PMF` specification reaches correctness but stops short of unforgeability,
which is the property the paper proves.

#### 4.6.2 The specification with OracleSpec

Replacing `PMF` with `OracleComp spec`, a program in the free monad over an oracle
signature `spec : OracleSpec ι`, keeps correctness and adds the game.

```lean
open OracleComp

structure MAC (𝕄 : Type) (n : ℕ) {ι : Type} (spec : OracleSpec ι)
    (crs sk pp σ : Type) where
  /-- setup `crs ← S(1^λ, n)`; `secParam` is the security parameter λ -/
  S : (secParam : ℕ) → OracleComp spec crs
  /-- key generation `(sk, pp) ← K(crs)` -/
  K : crs → OracleComp spec (sk × pp)
  /-- the MAC `σ ← M(sk, m)` over attributes `m : Fin n → 𝕄` -/
  M : sk → (Fin n → 𝕄) → OracleComp spec σ
  /-- deterministic verification `0/1 := V(sk, m, σ)` -/
  V : sk → (Fin n → 𝕄) → σ → Bool
```

Each problem of the `PMF` version is solved.

- `M` is now a program, the syntax of its steps, not a finished distribution. The
  `Sign` oracle runs the same program under a handler that records the message
  into Qrs, so the seam exists.
- The oracles live in `spec`. The plain MAC takes `spec = unifSpec`, where the
  only oracle is uniform sampling. The game extends `spec` with `Sign` and
  `Verify`, and H (Remark 3.2) extends it too.
- The adversary is itself an `OracleComp` program that queries `spec` and branches
  on the answers, so adaptive oracle access is expressible.
- Correctness survives the change. `evalDist : OracleComp spec α → SPMF α` recovers
  the distribution, so correctness interprets `S`, `K`, and `M` under `evalDist`
  and checks that `V` accepts with probability 1, exactly as the `PMF` version did.

The message family `𝕄` and the attribute count `n` are parameters, so one `n`
serves the whole scheme and `M` and `V` take exactly `n` attributes, a length-`n`
vector `Fin n → 𝕄`, which is $\mathbb{M}^n$. The carriers `crs`, `sk`, `pp`, `σ`
are parameters too, so each concrete scheme supplies its own, and `K` returns a
program producing the pair `(sk, pp)`. Correctness and UF-CMVA unforgeability come
later as predicates over a `MAC`, not as fields.

One simplification remains, shared by both versions. `S` takes only the security
parameter, while the paper writes `S(1^λ, n)`. Lifting `n` to a parameter keeps a
single consistent `n` by construction, at the cost of dropping `n` from the
signature of `S`.

### 4.7 Correctness (work in progress)

Correctness is the first property stated over a `MAC`. The honest run binds `S`,
`K`, and `M` and returns the verification bit, and correctness says that bit is
`true` with probability 1, for every security parameter and attribute vector.
Reading "probability 1" needs the spec to admit a distribution semantics, the
`HasEvalSPMF (OracleComp spec)` instance, since the probability is read off
`evalDist`.

```lean
open OracleComp

/-- one honest execution: generate keys, MAC `m`, return the verification bit -/
def honestRun {𝕄 : Type} {n : ℕ} {ι : Type} {spec : OracleSpec ι}
    {crs sk pp σ : Type} (mac : MAC 𝕄 n spec crs sk pp σ)
    (secParam : ℕ) (m : Fin n → 𝕄) : OracleComp spec Bool := do
  let crs      ← mac.S secParam
  let ⟨sk, pp⟩ ← mac.K crs
  let σ        ← mac.M sk m
  pure (mac.V sk m σ)

/-- O24 §3.2: an honestly produced tag always verifies -/
def Correct {𝕄 : Type} {n : ℕ} {ι : Type} {spec : OracleSpec ι}
    {crs sk pp σ : Type} [HasEvalSPMF (OracleComp spec)]
    (mac : MAC 𝕄 n spec crs sk pp σ) : Prop :=
  ∀ secParam (m : Fin n → 𝕄), Pr[= true | honestRun mac secParam m] = 1
```

`Correct` is a `def` returning `Prop`, the notion, not a theorem. A degenerate
`mac` whose `V` rejects is a valid inhabitant of the structure, and `Correct` is
simply `False` for it. A concrete construction discharges correctness as a
separate theorem, `theorem macGGM_correct : Correct macGGM`.
