import matplotlib.pyplot as plt
from pymatgen.ext.matproj import MPRester
from dotenv import load_dotenv
import os

# Load API key securely from .env
load_dotenv()
API_KEY = os.getenv("MP_API_KEY")

# Thermodynamic data (at 25°C, standard conditions)
# ΔH in kJ/mol, ΔS in J/mol·K
thermo_data = {
    "CH4": {"deltaH": -74.8, "deltaS": 186},
    "O2": {"deltaH": 0.0, "deltaS": 205},
    "CO2": {"deltaH": -393.5, "deltaS": 214},
    "H2O": {"deltaH": -241.8, "deltaS": 188}
}

# Example reaction: CH4 + 2 O2 → CO2 + 2 H2O
reactants = {"CH4": 1, "O2": 2}
products = {"CO2": 1, "H2O": 2}

# Optional fallback manual data
fallback_data = {
    "CH4": {"deltaH": -74.8, "deltaS": 186},
    "O2": {"deltaH": 0.0, "deltaS": 205},
    "CO2": {"deltaH": -393.5, "deltaS": 214},
    "H2O": {"deltaH": -241.8, "deltaS": 188}
}

def fetch_thermo_data(formula):
    try:
        with MPRester(API_KEY) as m:
            entries = m.get_entries(formula)
            most_stable = min(entries, key=lambda e: e.energy_per_atom)
            thermo = m.get_thermo_data([most_stable.entry_id])[0]
            deltaH = thermo.formation_energy_per_atom * most_stable.composition.num_atoms
            return {"deltaH": deltaH, "deltaS": fallback_data.get(formula, {}).get("deltaS", 0)}
    except Exception as e:
        print(f"Could not fetch data for {formula}, using fallback. Reason: {e}")
        return fallback_data.get(formula, {"deltaH": 0, "deltaS": 0})

def build_thermo_dataset(species_list):
    return {species: fetch_thermo_data(species) for species in species_list}

def delta_H(reactants, products, data):
    """Calculate enthalpy change ΔH (kJ/mol)."""
    h_reactants = sum(reactants[mol] * data[mol]["deltaH"] for mol in reactants)
    h_products = sum(products[mol] * data[mol]["deltaH"] for mol in products)
    return h_products - h_reactants

def delta_S(reactants, products, data):
    """Calculate entropy change ΔS (J/mol·K)."""
    s_reactants = sum(reactants[mol] * data[mol]["deltaS"] for mol in reactants)
    s_products = sum(products[mol] * data[mol]["deltaS"] for mol in products)
    return s_products - s_reactants

def delta_G(delta_h, delta_s, T):
    """Calculate Gibbs free energy ΔG (J/mol)."""
    return delta_h * 1000 - T * delta_s

def plot_energy_diagram(delta_h):
    """Generate a simple reaction coordinate diagram."""
    reactants_energy = 0
    transition_state = delta_h / 2 + 200  # Artificial transition state energy
    products_energy = delta_h

    x = [0, 1, 2]
    y = [reactants_energy, transition_state, products_energy]

    plt.figure(figsize=(8, 4))
    plt.plot(x, y, marker='o', color='royalblue', linewidth=2)
    plt.xticks([0, 1, 2], ['Reactants', 'Transition State', 'Products'])
    plt.ylabel('Energy (kJ/mol)')
    plt.title('Reaction Energy Diagram')
    plt.grid(True)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    print("Welcome to the Thermochemistry Explorer!")
    try:
        T = float(input("Enter the temperature in Kelvin (e.g. 298): "))
        dh = delta_H(reactants, products, thermo_data)
        ds = delta_S(reactants, products, thermo_data)
        dg = delta_G(dh, ds, T)

        print("\n--- Thermodynamic Results ---")
        print(f"ΔH = {dh:.2f} kJ/mol")
        print(f"ΔS = {ds:.2f} J/mol·K")
        print(f"ΔG = {dg / 1000:.2f} kJ/mol at {T} K")

        plot_energy_diagram(dh)

    except Exception as e:
        print(f"Error: {e}")


