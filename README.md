# Grammar Normalization to Chomsky Normal Form (CNF)

## Course: Formal Languages & Finite Automata

### Author: Cvasiuc Dmitrii

---

## Overview

This project implements a **grammar normalization** algorithm that converts a given context-free grammar (CFG) into **Chomsky Normal Form (CNF)**. CNF is a restricted form of CFG where all production rules are either of the form:
- `A → BC` (two non-terminals), or
- `A → a` (a single terminal).

The implementation follows a systematic approach to transform any valid CFG into CNF through a series of well-defined steps.

---

## Theory Behind Chomsky Normal Form

**Chomsky Normal Form (CNF)** is a way to structure context-free grammars to simplify parsing and analysis. The key properties are:

1. All rules are in one of the two forms mentioned above.
2. The grammar doesn't contain ε-productions (except possibly for the start symbol if ε is in the language).
3. No unit productions (A → B).
4. All symbols are accessible and productive.

The conversion process involves:
1. **ε-production elimination**: Removing productions that derive the empty string.
2. **Unit production elimination**: Removing rules of the form A → B.
3. **Inaccessible symbol elimination**: Removing symbols that cannot be reached from the start symbol.
4. **Non-productive symbol elimination**: Removing symbols that cannot derive terminal strings.
5. **Rule normalization**: Breaking down longer rules into CNF-compliant rules.

---

## Implementation Details

### Grammar Representation

The grammar is represented using four components:
- `VN`: Non-terminal symbols
- `VT`: Terminal symbols
- `S`: Start symbol
- `P`: Production rules

```python
class Grammar:
    def __init__(self, VN, VT, S, P):
        self.VN = VN    # Non-terminals
        self.VT = VT    # Terminals
        self.S = S      # Start symbol
        self.P = P      # Productions
```

---

### Key Transformation Steps

#### 1. Eliminating ε-Productions

```python
def _eliminate_epsilon_productions(self, vn, productions):
    # Identify nullable non-terminals
    nullable = set()
    while True:
        updated = {nt for nt in vn if nt not in nullable and nt in productions
                   and any(p == "ε" or all(s in nullable for s in p) for p in productions[nt])}
        if not updated: break
        nullable |= updated

    # Rebuild productions without ε
    for nt in vn:
        if nt in productions:
            new_prods = []
            for p in productions[nt]:
                if p != "ε":
                    self._add_all_combinations(p, nullable, new_prods)
            productions[nt] = list(set(new_prods))
```

**Key Features**:
- Identifies nullable symbols (those that can derive ε)
- Generates all possible combinations of productions without nullable symbols
- Removes ε-productions while preserving language (except ε itself)

#### 2. Eliminating Unit Productions

```python
def _eliminate_unit_productions(self, vn, productions):
    unit_pairs = {nt: {nt} for nt in vn}
    while True:
        updated = False
        for a in vn:
            for b in list(unit_pairs[a]):
                unit_prods = [p[0] for p in productions.get(b, []) if len(p) == 1 and p[0] in vn]
                for c in unit_prods:
                    if c not in unit_pairs[a]:
                        unit_pairs[a].add(c)
                        updated = True
        if not updated: break

    productions.update({
        nt: list({p for u in unit_pairs[nt] for p in productions.get(u, [])
                  if not (len(p) == 1 and p[0] in vn)})
        for nt in vn
    })
```

**Key Features**:
- Computes the transitive closure of unit productions
- Replaces chains like A → B → C with direct productions A → α where B → α
- Preserves language while simplifying grammar structure

---

### Example Transformation

**Original Grammar**:
```
Grammar {
  VN = ['S', 'A', 'B', 'C', 'D']
  VT = ['a', 'b']
  S = S
  P = {
    S → aB | DA
    A → a | BD | bDAB
    B → b | BA
    D → ε | BA
    C → BA
  }
}
```

**After ε-Elimination**:
- Nullable symbols: {'D'}
- Productions with D removed or combinations without D added

**After Unit Production Elimination**:
- Unit pairs identified and expanded
- Chains like S → A → a become S → a directly

**Final CNF Grammar**:
```
Grammar {
  VN = ['S', 'A', 'B', 'D', 'T1', 'T2', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8', 'V9', 'V10', 'V11']   
  VT = ['a', 'b']
  S = S
  P = {
    S → BA | DA | b | TV1 | a | BD | TV4 | TV6
    A → BA | b | TV7 | a | BD | TV10
    B → BA | b
    D → BA
    T1 → b
    T2 → a
    V1 → 1V2
    V2 → DV3
    V3 → AB
    V4 → 1V5
    V5 → AB
    V6 → 2B
    V7 → 1V8
    V8 → DV9
    V9 → AB
    V10 → 1V11
    V11 → AB
  }
}
```

---

## Usage Examples

### Basic Normalization

```python
grammar = Grammar(
    VN=['S', 'A', 'B', 'C', 'D'],
    VT=['a', 'b'],
    S='S',
    P={
        'S': ['aB', 'DA'],
        'A': ['a', 'BD', 'bDAB'],
        'B': ['b', 'BA'],
        'D': ['ε', 'BA'],
        'C': ['BA']
    }
)

normalizer = CNFNormalizer()
cnf_grammar = normalizer.normalize(grammar)
print(cnf_grammar)
```

### Testing with Different Grammars

The implementation works with any valid CFG, not just the example grammar:

```python
# Another grammar example
grammar2 = Grammar(
    VN=['S', 'X', 'Y'],
    VT=['0', '1'],
    S='S',
    P={
        'S': ['0X', '1Y', 'ε'],
        'X': ['1Y', '0'],
        'Y': ['0X', '1', 'ε']
    }
)

cnf_grammar2 = normalizer.normalize(grammar2)
```

---

## Conclusion

This implementation successfully converts context-free grammars to Chomsky Normal Form by applying theoretical concepts from formal language theory:

### Key Concepts Demonstrated

1. **ε-Production Elimination**
   - Identifies and removes empty productions while preserving language

2. **Unit Production Elimination**
   - Removes chain rules through transitive closure

3. **Symbol Accessibility**
   - Removes unreachable symbols from the start symbol

4. **Productivity Analysis**
   - Removes symbols that cannot derive terminal strings

5. **Rule Normalization**
   - Breaks down complex rules into CNF-compliant binary rules

### Challenges Encountered

- Handling multiple nullable symbols in productions required careful combination generation
- Managing the introduction of new variables during normalization while avoiding conflicts
- Ensuring completeness of unit production elimination through transitive closure

### Future Improvements

- **Optimization**: Reduce the number of new variables introduced
- **Error Handling**: Better reporting of invalid grammars
- **Visualization**: Add grammar visualization before/after normalization
- **Parser Integration**: Build a CYK parser that uses the CNF grammar

---

## References

1. [Wikipedia - Chomsky Normal Form](https://en.wikipedia.org/wiki/Chomsky_normal_form)
2. [Hopcroft, Motwani, Ullman - Introduction to Automata Theory](https://www.pearson.com/store/p/introduction-to-automata-theory-languages-and-computation/P100000912063/9781292039053)
3. [Sipser - Introduction to the Theory of Computation](https://www.cengage.com/c/introduction-to-the-theory-of-computation-3e-sipser/9781133187790/)

---

## Repository

🔗 [GitHub Repository](https://github.com/dmitrycvs/Chomsky-Normal-Form)
