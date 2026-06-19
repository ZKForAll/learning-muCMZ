# Learning μCMZ

or μCMZ in layman terms...

Study notes on the cryptographic primitives underlying μCMZ
(Orrù 2024, IACR ePrint 2024/1552).

> **This file is the deliverable of the project.** It is written by Christiano,
> or by Claude only when explicitly asked. The design rationale lives in
> [`journal.md`](journal.md).

## 1. The prime-order group (O24 §3)

Everything in μCMZ sits on one object, a group 𝔾. Picture a fixed collection of
points with a single operation that combines two points into a third, written as
addition. One point, 0, does nothing when added, and one point, G, is the chosen
starting point called the generator. Adding G to itself x times gives a point
written x • G. The setup step GrGen hands you this object together with the
number of points p and the generator G, packaged as Γ = (𝔾, p, G).

The number of points p is a prime, which has three consequences. Every point
other than 0 also works as a generator, so the group hides no smaller groups
inside it. Each point is reached by exactly one step count, so x • G for
x = 0, 1, …, p − 1 lists every point once. And the step counts behave like
ordinary arithmetic with addition, subtraction, multiplication, and division,
because a prime p makes the counts mod p, written ℤ_p, a field.

The security comes from a one-way effect. Going forward from a count x to the
point x • G is fast. Going backward from a point X to the count that produced it
is infeasible once p is large. That backward problem is the discrete logarithm.

In Lean we do not run GrGen. We simply assume such a group is given, by stating
the following.

```lean
variable (p : ℕ) [Fact p.Prime] {G : Type*} [AddCommGroup G] [Module (ZMod p) G] (g : G)
```

In words, p is a prime, G is a group written additively, the counts ℤ_p act on it
by repeated addition, and g is the chosen generator. Two extra facts, that the
group is cyclic and has exactly p points, are added only when a proof needs them.
The hardness of the discrete logarithm is not stated here, since it is a separate
assumption about attackers.

For experiments we use a small concrete group, a Schnorr group, built inside the
whole numbers mod a prime q, with toy values p = 11, q = 23, and generator 4. It
has exactly eleven points and runs in the computer. Real systems use elliptic
curves such as Ristretto255, which are smaller and faster at real sizes but much
harder to build in Lean. The code we write behaves the same over either.

## 2. Hardness assumptions (O24 §3.1)

The security rests on problems believed to be infeasible. Each is measured by an
advantage, a number for how well an attacker does.

### 2.1 Discrete logarithm (DL)

The generator g is public and so is the stepping rule. Given a random point X,
finding the step count x with x • g = X is infeasible once p is large. Forward,
from x to X, is fast. Backward, from X to x, has no known shortcut beyond trying
counts one by one over a huge range.

### 2.2 Decisional Diffie–Hellman (DDH)

Pick secret counts a and b. From the points a • g and b • g, the combined point
(a·b) • g is the Diffie–Hellman value. DDH says that even after seeing a • g and
b • g you cannot tell the true combined point from a random point. You can
neither compute it nor recognize it.

### 2.3 Advantage

The advantage is the edge an attacker has over blind luck. For DL it is the
chance of returning the correct x, which is near zero for a random guess. For DDH
the attacker answers a yes or no question, so a coin flip already wins half the
time, and the advantage is the gap between how often the attacker says "real" in
the two cases, which is zero for a coin flip. An assumption holds when the
advantage stays negligible as p and λ grow (negligible means that as the sizes
grow the advantage drops to practically nothing, far too small for any real
attacker to exploit).
