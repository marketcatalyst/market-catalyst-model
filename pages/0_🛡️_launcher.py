import streamlit as st

st.title("🛡️ STRATA Financial Intelligence Portal")
st.caption("Enterprise Workspace Security Engine & Scenario Access Control Gateway")
st.markdown("---")

st.subheader("👋 Welcome back, Marketcatalyst")
st.write("Select an active project workspace below. The platform will dynamically hydrate your calculation modules, local tax shapes, and loan structures.")

# Pull directly from our master configuration dictionary defined in home.py
if "available_projects" in st.session_state:
    available_projects = st.session_state["available_projects"]
    
    selected_project_name = st.selectbox(
        "Available Corporate Environments Registries:",
        options=list(available_projects.keys()),
        key="portal_environment_selector"
    )

    st.markdown(" ")
    if st.button(f"🚀 Hydrate Workspace & Launch [{selected_project_name}]", use_container_width=True):
        st.session_state["baseline_inputs"] = available_projects[selected_project_name].copy()
        st.toast(f"Operational variables for {selected_project_name} successfully cached in RAM!", icon="🔥")
        st.success("✔️ Workspace Hydrated. The sidebar options are unlocked.")
else:
    st.warning("System Registry Matrix Offline. Please re-authenticate.")