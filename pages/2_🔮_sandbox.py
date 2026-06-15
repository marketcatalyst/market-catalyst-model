# pages/2_🔮_sandbox.py

import os
import sys
import json
import streamlit as st
import pandas as pd
from pathlib import Path

# Absolute project path resolution
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

if not st.session_state.get("authenticated", False):
    st.error("🔒 Access Denied: Unauthorized Endpoints Locked")
    st.stop()

PROJECTS_DIR = "saved_projects"

st.title("🔮 Multi-Variant Stress-Testing Sandbox")
st.caption("Apply real-time adjustments and scenario levers to your active project baseline parameters.")
st.markdown("---")

active_project = st.session_state.get("selected_project", "")

if not active_project:
    st.info("💡 Please select an active project workspace context on the main Home Page first to open the sandbox tools.")
else:
    st.subheader(f"🛠️ Active Base Scenario: `{active_project}`")
    st.markdown("Adjust the sliders below to apply sweeping adjustments across your cost and income modeling assumptions:")
    
    # --- SANDBOX SLIDER DIALS ---
    col1, col2 = st.columns(2)
    with col1:
        revenue_multiplier = st.slider("Revenue Stream Performance Scale (%)", min_value=50, max_value=150, value=100, step=5)
        opex_multiplier = st.slider("Running Overhead Inflation Scale (%)", min_value=50, max_value=150, value=100, step=5)
    with col2:
        st.markdown("### 📋 Variant Target Matrix")
        st.caption("Adjustments modify copy parameters into a temporary scenario variant, leaving your baseline files untouched.")
        sandbox_suffix = st.text_input("Alternative Scenario Name Suffix:", value="Stressed-Run")

    # --- PROCESSING COPIED PARAMETERS ---
    if st.button("🔮 Generate Alternative Scenario Run", use_container_width=True):
        try:
            # 1. Map adjustments down to lists
            sandboxed_sales = []
            for s in st.session_state.get("manual_sales_entries", []):
                s_copy = s.copy()
                s_copy["amount"] = float(s["amount"]) * (revenue_multiplier / 100.0)
                sandboxed_sales.append(s_copy)
                
            sandboxed_opex = []
            for o in st.session_state.get("manual_opex_entries", []):
                o_copy = o.copy()
                o_copy["amount"] = float(o["amount"]) * (opex_multiplier / 100.0)
                sandboxed_opex.append(o_copy)
                
            # Capital setup costs are left fixed to preserve building infrastructure reality
            sandboxed_capital = [c.copy() for c in st.session_state.get("manual_capital_entries", [])]
            
            # 2. Package and export as a unique variant file identifier
            variant_filename = f"SANDBOX_VARIANT_{active_project}_{sandbox_suffix}"
            variant_payload = {
                "sales": sandboxed_sales,
                "opex": sandboxed_opex,
                "capital": sandboxed_capital
            }
            
            filepath = os.path.join(PROJECTS_DIR, f"{variant_filename}.json")
            with open(filepath, "w") as pf:
                json.dump(variant_payload, pf, indent=4)
                
            # 3. Swap the active workspace selection context to look at the new scenario run files instantly
            st.session_state["selected_project"] = variant_filename
            st.session_state["manual_sales_entries"] = sandboxed_sales
            st.session_state["manual_opex_entries"] = sandboxed_opex
            st.session_state["manual_capital_entries"] = sandboxed_capital
            
            st.success(f"🚀 Alternative scenario variant compiled and loaded perfectly as: `{variant_filename}`")
            st.info("Navigate to the Financial Forecast Sheets via the sidebar drawer to compare your variant projections!")
            st.rerun()
            
        except Exception as sand_err:
            st.error(f"Sandbox Variant Compilation Error: {str(sand_err)}")