#!/usr/bin/env python3
"""
Fetch thermochemical species data from the NIST Chemistry WebBook (HTML pages),
compute reaction ΔH°, ΔS°, and ΔG° at 298.15 K, and export training CSVs.

Outputs:
- data/processed/delta_g.csv  (reaction, delta_g)
- data/processed/spont.csv    (reaction, label)
- data/processed/reaction_thermo.csv (reaction, delta_h, delta_s, delta_g)
- data/raw/nist_species_cache.json   (cache of species properties)

Notes:
- NIST WebBook does not provide a stable JSON API; we parse HTML and do our best
  to find the 298 K gas-phase "Standard enthalpy of formation (ΔfH°)" and
  "Standard molar entropy (S°)". Not all species will have both values.
- Units: ΔfH° in kJ/mol; S° in J/(mol·K). We convert S° to kJ/(mol·K).
- Reaction ΔH°(rxn) = Σ ν_i ΔfH°(products) − Σ ν_j ΔfH°(reactants)
  Reaction ΔS°(rxn) = Σ ν_i S°(products)   − Σ ν_j S°(reactants)
  Reaction ΔG°(rxn) = ΔH°(rxn) − T * ΔS°(rxn), T=298.15 K

Usage:
    python scripts/fetch_nist_data.py --reactions-file data/processed/reactions.txt
    # reactions.txt: one reaction per line, e.g.
    # 2H2 + O2 -> 2H2O
    # C + O2 -> CO2
    #
    # Or use built-in defaults with --use-defaults
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
from pathlib import Path
from typing import Dict, Tuple, List

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://webbook.nist.gov/cgi/cbook.cgi"
T_REF = 298.15  # K

# ----------------------------
# Parsing chemistry strings
# ----------------------------

COEF_RE = re.compile(r"^\s*(\(?[0-9./]+\)?)\s*(.*)$")
ELEMENT_RE = re.compile(r"([A-Z][a-z]?)(\d*)")

def parse_coef_and_formula(part: str) -> tuple[float, str]:
    part = part.strip()
    m = COEF_RE.match(part)
    if m:
        raw = m.group(1).strip()
        try:
            coef = float(eval(raw))  # supports 7/2
        except Exception:
            try:
                coef = float(raw)
            except Exception:
                coef = 1.0
        formula = m.group(2).strip()
    else:
        coef, formula = 1.0, part
    # remove parentheses around formula (if any)
    formula = formula.strip()
    if formula.startswith("(") and formula.endswith(")"):
        formula = formula[1:-1].strip()
    # remove state symbols if present (e.g., H2O(g))
    formula = re.sub(r"\((g|l|s|aq)\)$", "", formula).strip()
    return coef, formula

def parse_side(side: str) -> Dict[str, float]:
    total: Dict[str, float] = {}
    for part in side.split("+"):
        if not part.strip():
            continue
        coef, formula = parse_coef_and_formula(part)
        total[formula] = total.get(formula, 0.0) + coef
    return total

def parse_reaction(reaction: str) -> tuple[Dict[str, float], Dict[str, float]]:
    if "->" not in reaction:
        raise ValueError(f"Reaction missing '->': {reaction}")
    lhs, rhs = [s.strip() for s in reaction.split("->", 1)]
    return parse_side(lhs), parse_side(rhs)

# ----------------------------
# NIST fetch + HTML parse
# ----------------------------

def fetch_species_page(formula: str) -> str:
    """Fetch NIST WebBook page HTML for a chemical formula (SI units).
    Note: multiple isomers may exist; we fetch the Formula landing page."""
    params = {"Formula": formula, "Units": "SI"}
    r = requests.get(BASE, params=params, timeout=20)
    r.raise_for_status()
    return r.text

def find_first_species_url(html: str) -> str | None:
    """On a Formula landing page, find the first species detail link."""
    soup = BeautifulSoup(html, "html.parser")
    # Look for links like cbook.cgi?ID=... or cbook.cgi?Name=...
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/cgi/cbook.cgi?ID=") or href.startswith("/cgi/cbook.cgi?Name="):
            # Prefer Thermochemistry data pages
            if "Units=SI" not in href:
                href += "&Units=SI"
            # Build absolute URL
            if href.startswith("/"):
                return "https://webbook.nist.gov" + href
            return href
    return None

def fetch_species_detail(url: str) -> str:
    r = requests.get(url, timeout=20)
    r.raise_for_status()
    return r.text

def parse_species_thermo(html: str) -> tuple[float | None, float | None]:
    """Return (ΔfH°_298_K_kJ_per_mol, S°_298_K_kJ_per_mol_K) if found; else (None, None)."""
    soup = BeautifulSoup(html, "html.parser")

    def textnorm(s: str) -> str:
        return " ".join(s.split()).replace("\xa0", " ")

    delta_hf = None  # kJ/mol
    s_molar = None   # kJ/(mol·K)  NOTE: NIST S° is often J/(mol·K), convert /1000

    # Search all tables for rows that mention Standard enthalpy of formation or Standard molar entropy
    for table in soup.find_all("table"):
        for tr in table.find_all("tr"):
            tds = tr.find_all(["td", "th"])
            if not tds:
                continue
            row_text = textnorm(" ".join(td.get_text(" ", strip=True) for td in tds))
            # Heuristics for entries at 298 K
            if ("Standard enthalpy of formation" in row_text or "ΔfH°" in row_text) and "298" in row_text:
                # Find a number in kJ/mol
                m = re.search(r"([-+]?\d+(?:\.\d+)?)\s*kJ/mol", row_text)
                if m:
                    delta_hf = float(m.group(1))
            if ("Standard molar entropy" in row_text or "S°" in row_text) and "298" in row_text:
                # Could be J/mol·K or kJ/mol·K
                m_kj = re.search(r"([-+]?\d+(?:\.\d+)?)\s*kJ/(?:mol·K|mol K|molK)", row_text)
                m_j  = re.search(r"([-+]?\d+(?:\.\d+)?)\s*J/(?:mol·K|mol K|molK)", row_text)
                if m_kj:
                    s_molar = float(m_kj.group(1))
                elif m_j:
                    s_molar = float(m_j.group(1)) / 1000.0

    return delta_hf, s_molar

# ----------------------------
# Cache + property retrieval
# ----------------------------

def load_cache(path: Path) -> Dict[str, dict]:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            return {}
    return {}

def save_cache(path: Path, cache: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2))

def get_species_thermo(formula: str, cache: dict) -> tuple[float | None, float | None]:
    """Return (ΔfH°_kJ/mol, S°_kJ/mol/K). Cache results."""
    key = formula.strip()
    if key in cache:
        rec = cache[key]
        return rec.get("delta_hf_kj_per_mol"), rec.get("s_kj_per_mol_k")

    # Fetch formula page, then first species detail, then parse
    try:
        html = fetch_species_page(formula)
        detail_url = find_first_species_url(html)
        if not detail_url:
            print(f"[warn] No species detail URL for {formula}")
            cache[key] = {"delta_hf_kj_per_mol": None, "s_kj_per_mol_k": None}
            return None, None
        detail_html = fetch_species_detail(detail_url)
        dhf, s = parse_species_thermo(detail_html)
    except Exception as e:
        print(f"[warn] Fetch/parse failed for {formula}: {e}")
        dhf, s = None, None

    cache[key] = {"delta_hf_kj_per_mol": dhf, "s_kj_per_mol_k": s}
    return dhf, s

# ----------------------------
# Reaction thermodynamics
# ----------------------------

def reaction_thermo(reaction: str, cache: dict, T: float = T_REF) -> tuple[float | None, float | None, float | None]:
    """Compute (ΔH°, ΔS°, ΔG°) at T from species formation properties."""
    lhs, rhs = parse_reaction(reaction)

    # Gather species set
    species = sorted(set(lhs) | set(rhs))

    # Look up species properties
    h: Dict[str, float] = {}
    s: Dict[str, float] = {}
    missing = []
    for sp in species:
        dhf, s0 = get_species_thermo(sp, cache)
        if dhf is None or s0 is None:
            missing.append(sp)
        else:
            h[sp] = dhf              # kJ/mol
            s[sp] = s0               # kJ/(mol·K)

    if missing:
        print(f"[warn] Missing data for {reaction}: {missing}")
        return None, None, None

    # Sum over stoichiometry
    def sum_props(sto: Dict[str, float], prop: Dict[str, float]) -> float:
        total = 0.0
        for sp, coef in sto.items():
            total += coef * prop[sp]
        return total

    dH = sum_props(rhs, h) - sum_props(lhs, h)        # kJ/mol
    dS = sum_props(rhs, s) - sum_props(lhs, s)        # kJ/(mol·K)
    dG = dH - T * dS                                  # kJ/mol
    return dH, dS, dG

# ----------------------------
# CLI
# ----------------------------

DEFAULT_REACTIONS = [
    "2H2 + O2 -> 2H2O",
    "C + O2 -> CO2",
    "N2 + 3H2 -> 2NH3",
    "CH4 + 2O2 -> CO2 + 2H2O",
    "2CO + O2 -> 2CO2",
    "CaCO3 -> CaO + CO2",
]

def read_reactions_from_file(path: Path) -> List[str]:
    lines = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines

def main() -> None:
    ap = argparse.ArgumentParser(description="Fetch NIST species data and compute reaction ΔG° datasets.")
    ap.add_argument("--reactions-file", type=str, default="", help="Text file with one reaction per line.")
    ap.add_argument("--temperature", type=float, default=T_REF, help="Temperature in K (default 298.15).")
    ap.add_argument("--sleep", type=float, default=0.8, help="Seconds to sleep between fetches to be polite.")
    args = ap.parse_args()

    root = Path.cwd()
    data_raw = root / "data" / "raw"
    data_proc = root / "data" / "processed"
    models_dir = root / "models"
    scripts_dir = root / "scripts"
    cache_path = data_raw / "nist_species_cache.json"

    data_raw.mkdir(parents=True, exist_ok=True)
    data_proc.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)

    # Load reactions
    if args.reactions_file:
        reactions = read_reactions_from_file(Path(args.reactions_file))
    else:
        reactions = DEFAULT_REACTIONS
        print("[info] Using built-in default reactions. Provide --reactions-file to customize.")

    # Load cache
    cache = load_cache(cache_path)

    rows = []
    for rxn in reactions:
        print(f"[info] Processing: {rxn}")
        dH, dS, dG = reaction_thermo(rxn, cache, T=args.temperature)
        if dH is None or dS is None or dG is None:
            print(f"[warn] Skipping {rxn}: incomplete species data.")
        else:
            rows.append({
                "reaction": rxn,
                "delta_h": dH,
                "delta_s": dS,
                "delta_g": dG,
                "T_K": args.temperature,
            })
        # Save cache incrementally
        save_cache(cache_path, cache)
        time.sleep(max(0.0, args.sleep))

    if not rows:
        print("[error] No complete rows computed. Try different reactions or inspect cache.")
        return

    df = pd.DataFrame(rows)
    # Primary outputs
    delta_g_csv = data_proc / "delta_g.csv"
    df[["reaction", "delta_g"]].to_csv(delta_g_csv, index=False)
    print(f"[ok] Wrote {delta_g_csv} ({len(df)} rows)")

    # Classification labels
    spont_csv = data_proc / "spont.csv"
    df.assign(label=(df["delta_g"] < 0).astype(int))[["reaction", "label"]].to_csv(spont_csv, index=False)
    print(f"[ok] Wrote {spont_csv} ({len(df)} rows)")

    # Full thermo breakdown
    thermo_csv = data_proc / "reaction_thermo.csv"
    df.to_csv(thermo_csv, index=False)
    print(f"[ok] Wrote {thermo_csv} (ΔH, ΔS, ΔG, T)")


if __name__ == "__main__":
    main()

