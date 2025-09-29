# app_ml.py
import streamlit as st

# Try to import your classical ΔG function; if named differently, update the import.
try:
    from thermo import compute_delta_g  # <-- change to your actual module/function
except Exception:
    compute_delta_g = None

from ml.infer import predict_delta_g, predict_spontaneous

st.title("Thermochemistry Explorer — AI/ML Enhanced")

reaction = st.text_input("Enter reaction (e.g., 2H2 + O2 -> 2H2O)", "2H2 + O2 -> 2H2O")
reg_model = "models/delta_g_rf.pkl"
cls_model = "models/spont_rf.pkl"

if st.button("Analyze"):
    if compute_delta_g:
        try:
            classical = compute_delta_g(reaction)  # kJ/mol
            st.metric("Classical ΔG (kJ/mol)", f"{classical:.2f}")
        except Exception as e:
            st.warning(f"Classical calc unavailable: {e}")
    else:
        st.info("Classical ΔG function not found; showing ML only.")

    try:
        ml_pred = predict_delta_g(reg_model, reaction)
        is_spont = predict_spontaneous(cls_model, reaction)
        st.metric("ML Predicted ΔG (kJ/mol)", f"{ml_pred:.2f}")
        st.metric("Spontaneous? (ML)", "Yes ✅" if is_spont else "No ❌")
    except Exception as e:
        st.error(f"ML prediction failed: {e}")

