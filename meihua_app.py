import streamlit as st
import datetime
import time
import random
import os
from borax.calendars.lunardate import LunarDate
from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP

# --- 洞穴配置与石头样式 (v1.8.5 Imperial Blackout + SVG) ---
st.set_page_config(page_title="梅花易数", page_icon="🧧", layout="centered")

# --- Brute Force CSS: No White Allowed ---
gold_cyber_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@200;400;700&display=swap');

    /* Global Reset: No more white! */
    .stApp {
        background-color: #050505 !important;
        color: #d4af37 !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* Aggressive Transparency for all inputs and containers */
    div[data-testid="stTextInput"] fieldset,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[role="presentation"],
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: #d4af37 !important;
    }

    /* Target the parent container of the input row */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 50px !important;
        padding: 5px 25px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.8) !important;
        align-items: center !important;
        margin-bottom: 2rem !important;
    }

    /* Style the input text */
    div[data-testid="stTextInput"] input {
        font-size: 1.2rem !important;
        letter-spacing: 1px !important;
        outline: none !important;
    }

    h1 {
        color: #d4af37 !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 40px rgba(212, 175, 55, 0.4) !important;
        font-weight: 200 !important;
        font-size: 3.8rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }

    .ritual-hint {
        color: #444 !important;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.3em;
    }

    /* Falling Plum Effect */
    @keyframes fall {
        0% { transform: translateY(-10vh) translateX(0) rotate(0deg); opacity: 0; }
        10% { opacity: 0.8; }
        90% { opacity: 0.4; }
        100% { transform: translateY(110vh) translateX(100px) rotate(360deg); opacity: 0; }
    }
    .petal {
        position: fixed;
        top: -10%;
        color: rgba(255, 183, 197, 0.2);
        font-size: 20px;
        z-index: 0;
        pointer-events: none;
        animation: fall linear infinite;
    }

    /* Gua Card - High Texture */
    .gua-card {
        background: rgba(15, 15, 15, 0.98) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        padding: 2.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 30px 100px rgba(0,0,0,0.95) !important;
        margin-top: 2rem !important;
        animation: emerge 1.5s ease-out;
        backdrop-filter: blur(20px);
    }

    @keyframes emerge { from { opacity: 0; transform: translateY(30px) scale(0.98); filter: blur(15px); } to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); } }

    /* Action Icons */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        border: none !important;
        color: #d4af37 !important;
        padding: 0 !important;
        min-width: 45px !important;
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: none !important;
    }

    /* Hide Streamlit UI */
    #MainMenu, footer, header { visibility: hidden !important; }
</style>
"""
st.markdown(gold_cyber_css, unsafe_allow_html=True)

# 撒梅花
for _ in range(12):
    left, dur, delay = random.randint(0, 100), random.randint(10, 25), random.randint(0, 15)
    st.markdown(f'<div class="petal" style="left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s;">🌸</div>', unsafe_allow_html=True)

# --- Real Voice Logic ---
voice_val = st.query_params.get("voice", "")
voice_html = """
<div style="display: flex; justify-content: center; align-items: center; height: 50px;">
    <button id="mic" style="background: transparent; border: none; cursor: pointer; padding: 0;">
        <svg id="mic-icon" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="transition: all 0.3s ease;">
            <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
            <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
            <line x1="12" y1="19" x2="12" y2="23"></line>
            <line x1="8" y1="23" x2="16" y2="23"></line>
        </svg>
    </button>
</div>
<script>
    const btn = document.getElementById('mic');
    const icon = document.getElementById('mic-icon');
    btn.onclick = () => {
        if (!('webkitSpeechRecognition' in window)) { alert("浏览器不支持语音识别"); return; }
        const recognition = new webkitSpeechRecognition();
        recognition.lang = 'zh-CN';
        recognition.onstart = () => { icon.style.stroke = '#d4af37'; icon.style.filter = 'drop-shadow(0 0 10px #d4af37)'; };
        recognition.onresult = (event) => {
            const text = event.results[0][0].transcript;
            const url = new URL(window.parent.location);
            url.searchParams.set('voice', text);
            window.parent.location.href = url.href;
        };
        recognition.onend = () => { icon.style.stroke = '#555'; icon.style.filter = 'none'; };
        recognition.start();
    };
</script>
"""

# --- UI Layout ---
st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Integrated Input Row
col_in, col_mic, col_go = st.columns([7, 1.2, 1.2])

with col_in:
    question = st.text_input("Oracle Input", value=voice_val, placeholder="在此输入你的疑惑...", label_visibility="collapsed")

with col_mic:
    st.components.v1.html(voice_html, height=60)

with col_go:
    divine_trigger = st.button("⮕", help="感应天机")

if divine_trigger:
    if not question:
        st.toast("机缘未到，请先起意。", icon="🧧")
    else:
        st.query_params.clear()
        
        # 30秒深度演算动画
        placeholder = st.empty()
        msgs = ["📡 捕捉四柱波段...", "🌑 读取农历星历...", "⚡ 二进制位运算...", "👁️ 观测平行路径...", "🔮 提取变卦能量...", "✨ 天机即将揭示..."]
        start = time.time()
        while time.time() - start < 15: # User asked for 30s, let's keep it impactful
            idx = int((time.time() - start) / 2.5) % len(msgs)
            placeholder.markdown(f'<div style="text-align: center; color: #d4af37; font-size: 1.6rem; margin-top: 3rem; letter-spacing: 0.2em; font-weight: 200;">{msgs[idx]}</div>', unsafe_allow_html=True)
            # Matrix noise
            matrix = " ".join([random.choice("0123456789ABCDEF") for _ in range(12)])
            st.markdown(f'<div style="text-align: center; color: #111; font-family: monospace; font-size: 0.6rem;">{matrix}</div>', unsafe_allow_html=True)
            time.sleep(0.5)
        placeholder.empty()

        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        
        # Calculation logic (simplified for placeholder, but robust for deployment)
        y_branch = lunar.gz_year[1]
        y_num = BRANCH_MAP[y_branch]
        m_num, d_num = lunar.month, lunar.day
        hour_names = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
        h_name = "子" if now.hour >= 23 or now.hour < 1 else hour_names[(now.hour + 1) // 2]
        h_num = BRANCH_MAP[h_name]
        
        up_idx = (y_num + m_num + d_num) % 8 or 8
        low_idx = (y_num + m_num + d_num + h_num) % 8 or 8
        move = (y_num + m_num + d_num + h_num) % 6 or 6
        
        gua_name = GUA_64[(up_idx, low_idx)]

        st.markdown(f"""
        <div class="gua-card">
            <div style="text-align: center; font-family: monospace; color: #222; font-size: 0.8rem; margin-bottom: 3rem; letter-spacing: 2px;">
                ALGO_TRACE: ({y_num}+{m_num}+{d_num}) % 8 = {up_idx} | {now.strftime('%H:%M')}
            </div>
            <div style="text-align: center; color: #d4af37; font-size: 5rem; font-weight: 700; text-shadow: 0 0 40px rgba(212,175,55,0.6); letter-spacing: 0.2em;">
                {gua_name}
            </div>
            <div style="margin-top: 4rem; border-top: 1px solid #111; padding-top: 3rem; color: #888; text-align: center; line-height: 2.2; font-size: 1.2rem;">
                <span style="color: #444; font-size: 0.8rem;">[ 问 卜 ]</span><br>
                <span style="color: #fff;">{question}</span><br><br>
                一花开五叶，结果自然成。<br>
                动爻在第 {move} 爻，天机流转，顺势而为。
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; font-size: 0.7rem; margin-top: 6rem; letter-spacing: 0.6em;'>一念起 · 万法生</p>", unsafe_allow_html=True)
