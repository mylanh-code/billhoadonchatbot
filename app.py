from datetime import datetime
import pandas as pd
import streamlit as st

# Cấu hình trang Streamlit - Bắt buộc đặt ở dòng đầu tiên của các lệnh Streamlit
st.set_page_config(page_title="Hệ Thống Bán Trà Sữa", page_icon="🧋", layout="wide")

# Khởi tạo session_state cho giỏ hàng và lịch sử chat nếu chưa có
if "cart" not in st.session_state:
    st.session_state.cart = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {
            "role": "assistant",
            "content": "Xin chào! Mình là chatbot tư vấn menu trà sữa. Bạn cần mình trợ giúp gì không?",
        }
    ]

# Danh mục thực đơn và giá tiền (VNĐ)
MENU_DRINKS = {
    "Trà Sữa Truyền Thống": {"M": 30000, "L": 35000},
    "Trà Sữa Ô Long": {"M": 35000, "L": 40000},
    "Trà Sữa Matcha": {"M": 37000, "L": 42000},
    "Sữa Tươi Trân Châu Đường Đen": {"M": 40000, "L": 45000},
    "Trà Trái Cây Nhiệt Đới": {"M": 32000, "L": 38000},
    "Trà Đào Cam Sả": {"M": 32000, "L": 38000},
}

MENU_TOPPINGS = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 7000,
    "Thạch trái cây": 5000,
    "Pudding trứng": 8000,
    "Kem Cheese": 10000,
}

# Gợi ý topping thích hợp cho từng món
TOPPING_RECOMMENDATIONS = {
    "Trà Sữa Truyền Thống": [
        "Trân châu đen",
        "Pudding trứng",
        "Kem Cheese",
    ],
    "Trà Sữa Ô Long": ["Trân châu trắng", "Kem Cheese"],
    "Trà Sữa Matcha": ["Pudding trứng", "Kem Cheese", "Trân châu đen"],
    "Sữa Tươi Trân Châu Đường Đen": [
        "Trân châu đen (đã có sẵn)",
        "Kem Cheese",
        "Pudding trứng",
    ],
    "Trà Trái Cây Nhiệt Đới": ["Trân châu trắng", "Thạch trái cây"],
    "Trà Đào Cam Sả": ["Trân châu trắng", "Thạch trái cây"],
}


# ==================== CHATBOT DỰA TRÊN LUẬT (RULE-BASED) ====================
def rule_based_chatbot(prompt: str) -> str:
    """Xử lý câu hỏi của người dùng dựa trên quy tắc từ khóa (Rules)."""
    text = prompt.lower().strip()

    # Luật 1: Giá cao nhất / Đắt nhất
    if any(k in text for k in ["cao nhất", "đắt nhất", "mắc nhất", "giá cao"]):
        max_m = max(MENU_DRINKS.items(), key=lambda x: x[1]["M"])
        max_l = max(MENU_DRINKS.items(), key=lambda x: x[1]["L"])
        return (
            f"🥤 Món có **giá cao nhất** tại quán là **{max_l[0]}**:\n"
            f"- Size M: **{max_m[1]['M']:,} VNĐ**\n"
            f"- Size L: **{max_l[1]['L']:,} VNĐ**"
        )

    # Luật 2: Giá thấp nhất / Rẻ nhất
    elif any(k in text for k in ["thấp nhất", "rẻ nhất", "giá rẻ", "giá thấp"]):
        min_m = min(MENU_DRINKS.items(), key=lambda x: x[1]["M"])
        min_l = min(MENU_DRINKS.items(), key=lambda x: x[1]["L"])
        return (
            f"🥤 Món có **giá thấp nhất** là **{min_m[0]}**:\n"
            f"- Size M: **{min_m[1]['M']:,} VNĐ**\n"
            f"- Size L: **{min_l[1]['L']:,} VNĐ**"
        )

    # Luật 3: Món nào ngọt / Tư vấn độ ngọt
    elif any(k in text for k in ["ngọt", "độ ngọt", "đường"]):
        return (
            "🧋 **Thông tin về độ ngọt các món:**\n"
            "- **Món ngọt đậm đà nhất:** *Sữa Tươi Trân Châu Đường Đen* (do có vị đường đen đặc trưng) và *Trà Sữa Matcha*.\n"
            "- **Món thanh mát, ít ngọt hơn:** *Trà Đào Cam Sả* và *Trà Trái Cây Nhiệt Đới*.\n"
            "💡 *Mẹo:* Bạn có thể chủ động chỉnh mức đường (30%, 50%, 70%) ở bảng đặt món để phù hợp với khẩu vị nhé!"
        )

    # Luật 4: Tư vấn topping phù hợp cho loại trà sữa
    elif any(
        k in text for k in ["topping", "kết hợp", "đi kèm", "nên dùng", "nên chọn"]
    ):
        matched_drink = None
        for drink in MENU_DRINKS.keys():
            if drink.lower() in text:
                matched_drink = drink
                break

        if matched_drink:
            toppings = ", ".join(TOPPING_RECOMMENDATIONS[matched_drink])
            return f"💡 Với **{matched_drink}**, bạn nên dùng kèm các topping sau để ngon nhất: **{toppings}**."
        else:
            return (
                "💡 **Gợi ý kết hợp topping phổ biến:**\n"
                "- **Trà sữa đậm vị (Truyền thống/Matcha/Ô Long):** Rất hợp với *Kem Cheese*, *Pudding trứng*, *Trân châu đen*.\n"
                "- **Trà trái cây (Đào cam sả/Nhiệt đới):** Hợp nhất với *Trân châu trắng* và *Thạch trái cây* ngon giòn thanh mát!"
            )

    # Luật 5: Lời chào hỏi
    elif any(k in text for k in ["hi", "hello", "chào", "xin chào"]):
        return "Xin chào! Bạn cần mình tư vấn chọn món, giá cả hay cách phối topping nào không?"

    # Mặc định khi không trùng khớp luật nào
    else:
        return (
            "🤖 Xin lỗi, mình chưa hiểu rõ ý bạn. Bạn có thể hỏi mình các câu như:\n"
            "- *Món nào giá cao nhất / rẻ nhất?*\n"
            "- *Món trà sữa nào ngọt?*\n"
            "- *Trà Sữa Matcha nên dùng topping nào?*\n"
            "- *Trà trái cây kết hợp topping gì ngon?*"
        )


# ==================== THANH BÊN (SIDEBAR): CHATBOT ====================
with st.sidebar:
    st.header("🤖 Chatbot Tư Vấn")
    st.caption("Hỏi đáp thông tin thực đơn & gợi ý chọn món")

    # Hiển thị lịch sử trò chuyện
    chat_container = st.container(height=350)
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Ô nhập tin nhắn người dùng
    if user_input := st.chat_input("Hỏi chatbot tại đây..."):
        # Lưu câu hỏi của người dùng
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        # Tạo phản hồi từ luật
        bot_response = rule_based_chatbot(user_input)
        st.session_state.chat_history.append(
            {"role": "assistant", "content": bot_response}
        )

        st.rerun()


# ==================== GIAO DIỆN CHÍNH ====================
# Hiển thị ảnh bìa nếu có (sử dụng try-except để tránh lỗi nếu thiếu file ảnh)
try:
    st.image("TRASUA.jpg.PNG", use_container_width=True)
except Exception:
    pass

st.title("🧋 Ứng Dụng Tính Hóa Đơn Quán Trà Sữa")
st.markdown("---")

col_input, col_summary = st.columns([1.2, 1])

# ==================== CỘT 1: NHẬP THÔNG TIN MÓN ====================
with col_input:
    st.header("📋 Nhập Thông Tin Đơn Hàng")

    # 1. Nhập tên khách hàng
    customer_name = st.text_input(
        "👤 Tên khách hàng:", placeholder="Nhập tên khách hàng..."
    )

    st.subheader("🥤 Chọn thức uống")

    # 2. Chọn loại trà sữa
    drink_name = st.selectbox("Chọn loại trà sữa:", list(MENU_DRINKS.keys()))

    # 3. Chọn size ly
    size = st.radio("Chọn size ly:", ["M", "L"], horizontal=True)
    base_price = MENU_DRINKS[drink_name][size]

    # 4. Mức độ đường và đá
    col_sugar, col_ice = st.columns(2)
    with col_sugar:
        sugar = st.select_slider(
            "Mức đường:",
            options=["0%", "30%", "50%", "70%", "100%"],
            value="100%",
        )
    with col_ice:
        ice = st.select_slider(
            "Mức đá:",
            options=["Không đá", "30%", "50%", "70%", "100%"],
            value="100%",
        )

    # 5. Chọn topping
    selected_toppings = st.multiselect(
        "Chọn topping (có thể chọn nhiều):",
        options=list(MENU_TOPPINGS.keys()),
        format_func=lambda x: f"{x} (+{MENU_TOPPINGS[x]:,}đ)",
    )

    # Tính giá topping
    topping_price = sum(MENU_TOPPINGS[top] for top in selected_toppings)

    # 6. Số lượng
    quantity = st.number_input(
        "Số lượng ly:", min_value=1, max_value=50, value=1, step=1
    )

    # Tính giá tiền cho món hiện tại
    unit_price = base_price + topping_price
    item_total = unit_price * quantity

    st.info(
        f"💰 **Đơn giá 1 ly (gồm topping):** {unit_price:,} VNĐ | **Thành tiền:** {item_total:,} VNĐ"
    )

    # 7. Nút THÊM MÓN
    if st.button(
        "➕ Thêm món vào đơn", type="primary", use_container_width=True
    ):
        if not customer_name.strip():
            st.error("⚠️ Vui lòng nhập Tên khách hàng trước khi thêm món!")
        else:
            st.session_state.cart.append(
                {
                    "Tên món": f"{drink_name} (Size {size})",
                    "Size": size,
                    "Mức đường/Đá": f"Đường: {sugar}, Đá: {ice}",
                    "Topping": (
                        ", ".join(selected_toppings)
                        if selected_toppings
                        else "Không"
                    ),
                    "Đơn giá": unit_price,
                    "Số lượng": quantity,
                    "Thành tiền": item_total,
                }
            )
            st.toast(
                f"Đã thêm {quantity} x {drink_name} vào đơn!", icon="✅"
            )

# ==================== CỘT 2: HIỂN THỊ CHI TIẾT & TỔNG TIỀN ====================
with col_summary:
    st.header("🛒 Đơn Hàng Hiện Tại")

    if customer_name.strip():
        st.markdown(f"**Khách hàng:** `{customer_name.strip()}`")
    else:
        st.caption("Chưa nhập tên khách hàng")

    if not st.session_state.cart:
        st.warning(
            "Đơn hàng chưa có món nào. Vui lòng chọn món và nhấn 'Thêm món vào đơn'."
        )
    else:
        # Bảng danh sách các món đã thêm
        df_cart = pd.DataFrame(st.session_state.cart)
        st.dataframe(
            df_cart[
                [
                    "Tên món",
                    "Mức đường/Đá",
                    "Topping",
                    "Số lượng",
                    "Thành tiền",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

        # Tính tổng tiền thanh toán
        grand_total = sum(
            item["Thành tiền"] for item in st.session_state.cart
        )

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
            pay_button = st.button(
                "💳 Thanh Toán & Xuất Hóa Đơn",
                type="primary",
                use_container_width=True,
            )

# ==================== XUẤT HÓA ĐƠN KHI BẤM THANH TOÁN ====================
if st.session_state.cart and "pay_button" in locals() and pay_button:
    st.balloons()
    st.success("🎉 Thanh toán thành công!")

    grand_total = sum(item["Thành tiền"] for item in st.session_state.cart)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # Hiển thị hóa đơn dạng khung giao diện
    bill_col1, bill_col2, bill_col3 = st.columns([1, 2, 1])
    with bill_col2:
        st.markdown(
            """
        <div style="text-align: center;">
            <h2>🧾 HÓA ĐƠN BÁN HÀNG</h2>
            <h4>🧋 QUÁN TRÀ SỮA HAPPY TEA</h4>
            <p><i>Địa chỉ: 123 Đường Sữa Tươi, Quận 1, TP. Hồ Chí Minh</i></p>
        </div>
        """,
            unsafe_allow_html=True,
        )

        st.write(f"**Tên khách hàng:** {customer_name}")
        st.write(
            f"**Thời gian:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        )
        st.write("---")

        # Bảng chi tiết hóa đơn
        for idx, item in enumerate(st.session_state.cart, 1):
            st.markdown(
                f"**{idx}. {item['Tên món']}** x **{item['Số lượng']}** = **{item['Thành tiền']:,} VNĐ**"
            )
            st.caption(
                f"└ Yêu cầu: {item['Mức đường/Đá']} | Topping: {item['Topping']}"
            )

        st.write("---")
        st.markdown(
            f"### 🎯 TỔNG CỘNG THANH TOÁN: <span style='color:red;'>{grand_total:,} VNĐ</span>",
            unsafe_allow_html=True,
        )
        st.write("---")
        st.markdown(
            "<p style='text-align: center;'><i>Cảm ơn quý khách và hẹn gặp lại! 🙏</i></p>",
            unsafe_allow_html=True,
        )
