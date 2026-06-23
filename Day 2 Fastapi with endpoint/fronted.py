import streamlit as st
import requests

# API ka base URL (tumhara FastAPI server)
API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Shop API", page_icon="🛒", layout="wide")

st.title("🛒 My Shop - FastAPI Frontend")
st.write("FastAPI backend se connected hai!")

# -------- SIDEBAR MENU --------
menu = st.sidebar.selectbox("Menu Chunein", [
    "🏠 Home",
    "👤 Users",
    "📦 Products",
    "🛍️ Orders"
])

# ============= HOME PAGE =============
if menu == "🏠 Home":
    st.header("Welcome Bhai! 🎉")
    
    # Check API status
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            data = response.json()
            st.success(f"✅ API Connected! Project: {data['project']}")
            st.info(f"📌 Version: {data['version']}")
        else:
            st.error("❌ API Se Connect Nahi Ho Saka")
    except:
        st.error("❌ FastAPI Server Band Hai! Pehle server start karo")
        st.code("uvicorn app.main:app --reload", language="bash")

# ============= USERS PAGE =============
elif menu == "👤 Users":
    st.header("👤 Users Management")
    
    tab1, tab2 = st.tabs(["📋 Sab Users", "➕ Naya User"])
    
    # --- Sab Users Dekho ---
    with tab1:
        if st.button("🔄 Users Load Karo"):
            try:
                response = requests.get(f"{API_URL}/api/v1/users/")
                if response.status_code == 200:
                    users = response.json()
                    st.success(f"✅ Total {len(users)} users mile")
                    for user in users:
                        with st.expander(f"👤 {user['full_name']} (@{user['username']})"):
                            st.json(user)
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    # --- Naya User Banao ---
    with tab2:
        with st.form("new_user"):
            st.subheader("Naya User Register Karein")
            username = st.text_input("Username", placeholder="aliza_dev")
            email = st.text_input("Email", placeholder="aliza@example.com")
            password = st.text_input("Password", type="password", placeholder="Secure@123")
            full_name = st.text_input("Full Name", placeholder="Aliza Javed")
            age = st.number_input("Age", min_value=13, max_value=120, value=22)
            role = st.selectbox("Role", ["viewer", "editor", "admin"])
            
            submitted = st.form_submit_button("✅ User Banao")
            
            if submitted:
                user_data = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "full_name": full_name,
                    "age": age,
                    "role": role
                }
                try:
                    response = requests.post(f"{API_URL}/api/v1/users/", json=user_data)
                    if response.status_code == 201:
                        st.success("🎉 User Ban Gaya!")
                        st.json(response.json())
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                        st.json(response.json())
                except Exception as e:
                    st.error(f"Error: {e}")

# ============= PRODUCTS PAGE =============
elif menu == "📦 Products":
    st.header("📦 Products Management")
    
    tab1, tab2 = st.tabs(["📋 Sab Products", "➕ Naya Product"])
    
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox("Category", ["all", "electronics", "clothing", "books", "food", "other"])
        with col2:
            in_stock = st.checkbox("Sirf In-Stock")
        with col3:
            st.write("")  # spacing
        
        if st.button("🔄 Products Load Karo"):
            try:
                params = {}
                if category != "all":
                    params["category"] = category
                if in_stock:
                    params["in_stock"] = True
                    
                response = requests.get(f"{API_URL}/api/v1/products/", params=params)
                if response.status_code == 200:
                    products = response.json()
                    st.success(f"✅ Total {len(products)} products mile")
                    
                    # Cards mein dikhao
                    cols = st.columns(3)
                    for i, prod in enumerate(products):
                        with cols[i % 3]:
                            with st.container():
                                st.subheader(prod['name'])
                                st.write(f"💰 Price: **${prod['price']}**")
                                st.write(f"🏷️ Final: **${prod['final_price']}**")
                                st.write(f"📦 Stock: {prod['stock']}")
                                st.write(f"🏷️ SKU: `{prod['sku']}`")
                                st.write(f"📂 {prod['category']}")
                                st.divider()
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        with st.form("new_product"):
            st.subheader("Naya Product Add Karein")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Product Name", placeholder="Python Book")
                price = st.number_input("Price ($)", min_value=0.01, value=29.99)
                stock = st.number_input("Stock", min_value=0, value=50)
                sku = st.text_input("SKU", placeholder="BK-001234")
            
            with col2:
                discount = st.slider("Discount (%)", 0, 100, 0)
                category = st.selectbox("Category", ["books", "electronics", "clothing", "food", "other"])
                tags = st.text_input("Tags (comma se)", placeholder="python, programming")
            
            description = st.text_area("Description", placeholder="Complete guide...")
            
            submitted = st.form_submit_button("✅ Product Banao")
            
            if submitted:
                product_data = {
                    "name": name,
                    "description": description,
                    "price": price,
                    "discount": discount,
                    "stock": stock,
                    "category": category,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "sku": sku
                }
                try:
                    response = requests.post(f"{API_URL}/api/v1/products/", json=product_data)
                    if response.status_code == 201:
                        st.success("🎉 Product Ban Gaya!")
                        st.json(response.json())
                    else:
                        st.error(f"❌ Error")
                        st.json(response.json())
                except Exception as e:
                    st.error(f"Error: {e}")

# ============= ORDERS PAGE =============
elif menu == "🛍️ Orders":
    st.header("🛍️ Orders Management")
    
    tab1, tab2 = st.tabs(["📋 Sab Orders", "➕ Naya Order"])
    
    with tab1:
        if st.button("🔄 Orders Load Karo"):
            try:
                response = requests.get(f"{API_URL}/api/v1/orders/")
                if response.status_code == 200:
                    orders = response.json()
                    st.success(f"✅ Total {len(orders)} orders")
                    
                    for order in orders:
                        status_emoji = {
                            "pending": "⏳", "confirmed": "✅", 
                            "shipped": "🚚", "delivered": "📦", 
                            "cancelled": "❌"
                        }
                        emoji = status_emoji.get(order['status'], "📋")
                        
                        with st.expander(f"{emoji} Order #{order['id']} - ${order['total']} ({order['status']})"):
                            st.json(order)
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    with tab2:
        st.info("💡 Pehle product create karo, phir order banao")
        
        with st.form("new_order"):
            user_id = st.number_input("User ID", min_value=1, value=1)
            product_id = st.number_input("Product ID", min_value=1, value=1)
            quantity = st.number_input("Quantity", min_value=1, value=1)
            unit_price = st.number_input("Unit Price ($)", min_value=0.01, value=29.99)
            payment = st.selectbox("Payment Method", ["card", "cash", "bank_transfer"])
            address = st.text_area("Delivery Address", placeholder="123 Main St, City, Country")
            
            submitted = st.form_submit_button("✅ Order Place Karo")
            
            if submitted:
                order_data = {
                    "user_id": user_id,
                    "items": [{"product_id": product_id, "quantity": quantity, "unit_price": unit_price}],
                    "payment_method": payment,
                    "delivery_address": address
                }
                try:
                    response = requests.post(f"{API_URL}/api/v1/orders/", json=order_data)
                    if response.status_code == 201:
                        st.success("🎉 Order Place Ho Gaya!")
                        st.json(response.json())
                    else:
                        st.error("❌ Error")
                        st.json(response.json())
                except Exception as e:
                    st.error(f"Error: {e}")

# -------- FOOTER --------
st.sidebar.markdown("---")
st.sidebar.info("💻 Backend: FastAPI\n🎨 Frontend: Streamlit\n🐍 Python")
