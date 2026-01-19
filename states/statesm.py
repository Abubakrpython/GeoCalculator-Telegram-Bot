
from aiogram.fsm.state import State, StatesGroup

class GeoStates(StatesGroup):
    first = State()
    second = State()
    segments = State()
    altitude = State()
