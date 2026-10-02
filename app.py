import streamlit as st
import pandas as pd
from datetime import datetime
st.image("TRASUA.jpg.PNG")
# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Hệ Thống Bán Trà Sữa",
    page_icon="🧋",
    layout="wide"
)

# Khởi tạo giỏ hàng trong session state nếu chưa có
if "cart" not in st.session_state:
    st.session_state.cart = []

# Danh mục thực đơn và giá tiền (VNĐ)
MENU_DRINKS = {
    "Trà Sữa Truyền Thống": {"M": 30000, "L": 35000},
    "Trà Sữa Ô Long": {"M": 35000, "L": 40000},
    "Trà Sữa Matcha": {"M": 37000, "L": 42000},
    "Sữa Tươi Trân Châu Đường Đen": {"M": 40000, "L": 45000},
    "Trà Trái Cây Nhiệt Đới": {"M": 32000, "L": 38000},
    "Trà Đào Cam Sả": {"M": 32000, "L": 38000}
}

MENU_TOPPINGS = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 7000,
    "Thạch trái cây": 5000,
    "Pudding trứng": 8000,
    "Kem Cheese": 10000
}

# Tiêu đề ứng dụng
st.title("🧋 Ứng Dụng Tính Hóa Đơn Quán Trà Sữa")
st.markdown("---")

col_input, col_summary = st.columns([1.2, 1])

# ==================== CỘT 1: NHẬP THÔNG TIN MÓN ====================
with col_input:
    st.header("📋 Nhập Thông Tin Đơn Hàng")
    
    # 1. Nhập tên khách hàng
    customer_name = st.text_input("👤 Tên khách hàng:", placeholder="Nhập tên khách hàng...")

    st.subheader("🥤 Chọn thức uống")
    
    # 2. Chọn loại trà sữa
    drink_name = st.selectbox("Chọn loại trà sữa:", list(MENU_DRINKS.keys()))
    
    # 3. Chọn size ly
    size = st.radio("Chọn size ly:", ["M", "L"], horizontal=True)
    base_price = MENU_DRINKS[drink_name][size]
    
    # 4. Mức độ đường và đá
    col_sugar, col_ice = st.columns(2)
    with col_sugar:
        sugar = st.select_slider("Mức đường:", options=["0%", "30%", "50%", "70%", "100%"], value="100%")
    with col_ice:
        ice = st.select_slider("Mức đá:", options=["Không đá", "30%", "50%", "70%", "100%"], value="100%")
        
    # 5. Chọn topping
    selected_toppings = st.multiselect(
        "Chọn topping (có thể chọn nhiều):",
        options=list(MENU_TOPPINGS.keys()),
        format_func=lambda x: f"{x} (+{MENU_TOPPINGS[x]:,}đ)"
    )
    
    # Tính giá topping
    topping_price = sum(MENU_TOPPINGS[top] for top in selected_toppings)
    
    # 6. Số lượng
    quantity = st.number_input("Số lượng ly:", min_value=1, max_value=50, value=1, step=1)
    
    # Tính giá tiền cho món hiện tại
    unit_price = base_price + topping_price
    item_total = unit_price * quantity
    
    st.info(f"💰 **Đơn giá 1 ly (gồm topping):** {unit_price:,} VNĐ | **Thành tiền:** {item_total:,} VNĐ")
    
    # 7. Nút THÊM MÓN
    if st.button("➕ Thêm món vào đơn", type="primary", use_container_width=True):
        if not customer_name.strip():
            st.error("⚠️ Vui lòng nhập Tên khách hàng trước khi thêm món!")
        else:
            st.session_state.cart.append({
                "Tên món": f"{drink_name} (Size {size})",
                "Size": size,
                "Mức đường/Đá": f"Đường: {sugar}, Đá: {ice}",
                "Topping": ", ".join(selected_toppings) if selected_toppings else "Không",
                "Đơn giá": unit_price,
                "Số lượng": quantity,
                "Thành tiền": item_total
            })
            st.toast(f"Đã thêm {quantity} x {drink_name} vào đơn!", icon="✅")

# ==================== CỘT 2: HIỂN THỊ CHI TIẾT & TỔNG TIỀN ====================
with col_summary:
    st.header("🛒 Đơn Hàng Hiện Tại")
    
    if customer_name.strip():
        st.markdown(f"**Khách hàng:** `{customer_name.strip()}`")
    else:
        st.caption("Chưa nhập tên khách hàng")

    if not st.session_state.cart:
        st.warning("Đơn hàng chưa có món nào. Vui lòng chọn món và nhấn 'Thêm món vào đơn'.")
    else:
        # Bảng danh sách các món đã thêm
        df_cart = pd.DataFrame(st.session_state.cart)
        st.dataframe(
            df_cart[["Tên món", "Mức đường/Đá", "Topping", "Số lượng", "Thành tiền"]],
            use_container_width=True,
            hide_index=True
        )
        
        # Tính tổng tiền thanh toán
        grand_total = sum(item["Thành tiền"] for item in st.session_state.cart)
        
        st.markdown("---")
        st.subheader(f"💵 Tổng số tiền thanh toán: :red[{grand_total:,} VNĐ]")
        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("🗑️ Xóa toàn bộ đơn", use_container_width=True):
                st.session_state.cart = []
                st.rerun()
                
        with col_btn2:
            # 8. Nút THANH TOÁN -> Xuất Hóa Đơn
            pay_button = st.button("💳 Thanh Toán & Xuất Hóa Đơn", type="primary", use_container_width=True)

# ==================== XUẤT HÓA ĐƠN KHI BẤM THANH TOÁN ====================
if st.session_state.cart and 'pay_button' in locals() and pay_button:
    st.balloons()
    st.success("🎉 Thanh toán thành công!")
    
    grand_total = sum(item["Thành tiền"] for item in st.session_state.cart)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Hiển thị hóa đơn dạng khung giao diện
    bill_col1, bill_col2, bill_col3 = st.columns([1, 2, 1])
    with bill_col2:
        st.markdown("""
        <div style="text-align: center;">
            <h2>🧾 HÓA ĐƠN BÁN HÀNG</h2>
            <h4>🧋 QUÁN TRÀ SỮA HAPPY TEA</h4>
            <p><i>Địa chỉ: 123 Đường Sữa Tươi, Quận 1, TP. Hồ Chí Minh</i></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write(f"**Tên khách hàng:** {customer_name}")
        st.write(f"**Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        st.write("---")
        
        # Bảng chi tiết hóa đơn
        for idx, item in enumerate(st.session_state.cart, 1):
            st.markdown(f"**{idx}. {item['Tên món']}** x **{item['Số lượng']}** = **{item['Thành tiền']:,} VNĐ**")
            st.caption(f"└ Yêu cầu: {item['Mức đường/Đá']} | Topping: {item['Topping']}")
            
        st.write("---")
        st.markdown(f"### 🎯 TỔNG CỘNG THANH TOÁN: <span style='color:red;'>{grand_total:,} VNĐ</span>", unsafe_allow_html=True)
        st.write("---")
        st.markdown("<p style='text-align: center;'><i>Cảm ơn quý khách và hẹn gặp lại! 🙏</i></p>", unsafe_allow_html=True)
