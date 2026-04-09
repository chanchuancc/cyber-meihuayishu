import streamlit as st
import datetime
import time
import random
import os
from borax.calendars.lunardate import LunarDate
from meihua_data import BAGUA, GUA_64, BRANCHES, BRANCH_MAP

# --- 洞穴配置与石头样式 (v1.9.5 Imperial Total Blackout) ---
st.set_page_config(page_title="梅花易数", page_icon="🧧", layout="centered")

# --- 暴力消白令: AGGRESSIVE CSS OVERRIDE ---
total_blackout_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@200;400;700&display=swap');

    /* 1. 根基玄曜 */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stToolbar"] {
        background-color: #050505 !important;
        color: #d4af37 !important;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* 2. 暴力消除所有白框背景 */
    div[data-testid="stTextInput"] fieldset,
    div[data-testid="stTextInput"] div,
    div[data-testid="stTextInput"] input,
    div[data-baseweb="input"],
    div[data-baseweb="base-input"],
    div[role="presentation"],
    fieldset,
    .st-ae, .st-af, .st-ag, .st-ah, .st-ai, .st-aj, .st-ak, .st-al, .st-am, .st-an, .st-ao {
        background-color: transparent !important;
        background: transparent !important;
        border-color: transparent !important;
        box-shadow: none !important;
        color: #d4af37 !important;
    }

    /* 3. 帝国入口长条 (Oracle Capsule) */
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextInput"]) {
        background: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 60px !important;
        padding: 5px 25px !important;
        box-shadow: 0 15px 50px rgba(0,0,0,0.9) !important;
        align-items: center !important;
        margin-bottom: 2.5rem !important;
        transition: all 0.4s ease;
    }
    div[data-testid="stHorizontalBlock"]:has(div[data-testid="stTextInput"]):focus-within {
        border-color: #d4af37 !important;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.3) !important;
    }

    /* 4. 输入文字高亮 */
    div[data-testid="stTextInput"] input {
        color: #fff !important;
        font-size: 1.2rem !important;
        background: transparent !important;
    }
    div[data-testid="stTextInput"] label { display: none !important; }

    /* 5. 标题与落梅 */
    h1 {
        color: #d4af37 !important;
        letter-spacing: 0.8em !important;
        text-align: center !important;
        text-shadow: 0 0 40px rgba(212, 175, 55, 0.4) !important;
        font-weight: 200 !important;
        font-size: 3.8rem !important;
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

    /* 6. 结果神龛 */
    .gua-card {
        background: rgba(15, 15, 15, 0.98) !important;
        border: 1px solid rgba(212, 175, 55, 0.15) !important;
        padding: 3.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 40px 120px rgba(0,0,0,1) !important;
        margin-top: 2rem !important;
        animation: emerge 1.5s cubic-bezier(0.2, 0, 0.2, 1);
    }
    @keyframes emerge { from { opacity: 0; transform: translateY(50px); filter: blur(20px); } to { opacity: 1; transform: translateY(0); filter: blur(0); } }

    /* 7. Confirm Button Style */
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"] {
        background: transparent !important;
        border: none !important;
        color: #d4af37 !important;
        width: 50px !important;
        height: 50px !important;
        min-width: 50px !important;
        font-size: 1.8rem !important;
        transition: transform 0.3s ease !important;
    }
    div[data-testid="stHorizontalBlock"] button[data-testid="baseButton-secondary"]:hover {
        transform: scale(1.2) translateX(5px) !important;
        background: transparent !important;
    }

    #MainMenu, footer, header { visibility: hidden !important; }
</style>
"""
st.markdown(total_blackout_css, unsafe_allow_html=True)

# 撒梅花
for _ in range(12):
    left, dur, delay = random.randint(0, 100), random.randint(10, 25), random.randint(0, 15)
    st.markdown(f'<div class="petal" style="left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s;">🌸</div>', unsafe_allow_html=True)

# --- 真实语音逻辑 (Real Voice API) ---
voice_val = st.query_params.get("v", "")
voice_html = """
<div style="display: flex; justify-content: center; align-items: center; height: 50px;">
    <button id="mic" style="background: transparent; border: none; cursor: pointer; padding: 0;">
        <svg id="mic-icon" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#444" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="transition: 0.3s;">
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
        if (!('webkitSpeechRecognition' in window)) { alert("浏览器不支持语音感应"); return; }
        const rec = new webkitSpeechRecognition();
        rec.lang = 'zh-CN';
        rec.onstart = () => { icon.style.stroke = '#d4af37'; icon.style.filter = 'drop-shadow(0 0 10px #d4af37)'; };
        rec.onresult = (e) => {
            const t = e.results[0][0].transcript;
            const url = new URL(window.parent.location.href);
            url.searchParams.set('v', t);
            window.parent.location.href = url.href;
        };
        rec.onend = () => { icon.style.stroke = '#444'; icon.style.filter = 'none'; };
        rec.start();
    };
</script>
"""

# --- 祭坛交互 ---
st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown('<div class="ritual-hint">屏息凝神 · 默念所求</div>', unsafe_allow_html=True)

col_in, col_mic, col_go = st.columns([8, 1, 1])
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
        placeholder = st.empty()
        msgs = ["📡 捕捉四柱波段...", "🌑 读取农历星历...", "⚡ 二进制位运算...", "👁️ 观测平行路径...", "🔮 提取变卦能量...", "✨ 天机即将揭示..."]
        start = time.time()
        while time.time() - start < 15:
            idx = int((time.time() - start) / 2.5) % len(msgs)
            placeholder.markdown(f'<div style="text-align: center; color: #d4af37; font-size: 1.6rem; margin-top: 3rem; letter-spacing: 0.2em; font-weight: 200;">{msgs[idx]}</div>', unsafe_allow_html=True)
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
            <div style="text-align: center; font-family: monospace; color: #1a1a1a; font-size: 0.8rem; margin-bottom: 3rem; letter-spacing: 3px;">
                CALIBRATED_TRACE: ({y_n}+{m_n}+{d_n}) % 8 = {up_idx} | {now.strftime('%H:%M')}
            </div>
            <div style="text-align: center; color: #d4af37; font-size: 5rem; font-weight: 700; text-shadow: 0 0 50px rgba(212,175,55,0.6); letter-spacing: 0.2em;">
                {gua_name}
            </div>
            <div style="margin-top: 4rem; border-top: 1px solid #111; padding-top: 3rem; color: #888; text-align: center; line-height: 2.2; font-size: 1.3rem;">
                <span style="color: #333; font-size: 0.8rem; letter-spacing: 5px;">[ 问 卜 ]</span><br>
                <span style="color: #fff;">{question}</span><br><br>
                一花开五叶，结果自然成。<br>
                动爻在第 {move} 爻，天机流转，顺势而为。
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<p style='text-align: center; color: #111; font-size: 0.7rem; margin-top: 8rem; letter-spacing: 0.8em;'>一 念 起 · 万 法 生</p>", unsafe_allow_html=True)
