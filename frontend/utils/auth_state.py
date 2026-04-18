import streamlit as st


def init_session():
    defaults = {"token": None, "user": None, "logged_in": False}
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def get_token() -> str:
    return st.session_state.get("token", "")


def get_user() -> dict:
    return st.session_state.get("user", {})


def is_admin() -> bool:
    user = get_user()
    return user.get("role") == "admin"


def login(token: str, user: dict):
    st.session_state.token     = token
    st.session_state.user      = user
    st.session_state.logged_in = True


def logout():
    st.session_state.token     = None
    st.session_state.user      = None
    st.session_state.logged_in = False


def require_login():
    init_session()
    if not is_logged_in():
        st.error("Please login first.")
        st.stop()


def require_admin():
    require_login()
    if not is_admin():
        st.error("Admin access required.")
        st.stop()
