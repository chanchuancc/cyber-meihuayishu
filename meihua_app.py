import streamlit as st
import datetime
import time
import random
import os
from borax.calendars.lunardate import LunarDate
from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP
from streamlit_mic_recorder import speech_to_text

# --- 洞穴配置与石头样式 (v2.0.0 Imperial Blackout) ---
st.set_page_config(page_title="梅花易数", page_icon="🧧", layout="centered")

# --- NUCLEAR CSS OVERRIDE: Eliminate ALL white backgrounds ---
gold_cyber_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@200;400;700&display=swap');

    /* 1. Force the entire page to be dark */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp {
        background-color: #050505 !important;
        background: #050505 !important;
        color: #d4af37 !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }

    /* 2. Target specific elements that might have white backgrounds */
    div[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
        display: none !important;
    }

    /* 3. Kill all white backgrounds in inputs and containers */
    fieldset, 
    div[data-testid="stTextInput"] *, 
    div[data-baseweb="input"] *, 
    div[data-baseweb="base-input"] *,
    div[role="presentation"] *,
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao {
        background-color: transparent !important;
        background: transparent !important;
        color: #d4af37 !important;
        border-color: transparent !important;
        box-shadow: none !important;
    }

    /* 4. The Oracle Bar (Capsule) */
    div[data-testid="stHorizontalBlock"] {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        border-radius: 60px !important;
        padding: 5px 30px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.8) !important;
        align-items: center !important;
        margin-bottom: 2.5rem !important;
        transition: all 0.4s ease;
    }

    /* 5. Input Style */
    div[data-testid="stTextInput"] input {
        font-size: 1.2rem !important;
        caret-color: #d4af37 !important;
        outline: none !important;
    }

    /* 6. Typography & Petals */
    h1 {
        color: #d4af37 !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 40px rgba(212, 175, 55, 0.4) !important;
        font-weight: 200 !important;
        font-size: 3.5rem !important;
        margin-top: 2rem !important;
    }
    .ritual-hint {
        color: #444 !important;
        font-size: 1.1rem;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 0.3em;
    }
    @keyframes fall {
        0% { transform: translateY(-10vh) translateX(0) rotate(0deg); opacity: 0; }
        10% { opacity: 0.8; }
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

    /* 7. Result Card */
    .gua-card {
        background: rgba(15, 15, 15, 0.98) !important;
        border: 1px solid rgba(212, 175, 55, 0.1) !important;
        padding: 3rem !important;
        border-radius: 12px !important;
        box-shadow: 0 40px 120px rgba(0,0,0,1) !important;
        margin-top: 2rem !important;
        animation: emerge 1.5s cubic-bezier(0.2, 0, 0.2, 1);
    }
    @keyframes emerge { from { opacity: 0; transform: translateY(50px); filter: blur(20px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }

    /* 8. Mic Button */
    div.st-emotion-cache-1pxm8lv, button[kind="secondary"] {
        background-color: transparent !important;
        border: none !important;
        color: #d4af37 !important;
    }

    /* Hide Streamlit Chrome */
    #MainMenu, footer, header { visibility: hidden !important; }
</style>
"""
st.markdown(gold_cyber_css, unsafe_allow_html=True)

# 撒梅花
for _ in range(12):
    left, dur, delay = random.randint(0, 100), random.randint(10, 25), random.randint(0, 15)
    st.markdown(f'<div class="petal" style="left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s;">🌸</div>', unsafe_allow_html=True)

# --- UI Layout ---
st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

# Integrated Input Row
col_in, col_mic, col_go = st.columns([7, 1.5, 1.2])

with col_mic:
    # Real Speech-to-Text Component
    text_from_voice = speech_to_text(language='zh-CN', start_prompt="🎙️", stop_prompt="⏹️", key='mic_meihua')

with col_in:
    if text_from_voice:
        st.session_state.meihua_q = text_from_voice
    question = st.text_input("Oracle Input", value=st.session_state.get('meihua_q', ""), placeholder="在此感应因果...", label_visibility="collapsed")

with col_go:
    divine_trigger = st.button("⮕", help="感应天机")

if divine_trigger:
    if not question:
        st.toast("机缘未到，请先起意。", icon="🧧")
    else:
        placeholder = st.empty()
        msgs = ["📡 捕捉四柱波段...", "🌑 读取农历星历...", "⚡ 二进制位运算...", "✨ 天机即将揭示..."]
        start = time.time()
        while time.time() - start < 10:
            idx = int((time.time() - start) / 2.5) % len(msgs)
            placeholder.markdown(f'<div style="text-align: center; color: #d4af37; font-size: 1.6rem; margin-top: 3rem;">{msgs[idx]}</div>', unsafe_allow_html=True)
            time.sleep(0.5)
        placeholder.empty()

        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        y_n = BRANCH_MAP[lunar.gz_year[1]]
        m_n, d_n = lunar.month, lunar.day
        h_n = BRANCH_MAP["子"] if now.hour >= 23 or now.hour < 1 else BRANCH_MAP[BRANCHES[(now.hour + 1) // 2]]
        
        up_idx = (y_n + m_n + d_n) % 8 or 8
        low_idx = (y_n + m_n + d_n + h_n) % 8 or 8
        move = (y_n + m_n + d_n + h_n) % 6 or 6
        gua_name = GUA_64[(up_idx, low_idx)]

        st.markdown(f"""
        <div class="gua-card">
            <div style="text-align: center; color: #d4af37; font-size: 5rem; font-weight: 700; text-shadow: 0 0 50px rgba(212,175,55,0.6); letter-spacing: 0.2em;">
                {gua_name}
            </div>
            <div style="margin-top: 4rem; border-top: 1px solid #111; padding-top: 3rem; color: #888; text-align: center; line-height: 2.2; font-size: 1.3rem;">
                <span style="color: #333; font-size: 0.8rem; letter-spacing: 5px;">[ 问 卜 ]</span><br>
                <span style="color: #fff;">{question}</span><br><br>
                一花开五叶，结果自然成。
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; font-size: 0.7rem; margin-top: 8rem;'>一 念 起 · 万 法 生</p>", unsafe_allow_html=True)
