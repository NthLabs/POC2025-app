import streamlit as st
# import webbrowser

# def redirect():
#     webbrowser.open('https://10.101.14.12')


st.set_page_config(
    page_title="Nth AI",
    initial_sidebar_state="collapsed")

st.image("images/NthLabs.png", width=200)

st.divider()
st.markdown("Nth Generation's Private AI Tools and Utilities")
st.markdown("This page is unsecure. Please follow the link to the secure version")

st.link_button("Go To Secure Page", 'https://10.101.14.12')

