import streamlit as st
import math
from typing import List

# ==========================================
# 1. Models (資料與商業邏輯層)
# ==========================================
class Mushroom:
    def __init__(self, category: str, name: str, hp: int):
        self.category = category
        self.name = name
        self.hp = hp
        
    def __str__(self):
        return f"{self.name} (血量: {self.hp:,})"

class MushroomRepository:
    def __init__(self):
        self.mushrooms = [
            Mushroom("一般普通", "白 / 粉 / 冰藍", 621000),
            Mushroom("一般普通", "黃 / 藍", 645800),
            Mushroom("一般普通", "紅", 670600),
            Mushroom("一般普通", "灰", 695500),
            Mushroom("一般普通", "紫", 720300),
            Mushroom("大型普通", "白 / 粉 / 冰藍", 2700000),
            Mushroom("大型普通", "黃 / 藍", 2808000),
            Mushroom("大型普通", "紅", 2916000),
            Mushroom("大型普通", "灰", 3024000),
            Mushroom("大型普通", "紫", 3132000),
            Mushroom("一般元素", "毒", 3783200),
            Mushroom("一般元素", "水 / 電", 3816700),
            Mushroom("一般元素", "火", 3850200),
            Mushroom("一般元素", "水晶", 3883600),
            Mushroom("大型元素", "毒", 13424400),
            Mushroom("大型元素", "水 / 電", 13543200),
            Mushroom("大型元素", "火", 13662000),
            Mushroom("大型元素", "水晶", 13780800),
            Mushroom("活動", "一般活動蘑菇", 648000),
            Mushroom("活動", "巨大活動蘑菇", 3456000),
        ]
        
    def get_categories(self) -> List[str]:
        categories = []
        for m in self.mushrooms:
            if m.category not in categories:
                categories.append(m.category)
        return categories

    def get_by_category(self, category: str) -> List[Mushroom]:
        return [m for m in self.mushrooms if m.category == category]

# ==========================================
# 2. Strategy Pattern (策略模式)
# ==========================================
class CalculationStrategy:
    pass

class CalculateTimeStrategy(CalculationStrategy):
    def calculate(self, hp: int, power: int) -> str:
        if power <= 0: raise ValueError("戰力必須大於0")
        total_seconds = math.ceil((hp * 100) / power)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        parts = []
        if hours > 0: parts.append(f"{hours} 小時")
        if minutes > 0: parts.append(f"{minutes} 分鐘")
        parts.append(f"{seconds} 秒")
        return f"預估打完時間：{' '.join(parts)}"

class CalculateMaxPowerStrategy(CalculationStrategy):
    def calculate(self, hp: int, hours: int, minutes: int) -> str:
        target_minutes = hours * 60 + minutes
        if target_minutes <= 0: raise ValueError("總時間不能為 0")
        target_seconds = target_minutes * 60
        max_power = math.floor((hp * 100) / target_seconds)
        time_str = f"{hours} 小時 {minutes} 分鐘" if hours > 0 else f"{minutes} 分鐘"
        return f"為確保打滿 {time_str}，戰力請低於：【 {max_power:,} 】"

# ==========================================
# 3. View & Controller (網頁渲染與控制層)
# ==========================================
# 設定網頁標題與 Icon
st.set_page_config(page_title="Pikmin Bloom 計算器", page_icon="🍄", layout="centered")

# 自訂 CSS 隱藏預設的右上角選單與底部浮水印，讓畫面更像獨立 APP
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

st.title("🍄 Pikmin Bloom 戰鬥計算器")
st.markdown("---")

repo = MushroomRepository()
categories = repo.get_categories()

st.subheader("1. 選擇蘑菇目標 🎯")
# 動態連動選單：選擇主分類後，血量選單自動更新
category = st.selectbox("主分類", categories)
mushrooms = repo.get_by_category(category)

mushroom_options = {f"{m.name} (血量: {m.hp:,})": m for m in mushrooms}
selected_display = st.selectbox("次分類 / 血量", list(mushroom_options.keys()))
selected_mushroom = mushroom_options[selected_display]

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("2. 選擇計算模式 ⚙️")
mode = st.radio("模式", ["算時間 (輸入目前總戰力)", "算戰力 (輸入想卡的耗時)"], label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
st.subheader("3. 數值與結果 📝")

if mode == "算時間 (輸入目前總戰力)":
    power = st.number_input("請輸入目前戰力", min_value=1, value=1000, step=100)
    if st.button("🚀 開始計算", use_container_width=True):
        strategy = CalculateTimeStrategy()
        st.success(strategy.calculate(selected_mushroom.hp, power))
else:
    col1, col2 = st.columns(2)
    with col1:
        hours = st.number_input("小時", min_value=0, value=0, step=1)
    with col2:
        minutes = st.number_input("分鐘", min_value=0, value=0, step=10)
        
    if st.button("🚀 開始計算", use_container_width=True):
        strategy = CalculateMaxPowerStrategy()
        try:
            result = strategy.calculate(selected_mushroom.hp, hours, minutes)
            st.warning(result) # 使用 warning 顏色(橘黃)來凸顯卡戰力警示
        except ValueError as e:
            st.error(f"⚠️ {str(e)}")