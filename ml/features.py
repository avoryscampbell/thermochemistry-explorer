# ml/features.py
from typing import Dict, List, Tuple
import numpy as np, re
from collections import Counter

_ELEMENT_RE = re.compile(r"([A-Z][a-z]?)(\d*)")
_COEF_RE = re.compile(r"^\s*(\(?[0-9./]+\)?)\s*(.*)$")

def _parse_coef_and_formula(part: str) -> tuple[float, str]:
    part = part.strip()
    m = _COEF_RE.match(part)
    if m:
        raw = m.group(1).strip()
        try:
            coef = float(eval(raw))  # supports 7/2 style
        except Exception:
            try:
                coef = float(raw)
            except Exception:
                coef = 1.0
        formula = m.group(2).strip()
    else:
        coef, formula = 1.0, part
    return coef, formula

def _element_counts(formula: str) -> Dict[str, float]:
    counts: Dict[str, float] = {}
    for elem, num in _ELEMENT_RE.findall(formula):
        n = float(num) if num else 1.0
        counts[elem] = counts.get(elem, 0.0) + n
    return counts

def _expand_side(side: str) -> Counter:
    total = Counter()
    for part in side.split("+"):
        if not part.strip(): 
            continue
        coef, formula = _parse_coef_and_formula(part)
        ec = _element_counts(formula)
        for k, v in ec.items():
            total[k] += coef * v
    return total

def featurize_reaction(reaction: str) -> Dict[str, float]:
    lhs, rhs = [s.strip() for s in reaction.split("->")]
    L, R = _expand_side(lhs), _expand_side(rhs)
    elems = sorted(set(L) | set(R))

    feats: Dict[str, float] = {}
    # Per-side totals
    for e in elems:
        feats[f"L_{e}"] = float(L.get(e, 0.0))
        feats[f"R_{e}"] = float(R.get(e, 0.0))
        feats[f"d_{e}"] = float(R.get(e, 0.0) - L.get(e, 0.0))

    # Simple string/shape features
    feats["num_elems"] = float(len(elems))
    feats["n_reactants"] = float(len([p for p in lhs.split("+") if p.strip()]))
    feats["n_products"]  = float(len([p for p in rhs.split("+") if p.strip()]))
    feats["len_lhs"] = float(len(lhs)); feats["len_rhs"] = float(len(rhs))
    feats["contains_O"] = 1.0 if "O" in elems else 0.0
    feats["contains_N"] = 1.0 if "N" in elems else 0.0
    feats["contains_C"] = 1.0 if "C" in elems else 0.0
    feats["contains_H"] = 1.0 if "H" in elems else 0.0
    return feats

def vectorize(reactions: List[str]) -> Tuple[np.ndarray, List[str]]:
    dicts = [featurize_reaction(r) for r in reactions]
    keys = sorted(set().union(*[d.keys() for d in dicts]))
    X = np.array([[d.get(k, 0.0) for k in keys] for d in dicts], dtype=float)
    return X, keys

