# Thermochemistry Explorer

Thermochemistry Explorer is a Python-based scientific computing tool that analyzes balanced chemical reactions to calculate thermodynamic quantities — including enthalpy (ΔH), entropy (ΔS), and Gibbs free energy (ΔG) — at user-specified temperatures. It retrieves live data from the [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/) and generates reaction energy diagrams to visualize spontaneity and thermodynamic favorability.

This project demonstrates how algorithmic thinking, data parsing, and visualization can drive insights in the natural sciences. It also introduces fallback logic for resilience in data-limited cases.

## Features

- Parse user-input balanced chemical equations (e.g., `CH4 + 2 O2 -> CO2 + 2 H2O`)
- Prompt for any temperature (in Kelvin)
- Calculate:

- Reaction enthalpy (ΔH, kJ/mol)
- Entropy change (ΔS, J/mol·K)
- Gibbs free energy (ΔG, kJ/mol)
- Generate energy diagrams for endothermic/exothermic behavior
- Automatically scrape from NIST or fallback to curated internal datasets for common species

## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/avoryscampbell/thermochemistry-explorer.git
cd thermochemistry-explorer
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage


python main.py


You will be prompted to enter:

1. A balanced chemical equation (e.g., `CH4 + 2 O2 -> CO2 + 2 H2O`)
2. Temperature in Kelvin** (e.g., `298`)

The tool will then:

* Parse the equation
* Retrieve thermodynamic data (via NIST or fallback)
* Print ΔH, ΔS, and ΔG
* Plot an energy diagram of the reaction

## Example

```
Enter a balanced chemical equation (e.g., CH4 + 2 O2 -> CO2 + 2 H2O): CH4 + 2 O2 -> CO2 + 2 H2O
Enter temperature in Kelvin: 298

ΔH = -802.30 kJ/mol
ΔS = 10.10 J/mol·K
ΔG = -805.31 kJ/mol
```

Energy diagram displayed in a Matplotlib window.

## Project Structure

```
thermochemistry-explorer/
│
├── main.py                     # Entry point
├── equation_parser.py          # Parses chemical equations
├── nist_scraper.py             # Scrapes thermodynamic data from NIST
├── fallback_thermo_data.py     # Fallback dataset for common species
├── energy_diagram.py           # Plots energy diagrams
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Acknowledgments

Developed by a Columbia University undergraduate in the Departments of Computer Science. Special thanks to:

* Columbia Department of Chemistry** for foundational thermodynamics instruction
* The NIST Chemistry WebBook** for open scientific data

## Goals

This project was created to:

* Demonstrate scientific computing fluency
* Integrate real-time data acquisition (web scraping)
* Show domain crossover from chemistry to software engineering
* Prepare for internships in software engineering, research, and quantitative finance

## License

This project is open source under the MIT License.

---

Planned Enhancements:

* Expand this into a Streamlit web app
* Implement formal benchmarking of thermodynamic parsing and calculation pipeline using large test suites
* Develop performance metrics to support quantitative performance claims
* Optimize reaction parsing and thermodynamic data retrieval using advanced data structures post-DSA coursework at Columbia

## Author

Created by Avory Campbell, B.A. Candidate in Computer Science, Columbia University  
Project developed as an intersection of computer science and chemistry to explore algorithmic approaches to thermodynamic computation.

For academic or professional inquiries, please contact via [GitHub](https://github.com/avoryscampbell) or [LinkedIn](https://www.linkedin.com/in/avory-campbell).
