from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# ===================== MAIN MENU =====================

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🧭 Calculate Coordinates")],
        [KeyboardButton(text="📜 My Calculation History")],
        [KeyboardButton(text="ℹ️ About the Bot")]
    ],
    resize_keyboard=True
)


# ===================== SEGMENTS KEYBOARD =====================

segments_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=str(i)) for i in [2, 3, 4]],
        [KeyboardButton(text=str(i)) for i in [5, 10, 15]],
        [KeyboardButton(text=str(i)) for i in [20, 25, 30]],
        [KeyboardButton(text=str(i)) for i in [35, 40, 45]],
        [KeyboardButton(text="❌ Cancel")]
    ],
    resize_keyboard=True
)


# ===================== ALTITUDE KEYBOARD =====================

altitude_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=str(i)) for i in [20, 30, 40]],
        [KeyboardButton(text=str(i)) for i in [50, 70, 90]],
        [KeyboardButton(text=str(i)) for i in [100, 130, 150]],
        [KeyboardButton(text=str(i)) for i in [200, 250, 300]],
        [KeyboardButton(text="❌ Cancel")]
    ],
    resize_keyboard=True
)


# ===================== CANCEL ONLY =====================

cancel_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Cancel")]],
    resize_keyboard=True
)
