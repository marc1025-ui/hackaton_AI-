import streamlit as st
from functools import wraps

def safewatch_app(title="SafeWatch - Hutchinson"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Configuration de la page
            st.set_page_config(
                page_title=title,
                page_icon="🛡️",
                layout="wide",
                initial_sidebar_state="collapsed"
            )

            # CSS global pour le dark theme Hutchinson
            st.markdown("""
            <style>
            .stApp {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%);
                color: #f1f5f9;
            }
            .stButton > button {
                background: linear-gradient(135deg, #dc2626, #b91c1c);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .stButton > button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
            }
            h1, h2, h3 { color: #f1f5f9; }
            .stMarkdown { color: #f1f5f9; }
            .stCaption { color: #f1f5f9 !important; }
            </style>
            """, unsafe_allow_html=True)

            return func(*args, **kwargs)
        return wrapper
    return decorator
