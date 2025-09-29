---

# Thermochemistry Explorer

Thermochemistry Explorer is a Python-based scientific computing and machine learning toolkit for analyzing chemical reactions. It computes thermodynamic quantities — enthalpy (ΔH), entropy (ΔS), and Gibbs free energy (ΔG) — at user-specified temperatures using data from the [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/). Beyond classical thermodynamics, it integrates machine learning models to predict ΔG and classify reaction spontaneity, enabling scalable, data-driven discovery.

This project demonstrates how algorithmic thinking, data parsing, and AI/ML can drive insights in the natural sciences — blending **scientific computing, applied machine learning, and modern software engineering**.

---

## Features

* **Classical Thermodynamics**

  * Parse user-input balanced chemical equations
  * Compute ΔH, ΔS, ΔG at arbitrary temperatures
  * Retrieve data live from NIST or fallback to curated datasets
  * Generate energy diagrams for reaction profiles

* **AI/ML Extensions**

  * Train regression models (e.g., Random Forest, XGBoost) to predict ΔG from reaction features
  * Train classifiers to predict spontaneity (ΔG < 0) across diverse reaction sets
  * Support for custom datasets via `data/processed/` CSVs
  * Save and reuse trained models for inference in research workflows
  * Compare ML predictions vs classical calculations in an interactive Streamlit UI

* **Engineering & Data Pipeline**

  * Clean separation of classical (`core/`) and ML (`ml/`) code
  * Automated training scripts with model cards (performance metrics, dataset info)
  * Modular design for easy extension and reproducibility

---

## Installation

```bash
git clone https://github.com/avoryscampbell/Thermochemistry-Explorer.git
cd Thermochemistry-Explorer
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## Usage

### CLI (classical mode)

```bash
python main.py
```

You’ll be prompted for:

1. A balanced equation (e.g., `CH4 + 2 O2 -> CO2 + 2 H2O`)
2. A temperature (Kelvin, e.g., `298`)

### ML Training

```bash
python -m ml.train_regression data/processed/delta_g.csv
python -m ml.train_classifier data/processed/spont.csv
```

### ML Inference

```bash
python -m ml.infer "CH4 + 2 O2 -> CO2 + 2 H2O"
```

### Streamlit (interactive UI)

```bash
streamlit run app_ml.py
```

---

## Example Output

**Classical calculation (298 K):**

```
ΔH = -802.30 kJ/mol
ΔS = 10.10 J/mol·K
ΔG = -805.31 kJ/mol
```

**ML prediction (trained RF model):**

```
Predicted ΔG = -798.2 kJ/mol
Spontaneity Class = Spontaneous
```

---

## Project Structure

```
thermochemistry-explorer/
│
├── core/                 # Classical thermodynamics
├── ml/                   # ML training, inference, features
├── data/processed/       # CSVs for regression/classification
├── models/               # Saved model artifacts
├── app_ml.py             # Streamlit interface
├── requirements.txt
└── README.md
```

---

## Roadmap

* Expand datasets via NIST WebBook scraping
* Incorporate molecular descriptors (e.g., RDKit features)
* Add SHAP/feature importance for ML interpretability
* Benchmark across multiple ML algorithms
* Deploy web app for public access

---

## Author

Created by **Avory Campbell**
B.A. Candidate in Computer Science, Columbia University

Blending **scientific computing and AI/ML** to explore how algorithms transform raw data into interpretable, predictive insights.

---
