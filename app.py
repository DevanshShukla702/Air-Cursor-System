import streamlit as st
import time

def main():
    st.set_page_config(page_title="AirCursor System", layout="wide", initial_sidebar_state="collapsed")

    # Inject Custom CSS for giant gesture-friendly buttons and layout
    st.markdown("""
        <style>
        /* Base page styling */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }

        /* Large Gesture-Friendly Buttons */
        div.stButton > button {
            width: 100%;
            height: 140px;
            font-size: 36px !important;
            font-weight: 700;
            border-radius: 20px;
            background-color: #2b2b2b;
            color: #ffffff;
            border: 2px solid #4ade80;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            margin-bottom: 30px;
            cursor: pointer;
        }

        /* Hover effects optimized for visual feedback during gesture approach */
        div.stButton > button:hover {
            background-color: #4ade80;
            color: #111827 !important;
            border-color: #22c55e;
            transform: scale(1.02);
            box-shadow: 0 20px 25px -5px rgba(74, 222, 128, 0.4), 0 10px 10px -5px rgba(74, 222, 128, 0.2);
        }
        
        div.stButton > button:active {
            transform: scale(0.97);
            background-color: #22c55e;
        }
        
        /* Titles and headers */
        h1 {
            text-align: center;
            font-size: 4rem;
            margin-bottom: 1rem;
            color: #f3f4f6;
        }
        
        .subtitle {
            text-align: center;
            color: #9ca3af;
            font-size: 1.5rem;
            margin-bottom: 3rem;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title Section
    st.title("AirCursor System")
    st.markdown("<div class='subtitle'>Use hand gestures to navigate the interface</div>", unsafe_allow_html=True)

    # Placeholders for feedback
    feedback_placeholder = st.empty()

    # Layout for centering large buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🍽️ Browse Menu", use_container_width=True):
            feedback_placeholder.success("Navigating to Menu...", icon="✅")
            time.sleep(1.5)
            st.rerun()
            
        if st.button("🛒 Place Order", use_container_width=True):
            feedback_placeholder.info("Opening Order processing...", icon="✅")
            time.sleep(1.5)
            st.rerun()
            
        if st.button("🙋 Request Help", use_container_width=True):
            feedback_placeholder.warning("Calling for assistance. A representative will be with you shortly.", icon="✅")
            time.sleep(1.5)
            st.rerun()
            
        if st.button("👋 Exit", use_container_width=True):
            feedback_placeholder.error("Exiting session. Thank you for visiting!", icon="✅")
            time.sleep(1.5)
            st.rerun()

    # Footer instruction
    st.markdown("""
        <div style='position: fixed; bottom: 20px; width: 100%; text-align: center; color: #6b7280;'>
            <i>Pinch your thumb and index finger together to click</i>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
