import streamlit as st
import re

# Page Configuration
st.set_page_config(page_title="دستیار خروج هوشمند فارکس", page_icon="🎯", layout="centered")

# Custom CSS for Persian RTL and Modern UI
st.markdown("""
<style>
    @import url('https://v1.fontapi.ir/css/Vazir');
    html, body, [class*="css"] {
        font-family: 'Vazir', sans-serif;
        direction: rtl;
        text-align: right;
    }
    .stButton>button {
        width: 100%;
        background-color: #1F4E78;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        height: 50px;
        font-size: 16px;
    }
    .card-lot {
        background-color: #e8f0fe;
        border-right: 6px solid #1a73e8;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        color: #174ea6;
    }
    .card-tp1 {
        background-color: #e6f4ea;
        border-right: 6px solid #34a853;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #137333;
    }
    .card-tp2 {
        background-color: #feefc3;
        border-right: 6px solid #f9ab00;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #b06000;
    }
    .card-tp3 {
        background-color: #fce8e6;
        border-right: 6px solid #ea4335;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        color: #c5221f;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 دستیار هوشمند خروج و مدیریت ریسک فارکس")
st.caption("نسخه وب/موبایل با پردازش خودکار متن سیگنال تلگرام")

# Sidebar Settings
st.sidebar.header("⚙️ تنظیمات حساب معاملاتی")
balance = st.sidebar.number_input("موجودی حساب ($):", min_value=10.0, value=1000.0, step=50.0)
risk_pct = st.sidebar.number_input("درصد ریسک در هر معامله (%):", min_value=0.1, value=1.0, step=0.1)

risk_amount = balance * (risk_pct / 100.0)
st.sidebar.info(f"مبلغ ریسک دلاری مجاز: **${risk_amount:.2f}**")

# Input Section: Paste Signal
st.subheader("📋 کپی و پیست متن سیگنال تلگرام")
raw_signal = st.text_area(
    "متن سیگنال را مستقیم کپی کرده و اینجا پیست کنید:",
    height=130,
    placeholder="مثال:\nXAUUSD\nSELL LIMIT\nنقطه ورود: 4062\nحد ضرر (SL) : 4069\nحد سود (TP) : 4035"
)

def parse_signal(text):
    if not text.strip():
        return None
    
    # Direction Detection
    direction = "SELL" if re.search(r'SELL|فروش', text, re.IGNORECASE) else "BUY"
    
    # Symbol Detection
    symbol = "GOLD" if re.search(r'XAU|GOLD|طلا', text, re.IGNORECASE) else "FOREX"
    
    # Label extraction using Regex
    sl_match = re.search(r'(?:SL|استاپ|حد ضرر|Stop)[\s:]*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    tp_match = re.search(r'(?:TP|تارگت|حد سود|Target)[\s:]*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    entry_match = re.search(r'(?:Entry|ورود|نقطه|Price)[\s:]*(\d+(?:\.\d+)?)', text, re.IGNORECASE)
    
    entry = float(entry_match.group(1)) if entry_match else None
    sl = float(sl_match.group(1)) if sl_match else None
    tp = float(tp_match.group(1)) if tp_match else None
    
    # Fallback to positional numbers if labels not found
    numbers = [float(n) for n in re.findall(r'\d+(?:\.\d+)?', text)]
    if not entry and len(numbers) >= 1:
        entry = numbers[0]
    if not sl and len(numbers) >= 2:
        sl = numbers[1]
    if not tp and len(numbers) >= 3:
        tp = numbers[2]
        
    return {
        "direction": direction,
        "symbol": symbol,
        "entry": entry,
        "sl": sl,
        "tp": tp
    }

if st.button("🚀 محاسبه هوشمند نقشه خروج"):
    parsed = parse_signal(raw_signal)
    if parsed and parsed["entry"] and parsed["sl"]:
        entry = parsed["entry"]
        sl = parsed["sl"]
        tp = parsed["tp"]
        direction = parsed["direction"]
        symbol = parsed["symbol"]
        
        sl_distance = abs(entry - sl)
        multiplier = 100 if symbol == "GOLD" else 10
        
        # Calculate Lot Size
        lot_size = risk_amount / (sl_distance * multiplier) if sl_distance > 0 else 0.01
        lot_size = max(0.01, round(lot_size, 2))
        
        # Calculate Exit Targets
        if direction == "BUY":
            tp1 = entry + sl_distance
            tp2 = entry + (2 * sl_distance)
        else:
            tp1 = entry - sl_distance
            tp2 = entry - (2 * sl_distance)
            
        tp3 = tp if tp else (entry + (3 * sl_distance) if direction == "BUY" else entry - (3 * sl_distance))
        
        # Display Results
        st.markdown(f"""
        <div class="card-lot">
            <h3>📊 حجم پیشنهادی معامله: {lot_size:.2f} لات</h3>
            <p><b>نماد:</b> {'طلا (XAUUSD)' if symbol == 'GOLD' else 'جفت‌ارز'} | <b>جهت:</b> {direction} | <b>مبلغ ریسک:</b> ${risk_amount:.2f} (۱٪)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🎯 کارت‌های راهنمای خروج پله‌ای")
        
        st.markdown(f"""
        <div class="card-tp1">
            <h4>🟢 TP1 (ریسک‌فری کامل): {tp1:.2f} (R/R 1:1)</h4>
            <p><b>اقدام دستی:</b> ۵۰٪ معامله (حدود {max(0.01, round(lot_size*0.5, 2))} لات) را ببندید و SL را به نقطه ورود ({entry:.2f}) بگذارید.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card-tp2">
            <h4>🟡 TP2 (سود ۱:۲): {tp2:.2f} (R/R 1:2)</h4>
            <p><b>اقدام دستی:</b> ۳۰٪ دیگر معامله (حدود {max(0.01, round(lot_size*0.3, 2))} لات) را در این قیمت ببندید.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="card-tp3">
            <h4>🔴 TP3 (تارگت کانال): {tp3:.2f}</h4>
            <p><b>اقدام دستی:</b> ۲۰٪ باقی‌مانده را تا رسیدن به این قیمت همراهی کنید.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.warning("⏱️ **قانون خروج زمانی:** اگر معامله فعال شد و بعد از ۲ الی ۳ ساعت درجا زد و به TP1 نرسید، معامله را دستی ببندید.")
    else:
        st.error("❌ نتوانستیم قیمت ورود و حد ضرر را از متن تشخیص دهیم. لطفاً متن سیگنال را بفرستید.")
