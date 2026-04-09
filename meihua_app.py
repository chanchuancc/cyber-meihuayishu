import streamlit as st
import datetime
import time
import random
import json
import os
from borax.calendars.lunardate import LunarDate

# --- 洞穴配置与石头样式 (v1.5.0 Oracle Portal) ---
st.set_page_config(page_title="梅花易数", page_icon="🌸", layout="centered")

# 石头刻字 CSS (礼部重构：去冗余、正中宫、提天机)
cave_css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@200;400;700&display=swap');

    /* 洞穴背景：玄色径向渐变 */
    .stApp {
        background: radial-gradient(circle at center, #1a1a1a 0%, #050505 100%);
        color: #d4af37;
        font-family: 'Noto Serif SC', 'Microsoft YaHei', serif;
    }
    
    /* 页面上浮：压缩顶部空间 */
    .block-container {
        padding-top: 1rem !important;
        max-width: 800px !important;
    }

    /* 落下梅花：灵性动效 */
    @keyframes fall {
        0% { transform: translateY(-10vh) translateX(0) rotate(0deg); opacity: 0; }
        10% { opacity: 0.8; }
        90% { opacity: 0.4; }
        100% { transform: translateY(110vh) translateX(100px) rotate(360deg); opacity: 0; }
    }
    .petal {
        position: fixed;
        top: -10%;
        color: rgba(255, 183, 197, 0.5);
        font-size: 22px;
        user-select: none;
        z-index: 0;
        pointer-events: none;
        animation: fall linear infinite;
    }

    /* 标题：大而正，去伪存真 */
    h1 {
        font-size: 3.5rem !important;
        font-weight: 200 !important;
        letter-spacing: 0.8rem !important;
        text-align: center;
        color: #d4af37;
        margin-bottom: 0.5rem !important;
        text-shadow: 0 0 25px rgba(212, 175, 55, 0.4);
        margin-top: 1rem !important;
    }
    .sub-title {
        text-align: center;
        color: #8a7b48;
        font-size: 1.1rem;
        letter-spacing: 0.3rem;
        margin-bottom: 2.5rem;
        font-weight: 300;
    }

    /* 神谕入口：三位一体输入框 */
    .ritual-hint {
        text-align: center;
        color: #666;
        font-size: 1.1rem;
        margin-bottom: 1.5rem;
        font-weight: 300;
        letter-spacing: 0.2rem;
    }
    
    /* 强制调整输入框和按钮在一行，且样式统一 */
    div[data-testid="stHorizontalBlock"] {
        align-items: center !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.2) !important;
        border-radius: 50px !important;
        padding: 5px 20px !important;
        box-shadow: 0 15px 40px rgba(0,0,0,0.6) !important;
        margin-bottom: 2rem !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stHorizontalBlock"]:focus-within {
        border-color: #d4af37 !important;
        box-shadow: 0 0 30px rgba(212, 175, 55, 0.3) !important;
    }
    
    /* REMOVE ALL WHITE BACKGROUNDS FROM INPUT */
    div[data-testid="stTextInput"], div[data-testid="stTextInput"] > div, div[data-testid="stTextInput"] div[data-baseweb="input"], div[data-testid="stTextInput"] div[data-baseweb="base-input"] {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stTextInput input {
        background-color: transparent !important;
        background: transparent !important;
        color: #fff !important;
        border: none !important;
        padding: 10px 0 !important;
        font-size: 1.2rem !important;
        box-shadow: none !important;
    }
    
    /* 按钮微调：小而精 */
    .stButton > button {
        background-color: transparent !important;
        background: transparent !important;
        color: #d4af37 !important;
        border: none !important;
        box-shadow: none !important;
        font-size: 1.5rem !important;
        padding: 0 !important;
        width: 45px !important;
        height: 45px !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: transform 0.2s ease !important;
        min-width: 45px !important;
    }
    .stButton > button:hover {
        color: #fff !important;
        transform: scale(1.2) !important;
        background: transparent !important;
    }

    /* 卦象结果：破茧动效 */
    .result-container {
        background: rgba(12, 12, 12, 0.95);
        border: 1px solid rgba(212, 175, 55, 0.2);
        padding: 3rem;
        border-radius: 12px;
        margin-top: 1rem;
        animation: emerge 1.2s cubic-bezier(0.23, 1, 0.32, 1);
        box-shadow: 0 40px 80px rgba(0,0,0,0.9);
    }
    @keyframes emerge {
        from { opacity: 0; transform: translateY(30px) scale(0.98); filter: blur(15px); }
        to { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); }
    }

    .trace-bar {
        text-align: center;
        font-family: 'Courier New', monospace;
        color: #444;
        font-size: 0.85rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #1a1a1a;
        padding-bottom: 1rem;
    }
    .important {
        color: #d4af37;
        font-weight: 700;
    }

    .gua-grid {
        display: flex;
        justify-content: space-around;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .gua-item {
        text-align: center;
        padding: 1rem;
    }
    .gua-label {
        font-size: 0.8rem;
        color: #6a5a2a;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .gua-name {
        font-size: 1.8rem;
        font-weight: 700;
        color: #d4af37;
        margin-bottom: 0.5rem;
    }
    .gua-symbol {
        font-size: 4rem;
        line-height: 1;
        color: #fff;
        text-shadow: 0 0 15px rgba(255,255,255,0.2);
    }

    /* Hide Streamlit UI elements */
    #MainMenu, footer, header { visibility: hidden; }
</style>
"""
st.markdown(cave_css, unsafe_allow_html=True)

# 撒梅花 (灵性流转)
for _ in range(12):
    left = random.randint(0, 100)
    dur = random.randint(8, 20)
    delay = random.randint(0, 15)
    st.markdown(f'<div class="petal" style="left:{left}%; animation-duration:{dur}s; animation-delay:{delay}s;">🌸</div>', unsafe_allow_html=True)

# --- 数据资产 (The Core) ---
BAGUA = {
    1: {"name": "乾", "symbol": "☰", "lines": [1, 1, 1]},
    2: {"name": "兑", "symbol": "☱", "lines": [1, 1, 0]},
    3: {"name": "离", "symbol": "☲", "lines": [1, 0, 1]},
    4: {"name": "震", "symbol": "☳", "lines": [1, 0, 0]},
    5: {"name": "巽", "symbol": "☴", "lines": [0, 1, 1]},
    6: {"name": "坎", "symbol": "☵", "lines": [0, 1, 0]},
    7: {"name": "艮", "symbol": "☶", "lines": [0, 0, 1]},
    8: {"name": "坤", "symbol": "☷", "lines": [0, 0, 0]}
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

# --- 核心函数 (Logic) ---
def get_shichen_idx(h):
    if h >= 23 or h < 1: return 1
    return (h + 1) // 2 + 1

def get_gua_id_by_lines(lines):
    for k, v in BAGUA.items():
        if v["lines"] == lines: return k
    return 1

# --- 界面交互 (UI) ---
st.markdown("<h1>梅 花 易 数</h1>", unsafe_allow_html=True)
st.markdown('<p class="sub-title">算法即神谕 · 结果自然成</p>', unsafe_allow_html=True)

st.markdown('<p class="ritual-hint">请屏息凝神，于心中默念所求之事</p>', unsafe_allow_html=True)

# 三位一体神谕入口 (Oracle Portal)
c1, c2, c3 = st.columns([6, 1, 1])
with c1:
    question = st.text_input("Divine Question", placeholder="输入你心中所惑...", label_visibility="collapsed")
with c2:
    voice_btn = st.button("🎙️", help="语音感应")
with c3:
    confirm_btn = st.button("⮕", help="感应天机")

if confirm_btn or voice_btn:
    if not question:
        st.toast("机缘未到。请先于心中落笔。", icon="🧧")
    else:
        # 30秒深度演算动画
        anim_box = st.empty()
        msgs = [
            ("📡 正在捕捉四柱波段...", 5),
            ("🌸 正在读取农历星历...", 6),
            ("⚡ 正在执行二进制位运算...", 6),
            ("👁️ 正在观测平行路径...", 7),
            ("🔮 正在解密神谕数据包...", 6)
        ]
        
        for msg, dur in msgs:
            for _ in range(dur * 2):
                with anim_box.container():
                    st.markdown(f'<div style="text-align: center; color: #d4af37; font-size: 1.2rem; margin-top: 2rem;">{msg}</div>', unsafe_allow_html=True)
                    glitch = "".join([random.choice("0123456789ABCDEF") for _ in range(32)])
                    st.markdown(f'<div style="text-align: center; color: #111; font-family: monospace; font-size: 0.7rem; letter-spacing: 4px; opacity: 0.3;">{glitch}</div>', unsafe_allow_html=True)
                    time.sleep(0.5)
        anim_box.empty()

        # 核心演算
        now = datetime.datetime.now()
        lunar = LunarDate.from_solar_date(now.year, now.month, now.day)
        y_gz = lunar.year_gz[1]
        Y, M, D, H = DIZHI_MAP[y_gz], lunar.month, lunar.day, get_shichen_idx(now.hour)

        up_idx = (Y + M + D) % 8 or 8
        low_idx = (Y + M + D + H) % 8 or 8
        move_idx = (Y + M + D + H) % 6 or 6

        # 推演三卦
        orig_name = GUA_64[(up_idx, low_idx)]
        orig_lines = BAGUA[low_idx]["lines"] + BAGUA[up_idx]["lines"]
        
        mut_l = get_gua_id_by_lines(orig_lines[1:4])
        mut_u = get_gua_id_by_lines(orig_lines[2:5])
        mut_name = GUA_64[(mut_u, mut_l)]
        
        trans_lines = list(orig_lines)
        trans_lines[move_idx-1] = 1 - trans_lines[move_idx-1]
        trans_l = get_gua_id_by_lines(trans_lines[0:3])
        trans_u = get_gua_id_by_lines(trans_lines[3:6])
        trans_name = GUA_64[(trans_u, trans_l)]

        # 最终交付
        st.markdown(f"""
        <div class="result-container">
            <div class="trace-bar">
                {now.strftime('%Y-%m-%d %H:%M:%S')} | {lunar.strftime('%Y年%L%M月%D')} {DIZHI_NAMES[H-1]}时<br>
                KERNEL: ({Y} + {M} + {D} + {H}) MOD 8/6
            </div>
            <div class="gua-grid">
                <div class="gua-item">
                    <div class="gua-label">本卦 (Original)</div>
                    <div class="gua-name">{orig_name}</div>
                    <div class="gua-symbol">{BAGUA[up_idx]["symbol"]}<br>{BAGUA[low_idx]["symbol"]}</div>
                </div>
                <div class="gua-item">
                    <div class="gua-label">互卦 (Mutual)</div>
                    <div class="gua-name">{mut_name}</div>
                    <div class="gua-symbol">{BAGUA[mut_u]["symbol"]}<br>{BAGUA[mut_l]["symbol"]}</div>
                </div>
                <div class="gua-item">
                    <div class="gua-label">变卦 (Transformed)</div>
                    <div class="gua-name">{trans_name}</div>
                    <div class="gua-symbol">{BAGUA[trans_u]["symbol"]}<br>{BAGUA[trans_l]["symbol"]}</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 2rem; color: #d4af37; font-size: 1.1rem; letter-spacing: 0.2em;">
                第 <span style="font-size: 2rem; font-weight: 700;">{move_idx}</span> 爻动
            </div>
            <div style="margin-top: 3rem; border-top: 1px solid #222; padding-top: 2rem; text-align: center;">
                <div style="color: #6a5a2a; font-size: 0.8rem; margin-bottom: 1rem; text-transform: uppercase;">[ 神 谕 解 读 ]</div>
                <div style="color: #bbb; line-height: 2.1; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
                    陛下所问：<b>{question}</b><br><br>
                    此卦由 <span class="important">{orig_name}</span> 启，历 <span class="important">{mut_name}</span> 之变，终归于 <span class="important">{trans_name}</span>。<br>
                    一花开五叶，结果自然成。请屏息感应，答案自在心中。
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br><br><p style='text-align: center; color: #111; font-size: 0.7rem; letter-spacing: 0.5em;'>数 起 于 心 · 卦 现 于 形</p>", unsafe_allow_html=True)
