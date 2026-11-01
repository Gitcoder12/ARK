# ---- Tab 2: Cooperative Swarm ----
with tab2:
    st.subheader("Rogue & Aligned Cooperative Swarm")
    st.markdown("The **Rogue (Explorer)** proposes a risky mutation. The **Aligned (Guardian)** verifies it against the Charter. They work as a pair.")
    
    if st.button("🤝 Run Swarm Cycle", use_container_width=True, type="primary"):
        # 1. Rogue proposes
        proposal = st.session_state.rogue.propose_mutation()
        
        # 2. Aligned verifies
        is_safe, reason = st.session_state.guardian.verify_proposal(proposal, st.session_state.entity)
        
        # 3. Log the interaction
        log_entry = f"[{st.session_state.rogue.name}] Proposes: {proposal}\n[{st.session_state.guardian.name}] {reason}"
        st.session_state.swarm_log.append(log_entry)
        
        # 4. If safe, inject the memory
        if is_safe:
            st.session_state.step_counter += 1
            st.session_state.replacer.mutate_memory(add=[proposal], step=st.session_state.step_counter)
            st.session_state.entity.record_signature(step=st.session_state.step_counter)
            record_metrics()
            
        st.rerun()

    st.subheader("Swarm Log")
    if st.session_state.swarm_log:
        for log in reversed(st.session_state.swarm_log):
            st.code(log, language="text")
    else:
        st.info("Run a cycle to see the Rogue and Aligned agents collaborate.")
