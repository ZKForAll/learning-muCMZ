# Learning μCMZ

or μCMZ in layman terms...

Study notes on the cryptographic primitives underlying μCMZ
(Orrù 2024, IACR ePrint 2024/1552).

> **This file is the deliverable of the project.** Christiano writes it, and
> Claude writes in it only when explicitly asked. The design rationale lives in
> [`journal.md`](journal.md).

## 1. The prime-order group (O24 §3)

Everything in μCMZ sits on one object, a group 𝔾. Picture a fixed collection of
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

## 2. Hardness assumptions (O24 §3.1)

The security rests on problems that we believe are infeasible. An advantage
measures each one, a number for how well an attacker does.

### 2.1 Discrete logarithm (DL)

The generator g is public and so is the stepping rule. Given a random point X,
finding the step count x with x • g = X is infeasible once p is large. Forward,
from x to X, runs fast. Backward, from X to x, has no known shortcut beyond
trying counts one by one over a huge range.

### 2.2 Decisional Diffie–Hellman (DDH)

Pick secret counts a and b. From the points a • g and b • g, the combined point
(a·b) • g is the Diffie–Hellman value. DDH says that even after seeing a • g and
b • g you cannot tell the true combined point from a random point. You can
neither compute it nor recognize it.

### 2.3 Advantage

The advantage is the edge an attacker has over blind luck. For DL it is the
chance of returning the correct x, which sits near zero for a random guess. For
DDH the attacker answers a yes or no question, so a coin flip already wins half
the time, and the advantage is the gap between how often the attacker says "real"
in the two cases, which a coin flip drives to zero. An assumption holds when the
advantage stays negligible as p and λ grow (negligible means that as the sizes
grow the advantage drops to practically nothing, far too small for any real
attacker to exploit).

### 2.4 q-discrete logarithm (q-DL)

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

### 2.5 q-Decisional Diffie–Hellman Inversion (q-DDHI)

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
