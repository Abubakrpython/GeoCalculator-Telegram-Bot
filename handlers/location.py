import logging
import xml.etree.ElementTree as ET
from xml.dom import minidom

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from geopy.distance import geodesic

from my_loaders import db
from states.statesm import GeoStates
from keyboards.keyboardm import (
    segments_kb,
    altitude_kb,
    cancel_kb,
    main_menu,
)

router = Router()
logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000


# =========================
# START COORDINATE FLOW
# =========================
@router.message(Command("coordinate"))
@router.message(F.text == "🧭 Coordinate calculation")
async def ask_first_coordinate(message: types.Message, state: FSMContext):
    """
    Starts coordinate calculation flow.
    """
    try:
        await message.answer(
            "📍 Please enter the <b>first coordinate</b>:\n"
            "<code>latitude, longitude</code>\n"
            "Example: <b>41.311081, 69.240562</b>",
            parse_mode="HTML",
            reply_markup=cancel_kb,
        )
        await state.set_state(GeoStates.first)
    except Exception as e:
        logger.exception(e)
        await message.answer("⚠️ Internal error. Please try again.")


# =========================
# CANCEL PROCESS
# =========================
@router.message(F.text == "❌ Cancel")
async def cancel_process(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "❌ Calculation cancelled.",
        reply_markup=main_menu,
    )


# =========================
# FIRST COORDINATE
# =========================
@router.message(GeoStates.first)
async def get_first_coordinate(message: types.Message, state: FSMContext):
    try:
        lat, lon = map(float, message.text.split(","))
        await state.update_data(coord_a=(lat, lon))

        await message.answer(
            "📍 Now enter the <b>second coordinate</b>:\n"
            "<code>latitude, longitude</code>\n"
            "Example: <b>41.327546, 69.281003</b>",
            parse_mode="HTML",
            reply_markup=cancel_kb,
        )
        await state.set_state(GeoStates.second)
    except Exception:
        await message.answer(
            "⚠️ Invalid format!\n"
            "Correct format: <b>41.311081, 69.240562</b>",
            parse_mode="HTML",
        )


# =========================
# SECOND COORDINATE
# =========================
@router.message(GeoStates.second)
async def get_second_coordinate(message: types.Message, state: FSMContext):
    try:
        lat, lon = map(float, message.text.split(","))
        await state.update_data(coord_b=(lat, lon))

        await message.answer(
            "✳️ How many segments do you need?",
            reply_markup=segments_kb,
        )
        await state.set_state(GeoStates.segments)
    except Exception:
        await message.answer(
            "⚠️ Invalid format!\n"
            "Correct format: <b>41.327546, 69.281003</b>",
            parse_mode="HTML",
        )


# =========================
# SEGMENTS COUNT
# =========================
@router.message(GeoStates.segments)
async def get_segments_count(message: types.Message, state: FSMContext):
    try:
        segments = int(message.text)
        await state.update_data(segments=segments)

        await message.answer(
            "🛫 Choose or enter altitude (meters).\n"
            "Examples:\n"
            "<b>50</b> or <b>50,60,70</b>",
            parse_mode="HTML",
            reply_markup=altitude_kb,
        )
        await state.set_state(GeoStates.altitude)
    except ValueError:
        await message.answer("⚠️ Please enter a valid number.")


# =========================
# ALTITUDE & CALCULATION
# =========================
@router.message(GeoStates.altitude)
async def process_altitude_and_calculation(message: types.Message, state: FSMContext):
    try:
        text = message.text.replace(" ", "")
        altitude_values = list(map(int, text.split(",")))

        if len(altitude_values) not in (1, 3):
            raise ValueError

        data = await state.get_data()
        point_a, point_b = data["coord_a"], data["coord_b"]
        segments = data["segments"]

        # Generate intermediate points
        points = []
        for i in range(segments + 1):
            fraction = i / segments
            lat = point_a[0] + (point_b[0] - point_a[0]) * fraction
            lon = point_a[1] + (point_b[1] - point_a[1]) * fraction
            alt = altitude_values[i % len(altitude_values)]
            points.append((lat, lon, alt))

        total_distance_km = geodesic(point_a, point_b).kilometers
        avg_segment_km = total_distance_km / segments

        # Calculate distances between points
        distances = []
        for i in range(len(points) - 1):
            d = geodesic(
                (points[i][0], points[i][1]),
                (points[i + 1][0], points[i + 1][1]),
            ).meters
            distances.append(d)

        # Send points info
        message_text = ""
        for i, (lat, lon, alt) in enumerate(points):
            if i < len(distances):
                message_text += (
                    f"📍 <b>Point {i}</b>: <code>{lat:.6f}, {lon:.6f}</code>\n"
                    f"🛫 {alt} m | 📏 {distances[i]:.1f} m to next\n\n"
                )
            else:
                message_text += (
                    f"📍 <b>Point {i}</b>: <code>{lat:.6f}, {lon:.6f}</code>\n"
                    f"🛬 {alt} m | 🔚 Final point\n\n"
                )

        while len(message_text) > 3900:
            await message.answer(message_text[:3900], parse_mode="HTML")
            message_text = message_text[3900:]

        if message_text:
            await message.answer(message_text, parse_mode="HTML")

        # =========================
        # CREATE INAV MISSION FILE
        # =========================
        mission = ET.Element("mission")
        ET.SubElement(mission, "version", {"value": "2.3-pre8"})
        ET.SubElement(
            mission,
            "mwp",
            {
                "cx": str(points[0][1]),
                "cy": str(points[0][0]),
                "home-x": "0",
                "home-y": "0",
                "zoom": "13",
            },
        )
        ET.SubElement(mission, "geozones", {"count": "0"})

        for i, (lat, lon, alt) in enumerate(points, start=1):
            ET.SubElement(
                mission,
                "missionitem",
                {
                    "no": str(i),
                    "action": "WAYPOINT",
                    "lat": f"{lat:.7f}",
                    "lon": f"{lon:.7f}",
                    "alt": str(alt),
                    "parameter1": "0",
                    "parameter2": "0",
                    "parameter3": "0",
                    "flag": "165" if i == len(points) else "0",
                },
            )

        xml_string = minidom.parseString(ET.tostring(mission)).toprettyxml(indent="\t")
        file_path = f"INAV_{message.from_user.id}.mission"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
            f.write(xml_string)

        # Save calculation to database
        await db.add_calculation(
            user_id=message.from_user.id,
            coord_a=str(point_a),
            coord_b=str(point_b),
            segments=segments,
            result=f"{total_distance_km:.3f} km | Altitudes: {altitude_values}",
        )

        # Final summary
        await message.answer(
            "✅ <b>Calculation completed!</b>\n"
            f"📏 Total distance: <code>{total_distance_km:.3f} km</code>\n"
            f"📍 Average segment: <code>{avg_segment_km * 1000:.1f} m</code>\n"
            "📂 INAV mission file generated.",
            parse_mode="HTML",
        )

        await message.answer_document(
            FSInputFile(file_path),
            caption="✈️ INAV 7.0.1 mission file ready!",
            reply_markup=main_menu,
        )

        await state.clear()

    except Exception as e:
        logger.exception(e)
        await message.answer(
            "⚠️ Invalid altitude input.\n"
            "Examples: <b>50</b> or <b>50,60,70</b>",
            parse_mode="HTML",
        )


# =========================
# CALCULATION HISTORY
# =========================
@router.message(Command("history"))
@router.message(F.text == "📜 Calculation history")
async def show_history(message: types.Message):
    try:
        rows = await db.get_last_calculations(message.from_user.id, limit=3)

        if not rows:
            await message.answer(
                "📭 You have no calculation history yet.",
                reply_markup=main_menu,
            )
            return

        await message.answer(
            "📜 <b>Your last 3 calculations:</b>",
            parse_mode="HTML",
        )

        for idx, row in enumerate(rows, start=1):
            await message.answer(
                f"📍 <b>Result {idx}:</b> <code>{row['result']}</code>",
                parse_mode="HTML",
            )

    except Exception as e:
        logger.exception(e)
        await message.answer("⚠️ Failed to load history.")
