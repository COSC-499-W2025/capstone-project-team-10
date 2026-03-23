# ---------- UI Color Constants ----------
HEADER_BG_COLOR = "#002145"

BG_COLOR = "#FFFFFF"

SIDEBAR_BG_COLOR = "#B1B2B5"
SIDEBAR_ITEM_SELECTED_BG = "#616264"
SIDEBAR_ITEM_HOVER_BG = "rgba(97, 98, 100, 120)"

SIDEBAR_TEXT_COLOR = "#000000"
SIDEBAR_SELECTED_TEXT_COLOR = "#FFFFFF"

DANGER_BG_COLOR = "#c02b2b"
DANGER_ITEM_HOVER_BG = "#8A5050"


BUTTON_STYLE = f"""
    QPushButton {{
        border-radius: 4px;
        background-color: {HEADER_BG_COLOR};
        color: white;
        font-weight: bold;
        padding: 6px 12px;
    }}
    QPushButton:hover {{
        background-color: {SIDEBAR_ITEM_HOVER_BG};
    }}
    QPushButton:pressed {{
        background-color: {SIDEBAR_SELECTED_TEXT_COLOR}
        color: {SIDEBAR_TEXT_COLOR}
    }}
"""

DANGER_BUTTON_STYLE = f"""
    QPushButton {{
        border-radius: 4px;
        background-color: {DANGER_BG_COLOR};
        color: white;
        font-weight: bold;
        padding: 6px 12px;
    }}
    QPushButton:hover {{
        background-color: {DANGER_ITEM_HOVER_BG};
    }}
    QPushButton:pressed {{
        background-color: {SIDEBAR_SELECTED_TEXT_COLOR}
        color: {SIDEBAR_TEXT_COLOR}
    }}
"""

CHECK_BOX_STYLES = f"""
QCheckBox {{
    font-size: 13px;
    color: #222;
    padding: 6px 0 6px 4px;
    spacing: 12px;
    background-color: {SIDEBAR_BG_COLOR};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 2px solid {HEADER_BG_COLOR};
    border-radius: 4px;
    background: white;
}}
QCheckBox::indicator:unchecked {{
    background: white;
    border: 2px solid {HEADER_BG_COLOR};
}}
QCheckBox::indicator:checked {{
    background: {HEADER_BG_COLOR};
    border: 2px solid {HEADER_BG_COLOR};
}}"""
