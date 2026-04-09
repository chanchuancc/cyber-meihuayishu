import streamlit as st
import datetime
import time
import random
import json
import os
from borax.calendars.lunardate import LunarDate

# --- 洞穴配置与石头样式 (v1.4.0 Cavemen Refined) ---
st.set_page_config(page_title="梅花易数", page_icon="🌸", layout="centered")

# 石头刻字 CSS
cave_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@300;700&display=swap');

    /* 洞穴背景：玄色渐变 */
    .stApp {
        background: radial-gradient(circle at center, #1a1a1a 0%, #050505 100%);
        color: #d4af37;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }

    /* 落下梅花：飘啊飘 */
    @keyframes fall {
        0% { transform: translateY(-10vh) translateX(0) rotate(0deg); opacity: 1; }
        100% { transform: translateY(100vh) translateX(100px) rotate(360deg); opacity: 0; }
    }
    .petal {
        position: fixed;
        top: -10%;
        color: #ffb7c5;
        font-size: 20px;
        user-select: none;
        z-index: 0;
        pointer-events: none;
        animation: fall linear infinite;
    }

    /* 标题：大，稳，没虚的 */
    h1 {
        color: #d4af37;
        letter-spacing: 0.5em;
        text-align: center;
        margin-top: 1rem !important;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
    }

    /* 输入框：石洞感 */
    .stTextArea label, .stTextInput label {
        color: #8a7b48 !important;
        font-size: 1.1rem !important;
        text-align: center;
        display: block;
        width: 100%;
    }
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(20, 20, 20, 0.9) !important;
        color: #d4af37 !important;
        border: 1px solid #4a3f21 !important;
        border-radius: 4px !important;
        text-align: center;
    }

    /* 按钮：中间，一排，有力 */
    .stButton {
        display: flex;
        justify-content: center;
        margin-top: 1rem;
    }
    .stButton > button {
        background-color: rgba(212, 175, 55, 0.1);
        color: #d4af37;
        border: 2px solid #d4af37;
        border-radius: 4px;
        padding: 1rem 6rem;
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 0.8em;
        width: 100%;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background-color: #d4af37;
        color: #000;
        box-shadow: 0 0 30px #d4af37;
    }

    /* 卦象卡片：像祭坛上的石头 */
    .gua-container {
        display: flex;
        justify-content: center;
        gap: 2rem;
        margin-top: 2rem;
        flex-wrap: wrap;
    }
    .gua-card {
        background: rgba(30, 30, 30, 0.8);
        border: 1px solid #4a3f21;
        padding: 1.5rem;
        width: 200px;
        text-align: center;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    .gua-symbol {
        font-size: 4rem;
        line-height: 1;
        margin: 1rem 0;
        color: #fff;
    }
    .gua-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #d4af37;
    }

    /* 演算文字：主次分明 */
    .trace {
        color: #6a5a2a;
        font-size: 0.9rem;
        text-align: center;
        margin: 1rem 0;
        font-family: monospace;
    }
    .important {
        color: #d4af37;
        font-weight: 700;
    }

    #MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(cave_css, unsafe_allow_html=True)

# 撒梅花
for _ in range(15):
    left = random.randint(0, 100)
    dur = random.randint(5, 15)
    delay = random.randint(0, 10)
    st.markdown(f'<div class="petal" style="left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s;">🌸</div>', unsafe_allow_html=True)

# --- 搬运数据字典 (Cave Data) ---

BAGUA = {
    1: {"name": "乾", "symbol": "☰", "lines": [1, 1, 1], "nature": "天"},
    2: {"name": "兑", "symbol": "☱", "lines": [1, 1, 0], "nature": "泽"},
    3: {"name": "离", "symbol": "☲", "lines": [1, 0, 1], "nature": "火"},
    4: {"name": "震", "symbol": "☳", "lines": [1, 0, 0], "nature": "雷"},
    5: {"name": "巽", "symbol": "☴", "lines": [0, 1, 1], "nature": "风"},
    6: {"name": "坎", "symbol": "☵", "lines": [0, 1, 0], "nature": "水"},
    7: {"name": "艮", "symbol": "☶", "lines": [0, 0, 1], "nature": "山"},
    8: {"name": "坤", "symbol": "☷", "lines": [0, 0, 0], "nature": "地"}
}

GUA_64 = {
    (1, 1): "乾为天", (1, 2): "天泽履", (1, 3): "天火同人", (1, 4): "天雷无妄", (1, 5): "天风姤", (1, 6): "天水讼", (1, 7): "天山遁", (1, 8): "天地否",
    (2, 1): "泽天夬", (2, 2): "兑为泽", (2, 3): "泽火革", (2, 4): "泽雷随", (2, 5): "泽风大过", (2, 6): "泽水困", (2, 7): "泽山咸", (2, 8): "泽地萃",
    (3, 1): "火天大有", (3, 2): "火泽睽", (3, 3): "离为火", (3, 4): "火雷噬嗑", (3, 5): "火风鼎", (3, 6): "火水未济", (3, 7): "火山旅", (3, 8): "火地晋",
    (4, 1): "雷天大壮", (4, 2): "雷泽归妹", (4, 3): "雷火丰", (4, 4): "震为雷", (4, 5): "雷风恒", (4, 6): "雷水解", (4, 7): "雷山小过", (4, 8): "雷地豫",
    (5, 1): "风天小畜", (5, 2): "风泽中孚", (5, 3): "风火家人", (5, 4): "风雷益", (5, 5): "巽为风", (5, 6): "风水涣", (5, 7): "风山渐", (5, 8): "风地观",
    (6, 1): "水天需", (6, 2): "水泽节", (6, 3): "水火既济", (6, 4): "水雷屯", (6, 5): "水风井", (6, 6): "坎为水", (6, 7): "水山蹇", (6, 8): "水地比",
    (7, 1): "山天大畜", (7, 2): "山泽损", (7, 3): "山火贲", (7, 4): "山雷颐", (7, 5): "山风蛊", (7, 6): "山水蒙", (7, 7): "艮为山", (7, 8): "山地剥",
    (8, 1): "地天泰", (8, 2): "地泽临", (8, 3): "地火明夷", (8, 4): "地雷复", (8, 5): "地风升", (8, 6): "地水师", (8, 7): "地山谦", (8, 8): "坤为地"
}

DIZHI_MAP = {"子": 1, "丑": 2, "寅": 3, "卯": 4, "辰": 5, "巳": 6, "午": 7, "未": 8, "申": 9, "酉": 10, "戌": 11, "亥": 12}
DIZHI_NAMES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# --- 石头逻辑 (Cave Logic) ---

def get_shichen_num(hour):
    if hour >= 23 or hour < 1: return 1
    return (hour + 1) // 2 + 1

def get_gua_id(lines):
    for k, v in BAGUA.items():
        if v["lines"] == lines: return k
    return 1

# --- 祭坛交互 (UI) ---

st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)

st.markdown('<div style="text-align: center; color: #8a7b48; margin-bottom: 0.5rem;">屏息凝神，默念心中所求...</div>', unsafe_allow_html=True)
question = st.text_input("问卜之事", placeholder="在此输入你的疑惑", label_visibility="collapsed")

if st.button("感 应 天 机"):
    if not question:
        st.warning("没写问啥，占不了！")
    else:
        # 30秒磨石器动画
        placeholder = st.empty()
        start = time.time()
        msgs = ["打磨石器...", "观察星空...", "采集梅花...", "捕捉风声...", "占卜中...", "快好了...", "天意降临！"]
        while time.time() - start < 30:
            idx = int((time.time() - start) / 4) % len(msgs)
            placeholder.markdown(f'<div class="trace" style="font-size: 1.5rem;">{msgs[idx]}</div>', unsafe_allow_html=True)
            time.sleep(0.5)
        placeholder.empty()

        # 开始算卦
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        
        y_gz = lunar.year_gz[1]
        y_n = DIZHI_MAP[y_gz]
        m_n = lunar.month
        d_n = lunar.day
        h_n = get_shichen_num(now.hour)

        # 梅花公式
        up = (y_n + m_n + d_n) % 8 or 8
        low = (y_n + m_n + d_n + h_n) % 8 or 8
        move = (y_n + m_n + d_n + h_n) % 6 or 6

        # 推演
        orig_name = GUA_64[(up, low)]
        orig_lines = BAGUA[low]["lines"] + BAGUA[up]["lines"]
        
        # 互卦
        mut_l = get_gua_id(orig_lines[1:4])
        mut_u = get_gua_id(orig_lines[2:5])
        mut_name = GUA_64[(mut_u, mut_l)]
        
        # 变卦
        trans_lines = list(orig_lines)
        trans_lines[move-1] = 1 - trans_lines[move-1]
        trans_l = get_gua_id(trans_lines[0:3])
        trans_u = get_gua_id(trans_lines[3:6])
        trans_name = GUA_64[(trans_u, trans_l)]

        # 展示
        st.markdown(f'<div class="trace">公历: <span class="important">{now.strftime("%Y-%m-%d %H:%M")}</span> | 农历: <span class="important">{lunar.strftime("%Y-%L%M-%D")}</span> {DIZHI_NAMES[h_n-1]}时</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="trace">演算: 上卦({y_n}+{m_n}+{d_n})%8={up} | 下卦({y_n}+{m_n}+{d_n}+{h_n})%8={low} | 动爻={move}</div>', unsafe_allow_html=True)

        st.markdown('<div class="gua-container">', unsafe_allow_html=True)
        for label, name, u_id, l_id in [("本卦", orig_name, up, low), ("互卦", mut_name, mut_u, mut_l), ("变卦", trans_name, trans_u, trans_l)]:
            st.markdown(f"""
            <div class="gua-card">
                <div style="color: #6a5a2a; font-size: 0.8rem;">{label}</div>
                <div class="gua-name">{name}</div>
                <div class="gua-symbol">{BAGUA[u_id]["symbol"]}<br>{BAGUA[l_id]["symbol"]}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div style="text-align: center; margin-top: 1rem; color: #d4af37; font-size: 1.2rem;">第 <span style="font-size: 2rem;">{move}</span> 爻动</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background: rgba(20,20,20,0.8); padding: 2rem; margin-top: 2rem; border-radius: 8px; border: 1px solid #4a3f21;">
            <div style="color: #8a7b48; font-size: 0.9rem; margin-bottom: 0.5rem;">[ 占卜解惑 ]</div>
            <div style="color: #fff; font-size: 1.1rem; margin-bottom: 1rem;">问：{question}</div>
            <div style="color: #ccc; line-height: 1.8;">
                卦象说：从 <span class="important">{orig_name}</span> 开始，经过 <span class="important">{mut_name}</span> 的变化，最后变成 <span class="important">{trans_name}</span>。<br>
                别急，慢慢来，天意都在花瓣里。
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br><br><div style='text-align: center; color: #111; font-size: 0.6rem; letter-spacing: 0.5em;'>花开花落，自有定数</div>", unsafe_allow_html=True)
