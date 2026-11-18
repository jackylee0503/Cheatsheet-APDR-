# APDR C01A Quick Summary

## Boolean Algebra

- Boolean algebra: **Huntington-style axioms** -> distributive lattice -> ring algebra (Boolean algebra)
- Partial evaluation on bits
- Relationship with ring algebra
- Bit quantifiers

## NAND as a Complete Gate

- NAND is functionally complete.
- Reasons:
  1. NAND, NOR, and the other basic logic operators can be derived from NAND.
  2. It can be used to reverse-engineer a chip.
- From the perspective of computational complexity, this is interesting:
  - It relates to **NP-complete** problems.
  - Therefore, heuristic approaches are needed.

## Representing and Minimizing Boolean Functions

1. Use a truth table.
2. Simplify the expression.

### Common simplification forms

- DNF (Disjunctive Normal Form)
- CNF (Conjunctive Normal Form)
- Chad's method

**Using 1's complement for shortcut simplification**

DNF and CNF minimization is not always easy. In practice, it may be faster to use software or visually inspect the truth table.

> The rest of the material on **Moebius reduction** is not clear to me yet, so it could not be organized here.

## Hazard

Example:

```text
xy + x'z + yz = xy + x'z
```

Consider a transition where:

- `x: 1 -> 0`
- `y` and `z` remain `1`

In this case, a temporary problem occurs.
