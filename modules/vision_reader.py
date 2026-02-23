import google.generativeai as genai
import streamlit as st
import PIL.Image
import json
import re


def analyze_betting_image(uploaded_file):

    # 🔐 API KEY desde Streamlit Secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel("gemini-1.5-flash")

    img = PIL.Image.open(uploaded_file)

    # ===============================
    # 🧠 MASTER PROMPT — SPORTSBOOK VISION AI
    # ===============================

    prompt = """
You are an ELITE sports betting data extraction AI.

Your task:
Read a sportsbook screenshot (Caliente.mx NBA markets)
and extract structured betting data EXACTLY like a professional trader.

-------------------------
VISUAL UNDERSTANDING RULES
-------------------------

1. Each matchup contains TWO teams stacked vertically.
   Top team = Away
   Bottom team = Home

2. Column meanings:

   SPREAD / HANDICAP:
   numbers like +1.5, -3.0, +6.5

   TOTALS:
   ALWAYS contain:
   O <number>
   U <number>

   Example:
   O 232
   U 232

   NEVER confuse totals with handicap.

3. MONEYLINE ODDS:
   numbers like:
   +120
   -150
   +550

4. Ignore:
   - icons
   - stars
   - timers
   - logos
   - loading graphics
   - headers

5. If information is uncertain → skip that game.

-------------------------
OUTPUT FORMAT (STRICT)
-------------------------

Return ONLY valid JSON.

NO explanations.
NO markdown.
NO comments.

Structure:

{
  "games":[
    {
      "away":"Team A",
      "home":"Team B",
      "total_line":232.5,
      "odds_over":-110,
      "odds_under":-110,
      "spread_home":-3.5,
      "spread_away":3.5
    }
  ]
}

-------------------------
QUALITY RULES
-------------------------

✔ Extract only NBA games visible.
✔ Numbers must be numeric.
✔ Do NOT hallucinate teams.
✔ Do NOT invent lines.
✔ Skip incomplete rows.
✔ Return empty list if nothing readable.

Now analyze the image.
"""

    try:
        response = model.generate_content([prompt, img])

        raw_text = response.text

        # 🧼 LIMPIEZA AUTOMÁTICA DEL JSON
        cleaned = (
            raw_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        data = json.loads(cleaned)

        # 🧠 VALIDACIÓN EXTRA (ANTI-HALLUCINATION)
        if "games" not in data:
            return []

        valid_games = []

        for g in data["games"]:
            try:
                valid_games.append({
                    "away": str(g["away"]),
                    "home": str(g["home"]),
                    "total_line": float(g["total_line"]),
                    "odds_over": float(g["odds_over"]),
                    "odds_under": float(g["odds_under"]),
                    "spread_home": float(g["spread_home"]),
                    "spread_away": float(g["spread_away"]),
                })
            except:
                continue

        return valid_games

    except Exception as e:
        st.error(f"Vision AI error: {e}")
        return []
