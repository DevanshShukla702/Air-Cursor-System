import streamlit as st
import time
import os

def check_gesture_commands():
    if os.path.exists("gesture_command.txt"):
        try:
            with open("gesture_command.txt", "r") as f:
                cmd = f.read().strip()
            # Delete file after reading
            os.remove("gesture_command.txt")
            
            if cmd == "HOME" and st.session_state.page != 'Home':
                navigate_to('Home')
                st.rerun()
            elif cmd == "MENU" and st.session_state.page != 'Menu':
                navigate_to('Menu')
                st.rerun()
        except Exception:
            pass

def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'Home'
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'total_price' not in st.session_state:
        st.session_state.total_price = 0.0

def navigate_to(page_name):
    st.session_state.page = page_name

def add_to_cart(item, price):
    st.session_state.cart.append({'item': item, 'price': price})
    st.session_state.total_price += price

def clear_cart():
    st.session_state.cart = []
    st.session_state.total_price = 0.0

def main():
    st.set_page_config(page_title="AirCursor System", layout="centered", initial_sidebar_state="collapsed")
    initialize_session_state()
    check_gesture_commands()

    # Generic Custom CSS to make buttons large for gesture control
    st.markdown("""
        <style>
        /* Base page styling */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
        }

        /* Make standard Streamlit buttons large */
        div.stButton > button {
            width: 100%;
            height: 90px;
            font-size: 26px !important;
            font-weight: bold;
            border-radius: 12px;
            background-color: #2b2b2b;
            color: #ffffff;
            border: 2px solid #4ade80;
            transition: all 0.2s ease;
            margin-bottom: 15px;
        }

        div.stButton > button:hover {
            background-color: #4ade80;
            color: #111827 !important;
            border-color: #22c55e;
            transform: scale(1.02);
            box-shadow: 0 10px 15px -3px rgba(74, 222, 128, 0.4);
        }
        
        div.stButton > button:active {
            transform: scale(0.97);
            background-color: #22c55e;
        }
        
        h1 {
            text-align: center;
            font-size: 3rem;
            color: #f3f4f6;
            margin-bottom: 0px;
        }
        
        .subtitle {
            text-align: center;
            color: #9ca3af;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("Touchless Smart Kiosk")
    
    # Render logic based on session state page
    page = st.session_state.page
    
    if page == 'Home':
        st.markdown("<div class='subtitle'>Welcome! Use hand gestures to select an option below:</div>", unsafe_allow_html=True)
        st.write("")
        if st.button("🍔 Browse Menu", use_container_width=True):
            navigate_to('Menu')
            st.rerun()
            
        if st.button("🛒 View Order", use_container_width=True):
            navigate_to('Order')
            st.rerun()
            
        if st.button("🙋 Help & Instructions", use_container_width=True):
            navigate_to('Help')
            st.rerun()
            
    elif page == 'Menu':
        st.markdown("<div class='subtitle'>Select items to add to your cart</div>", unsafe_allow_html=True)
        
        if st.button("⬅️ Back to Home", use_container_width=True):
            navigate_to('Home')
            st.rerun()
            
        st.markdown("---")
        
        # Expanded menu items to ensure scrollibility
        menu_items = [
            ("🍕 Pizza", 10.00),
            ("🍔 Burger", 8.00),
            ("☕ Coffee", 5.00),
            ("🥪 Sandwich", 6.00),
            ("🥗 Salad", 7.00),
            ("🍰 Cheesecake", 4.00),
            ("🥤 Soda", 2.00),
            ("🍦 Ice Cream", 3.00),
            ("🍩 Donut", 2.50),
            ("🍟 French Fries", 4.50)
        ]
        
        feedback_placeholder = st.empty()
        
        for name, price in menu_items:
            with st.container():
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.markdown(f"### {name}")
                    st.markdown(f"**Price:** ${price:.2f}")
                with col2:
                    st.write("") # spacing alignment
                    # Unique key for every button
                    if st.button(f"Add {name.split(' ')[1]}", key=f"add_{name}", use_container_width=True):
                        add_to_cart(name, price)
                        feedback_placeholder.success(f"{name} added to cart!")
                st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
                
    elif page == 'Order':
        st.markdown("<div class='subtitle'>Review your selected items</div>", unsafe_allow_html=True)
        
        if st.button("⬅️ Back to Home", use_container_width=True):
            navigate_to('Home')
            st.rerun()
            
        st.markdown("---")
        
        cart = st.session_state.cart
        if len(cart) == 0:
            st.info("Your cart is empty. Go back and browse the menu to add items!")
        else:
            for i, item_data in enumerate(cart):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{i+1}. {item_data['item']}**")
                with col2:
                    st.markdown(f"${item_data['price']:.2f}")
            
            st.markdown("---")
            st.markdown(f"<h3 style='text-align: right;'>Total: ${st.session_state.total_price:.2f}</h3>", unsafe_allow_html=True)
            
            st.write("")
            colA, colB = st.columns(2)
            with colA:
                if st.button("🗑️ Clear Cart", use_container_width=True):
                    clear_cart()
                    st.rerun()
            with colB:
                if st.button("✅ Checkout", use_container_width=True):
                    st.success("Order Placed Successfully! Returning to home...")
                    time.sleep(2)
                    clear_cart()
                    navigate_to('Home')
                    st.rerun()
                    
    elif page == 'Help':
        st.markdown("<div class='subtitle'>Gesture Controls Guide</div>", unsafe_allow_html=True)
        
        if st.button("⬅️ Back to Home", use_container_width=True):
            navigate_to('Home')
            st.rerun()
            
        st.markdown("---")
        
        st.info("### 🖱️ Move Cursor\nKeep your **Index Finger** extended to drag the mouse.")
        st.success("### 👆 Left Click\nPinch your **Thumb** and **Index Finger** together to click buttons.")
        st.success("### ✌️ Right Click\nPinch your **Thumb** and **Middle Finger** together to right-click.")
        st.warning("### ↕️ Scroll\nExtend your **Index** and **Middle Fingers** together and move your hand up/down to scroll long pages like the Menu.")
        st.error("### ↔️ Back / Forward\nExtend at least 3 fingers and quickly swipe your hand **Left** or **Right** to go Back or Forward in your browser.")
        st.markdown("### ⏸️ Pause Mode\nOpen your palm entirely (all 5 fingers up). The cursor tracking will freeze so you can reposition your hand comfortably.")

if __name__ == "__main__":
    main()
