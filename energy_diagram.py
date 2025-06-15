import matplotlib.pyplot as plt

def plot_energy_diagram(delta_h):
    plt.figure(figsize=(6, 4))
    
    reactant_energy = 0
    product_energy = -delta_h  # ΔH = H_products - H_reactants

    # Reactant block
    plt.plot([0, 1], [reactant_energy, reactant_energy], label='Reactants', color='blue', linewidth=3)
    # Line dropping to product energy
    plt.plot([1, 2], [reactant_energy, product_energy], 'k--')
    # Product block
    plt.plot([2, 3], [product_energy, product_energy], label='Products', color='green', linewidth=3)

    # Add arrows and labels
    plt.annotate(f"ΔH = {delta_h:.2f} kJ/mol",
                 xy=(1.5, (reactant_energy + product_energy)/2),
                 xytext=(1.5, (reactant_energy + product_energy)/2 + 10),
                 arrowprops=dict(facecolor='black', shrink=0.05),
                 ha='center')

    # Styling
    plt.title("Reaction Energy Diagram")
    plt.ylabel("Relative Energy (kJ/mol)")
    plt.xticks([])
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()

