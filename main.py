"""
Thermochemistry Explorer
Author: Avory Campbell
Columbia University, Department of Computer Science

A Python program for computing thermodynamic quantities (ΔH, ΔS, ΔG) from balanced chemical reactions,
using both live scraping from the NIST Chemistry WebBook and fallback datasets.

Fallback Thermodynamic Dataset: Provides hard-coded thermodynamic properties (ΔHf°, S°)
for common chemical species in case NIST data retrieval fails. Ensures continuity and stability of
analysis in offline or partial-data scenarios.
"""

# Fallback thermo data for common species: ΔH in kJ/mol, ΔS in J/mol·K
FALLBACK_THERMO_DATA = {
    "H2O": {"deltaH": -241.8, "deltaS": 69.9},
    "CO2": {"deltaH": -393.5, "deltaS": 213.7},
    "O2": {"deltaH": 0.0, "deltaS": 205.0},
    "H2": {"deltaH": 0.0, "deltaS": 130.6},
    "CH4": {"deltaH": -74.8, "deltaS": 186.3},
    "NH3": {"deltaH": -45.9, "deltaS": 192.8},
    "N2": {"deltaH": 0.0, "deltaS": 191.5},
    "C2H6": {"deltaH": -84.0, "deltaS": 229.5},
    "CO": {"deltaH": -110.5, "deltaS": 197.7},
    "H2O2": {"deltaH": -136.1, "deltaS": 109.6},
}

from nist_scraper import fetch_nist_data
from equation_parser import parse_equation
from energy_diagram import plot_energy_diagram

def delta_H(reactants, products, data):
    return sum(products[sp] * data[sp]["deltaH"] for sp in products) - \
           sum(reactants[sp] * data[sp]["deltaH"] for sp in reactants)

def delta_S(reactants, products, data):
    return sum(products[sp] * data[sp]["deltaS"] for sp in products) - \
           sum(reactants[sp] * data[sp]["deltaS"] for sp in reactants)

def delta_G(dh, ds, T):
    return dh - (T * ds / 1000)

def main():
    print("Thermochemistry Explorer (NIST with fallback)")
    equation = input("Enter a balanced chemical equation (e.g., CH4 + 2 O2 -> CO2 + 2 H2O): ")
    T = float(input("Enter temperature in Kelvin: "))

    reactants, products = parse_equation(equation)
    all_species = list(set(reactants.keys()).union(products.keys()))

    thermo_data = {}
    for species in all_species:
        data = fetch_nist_data(species)
        if data:
            thermo_data[species] = data
        elif species in FALLBACK_THERMO_DATA:
            print(f"Using fallback data for {species}")
            thermo_data[species] = FALLBACK_THERMO_DATA[species]
        else:
            print(f"Missing thermo data for {species}, skipping.")
    
    missing = [sp for sp in all_species if sp not in thermo_data]
    if missing:
        print("️ Could not retrieve data for:", missing)
        return

    dh = delta_H(reactants, products, thermo_data)
    ds = delta_S(reactants, products, thermo_data)
    dg = delta_G(dh, ds, T)

    print(f"\nΔH = {dh:.2f} kJ/mol")
    print(f"ΔS = {ds:.2f} J/mol·K")
    print(f"ΔG = {dg:.2f} kJ/mol")

    plot_energy_diagram(dh)

if __name__ == "__main__":
    main()
