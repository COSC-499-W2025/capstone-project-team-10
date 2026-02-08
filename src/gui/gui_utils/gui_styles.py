# ---------- UI Color Constants ----------
HEADER_BG_COLOR = "#002145"

SIDEBAR_BG_COLOR = "#B1B2B5"
SIDEBAR_ITEM_SELECTED_BG = "#616264"
SIDEBAR_ITEM_HOVER_BG = "rgba(97, 98, 100, 120)"

SIDEBAR_TEXT_COLOR = "black"
SIDEBAR_SELECTED_TEXT_COLOR = "white"

BUTTON_STYLE = f"""
    QPushButton {{
        border-radius: 4px;
        background-color: {HEADER_BG_COLOR};
        color: white;
        font-weight: bold;
        padding: 6px 12px;
    }}
    QPushButton:hover {{
        background-color: #001f3d;
    }}
"""
