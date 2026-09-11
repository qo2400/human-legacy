# HUMAN LEGACY
# Civilization Evolution Prototype
# Python 3 + Kivy
#
# Main systems:
# - Human population
# - Dynamic social values
# - Government evolution
# - Research and technology
# - Science and knowledge
# - Economy
# - Culture
# - Military
# - Diplomacy
# - Random historical events
# - Environment
# - Historical timeline
# - Save / Load
#
# No external assets are required.
#
# FIXES IN THIS VERSION:
# 1. Save file now lives in the app's private, writable data directory
#    (App.user_data_dir) instead of the current working directory, which
#    is often not writable/persistent on Android.
# 2. All save/load operations are wrapped in try/except so a storage
#    error shows a message instead of crashing the app.
# 3. The History screen text now wraps correctly on narrow phone screens
#    (it used to overflow horizontally with no way to read it).
# 4. History log is capped so the save file cannot grow without limit
#    during very long play sessions.
# 5. Android hardware back button now closes open popups instead of
#    closing the whole app while a popup is open.
# 6. Font sizes use sp() (scales with the user's accessibility text
#    size) instead of dp() for text.

import json
import random
from pathlib import Path

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout


# ============================================================
# SAVE FILE LOCATION
# ============================================================

def get_save_path():
    """
    Returns a writable, persistent path for the save file.
    Uses the Kivy app's private data directory when the app is
    running (this is the correct, permission-safe location on
    Android). Falls back to the current directory when running
    outside of a Kivy App context (e.g. quick testing).
    """

    try:

        app = App.get_running_app()

        if app is not None:

            base = Path(app.user_data_dir)

        else:

            base = Path(".")

    except Exception:

        base = Path(".")

    try:

        base.mkdir(parents=True, exist_ok=True)

    except Exception:

        base = Path(".")

    return base / "human_legacy_save.json"


# ============================================================
# CIVILIZATION ENGINE
# ============================================================

class Civilization:

    MAX_HISTORY = 500

    def __init__(self):

        # ----------------------------------------------------
        # TIME
        # ----------------------------------------------------

        self.year = -10000

        # ----------------------------------------------------
        # BASIC CIVILIZATION STATS
        # ----------------------------------------------------

        self.population = 120.0
        self.knowledge = 5.0
        self.science = 1.0

        self.stability = 72.0
        self.happiness = 68.0

        self.wealth = 20.0
        self.military = 4.0
        self.culture = 10.0

        self.environment = 80.0

        # ----------------------------------------------------
        # SOCIAL VALUES
        # ----------------------------------------------------

        self.values = {

            "Freedom": 45.0,
            "Equality": 50.0,
            "Tradition": 70.0,
            "Authority": 35.0,
            "Religion": 60.0,
            "Science": 15.0,
            "Militarism": 10.0,
            "Individualism": 30.0,
        }

        # ----------------------------------------------------
        # TECHNOLOGY
        # ----------------------------------------------------

        self.techs = {

            "Fire": True,
            "Stone Tools": True,
            "Agriculture": False,
            "Writing": False,
            "Bronze": False,
            "Iron": False,
            "Mathematics": False,
            "Medicine": False,
            "Engineering": False,
            "Printing": False,
            "Steam Power": False,
            "Electricity": False,
            "Computing": False,
            "Artificial Intelligence": False,
            "Spaceflight": False,
        }

        # ----------------------------------------------------
        # GOVERNMENT
        # ----------------------------------------------------

        self.government = "Tribal Council"

        # ----------------------------------------------------
        # DIPLOMACY
        # ----------------------------------------------------

        self.relations = {

            "Northern Tribe": 50.0,
            "River People": 50.0,
            "Mountain Clan": 50.0,
        }

        # ----------------------------------------------------
        # HISTORY
        # ----------------------------------------------------

        self.history = [

            "The first human settlement of this world is born."
        ]

    # ========================================================
    # LOGGING (capped so save file cannot grow forever)
    # ========================================================

    def _log(self, text):

        self.history.append(text)

        if len(self.history) > self.MAX_HISTORY:

            self.history = self.history[-self.MAX_HISTORY:]

    # ========================================================
    # LIMIT VALUES
    # ========================================================

    def clamp(self):

        for group in (self.values, self.relations):

            for key in group:

                group[key] = max(0.0, min(100.0, group[key]))

        self.stability = max(0.0, min(100.0, self.stability))
        self.happiness = max(0.0, min(100.0, self.happiness))
        self.environment = max(0.0, min(100.0, self.environment))

    # ========================================================
    # GOVERNMENT ENGINE
    # ========================================================

    def government_for_values(self):

        v = self.values

        if v["Authority"] > 75 and v["Militarism"] > 65:
            return "Military Empire"

        if v["Religion"] > 78 and v["Tradition"] > 65:
            return "Sacred Kingdom"

        if v["Freedom"] > 70 and v["Equality"] > 65:
            return "Republic"

        if v["Science"] > 70 and v["Freedom"] > 55:
            return "Scientific Democracy"

        if v["Authority"] > 70:
            return "Absolute Monarchy"

        if v["Equality"] > 70 and v["Tradition"] < 45:
            return "Civic Federation"

        if v["Individualism"] > 70:
            return "Free Confederation"

        return "Tribal Council"

    # ========================================================
    # RESEARCH SYSTEM
    # ========================================================

    def available_research(self):

        t = self.techs
        result = []

        if not t["Agriculture"]:
            result.append(("Agriculture", 8, "Permanent settlements and food production."))

        if t["Agriculture"] and not t["Writing"]:
            result.append(("Writing", 14, "Records, administration and accumulated knowledge."))

        if t["Agriculture"] and not t["Bronze"]:
            result.append(("Bronze", 18, "Better tools, weapons and trade."))

        if t["Bronze"] and not t["Iron"]:
            result.append(("Iron", 25, "Stronger tools, weapons and infrastructure."))

        if t["Writing"] and not t["Mathematics"]:
            result.append(("Mathematics", 22, "Calculation, astronomy and engineering."))

        if t["Writing"] and not t["Medicine"]:
            result.append(("Medicine", 26, "Health, survival and population growth."))

        if t["Mathematics"] and t["Iron"] and not t["Engineering"]:
            result.append(("Engineering", 32, "Machines, roads and large structures."))

        if t["Writing"] and t["Mathematics"] and not t["Printing"]:
            result.append(("Printing", 40, "Rapid spread of knowledge."))

        if t["Engineering"] and not t["Steam Power"]:
            result.append(("Steam Power", 52, "Industrialization begins."))

        if t["Steam Power"] and not t["Electricity"]:
            result.append(("Electricity", 70, "Modern industry and communication."))

        if t["Electricity"] and not t["Computing"]:
            result.append(("Computing", 95, "The information age begins."))

        if t["Computing"] and not t["Artificial Intelligence"]:
            result.append(("Artificial Intelligence", 125, "Machine intelligence."))

        if t["Artificial Intelligence"] and not t["Spaceflight"]:
            result.append(("Spaceflight", 160, "Humanity reaches beyond Earth."))

        return result

    # ========================================================
    # RESEARCH
    # ========================================================

    def research(self, name, cost):

        if self.techs.get(name, False):
            return False, "Already discovered."

        if self.knowledge < cost:
            return False, "Not enough knowledge."

        self.knowledge -= cost
        self.techs[name] = True
        self.science += cost * 0.12
        self.culture += 2.0

        self._log(f"{self.year}: Humanity discovered {name}.")

        return True, f"Discovery completed: {name}"

    # ========================================================
    # RANDOM HISTORICAL EVENTS
    # ========================================================

    def random_event(self):

        events = [
            ("A drought tests the civilization.", -8, -4, -6),
            ("A charismatic teacher spreads new ideas.", 4, 6, 2),
            ("A trade route opens.", 5, 3, 4),
            ("A disease spreads through the population.", -6, -2, -10),
            ("A neighboring tribe requests cooperation.", 3, 4, 3),
            ("A generation of inventors appears.", 8, 5, 2),
            ("A leadership dispute divides society.", -7, -5, -3),
            ("A philosophical movement changes society.", 2, 7, 1),
            ("Merchants establish a distant trade network.", 4, 3, 8),
            ("A military threat appears at the border.", -5, -4, -2),
        ]

        text, stability, happiness, wealth = random.choice(events)

        self.stability += stability
        self.happiness += happiness
        self.wealth += wealth

        self._log(f"{self.year}: {text}")

        return text

    # ========================================================
    # ADVANCE TIME
    # ========================================================

    def advance(self):

        self.year += 25

        # SCIENCE GENERATION
        science_gain = (
            0.35
            + self.population / 1200
            + self.culture / 250
            + self.values["Science"] / 180
        )

        if self.techs["Writing"]:
            science_gain += 3

        if self.techs["Printing"]:
            science_gain += 4

        if self.techs["Computing"]:
            science_gain += 8

        if self.techs["Artificial Intelligence"]:
            science_gain += 14

        self.knowledge += science_gain

        # POPULATION
        if self.techs["Agriculture"]:
            self.population *= 1.018
            self.wealth += 2
        else:
            self.population *= 1.004

        if self.techs["Medicine"]:
            self.population *= 1.012
            self.happiness += 1

        if self.techs["Iron"]:
            self.military += 0.8

        if self.techs["Engineering"]:
            self.wealth += 3

        if self.techs["Steam Power"]:
            self.population *= 1.01
            self.wealth += 7

        if self.techs["Electricity"]:
            self.wealth += 12
            self.culture += 2

        if self.techs["Computing"]:
            self.culture += 4

        if self.techs["Spaceflight"]:
            self.culture += 5

        # ENVIRONMENT
        if self.population > 5000:
            self.environment -= 1

        if self.population > 20000:
            self.environment -= 1.5

        # DIPLOMACY
        for name in self.relations:
            self.relations[name] += random.uniform(-3, 3)

        # SOCIAL EVOLUTION
        if self.techs["Agriculture"]:
            self.values["Tradition"] += 0.08

        if self.techs["Writing"]:
            self.values["Authority"] += 0.05

        if self.techs["Mathematics"]:
            self.values["Science"] += 0.12

        if self.techs["Printing"]:
            self.values["Freedom"] += 0.10

        if self.techs["Computing"]:
            self.values["Individualism"] += 0.12

        # RANDOM EVENT
        event_text = None

        if random.random() < 0.48:
            event_text = self.random_event()

        # GOVERNMENT
        old_government = self.government
        self.government = self.government_for_values()

        if old_government != self.government:
            self._log(
                f"{self.year}: Government changed from "
                f"{old_government} to {self.government}."
            )

        self.clamp()

        if event_text:
            return event_text

        return "A generation passes. Society continues to evolve."

    # ========================================================
    # SOCIAL POLICY
    # ========================================================

    def policy(self, name):

        if name not in self.values:
            return

        self.values[name] += 12
        self.culture += 1

        self._log(f"{self.year}: Society promoted the value of {name}.")

        old_government = self.government
        self.government = self.government_for_values()

        if old_government != self.government:
            self._log(
                f"{self.year}: Political transformation: "
                f"{old_government} -> {self.government}"
            )

        self.clamp()

    # ========================================================
    # SAVE
    # ========================================================

    def save(self):

        data = {
            "year": self.year,
            "population": self.population,
            "knowledge": self.knowledge,
            "science": self.science,
            "stability": self.stability,
            "happiness": self.happiness,
            "wealth": self.wealth,
            "military": self.military,
            "culture": self.culture,
            "environment": self.environment,
            "values": self.values,
            "techs": self.techs,
            "government": self.government,
            "history": self.history,
            "relations": self.relations,
        }

        try:

            path = get_save_path()

            path.write_text(
                json.dumps(data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            return True

        except Exception:

            return False

    # ========================================================
    # LOAD
    # ========================================================

    def load(self):

        path = get_save_path()

        if not path.exists():
            return False

        try:

            data = json.loads(path.read_text(encoding="utf-8"))

            for key, value in data.items():

                # Only accept known attributes, and merge dicts so a
                # save made by an older version (missing new techs
                # or values) does not wipe out the defaults.
                if not hasattr(self, key):
                    continue

                current = getattr(self, key)

                if isinstance(current, dict) and isinstance(value, dict):
                    current.update(value)
                else:
                    setattr(self, key, value)

            self.clamp()

            return True

        except Exception:

            return False


# ============================================================
# GAME USER INTERFACE
# ============================================================

class GameUI(BoxLayout):

    def __init__(self, civilization, **kwargs):

        super().__init__(
            orientation="vertical",
            spacing=dp(6),
            padding=dp(8),
            **kwargs
        )

        self.civ = civilization
        self.open_popup = None

        # ----------------------------------------------------
        # TITLE
        # ----------------------------------------------------

        title = Label(
            text="HUMAN LEGACY",
            font_size=sp(25),
            bold=True,
            size_hint_y=None,
            height=dp(45),
        )

        self.add_widget(title)

        # ----------------------------------------------------
        # INFORMATION PANEL
        # ----------------------------------------------------

        self.info = Label(
            size_hint_y=None,
            height=dp(150),
            halign="left",
            valign="top",
            font_size=sp(14),
        )

        self.info.bind(
            size=lambda obj, value: setattr(obj, "text_size", value)
        )

        self.add_widget(self.info)

        # ----------------------------------------------------
        # MAIN BUTTONS
        # ----------------------------------------------------

        buttons = GridLayout(
            cols=2,
            spacing=dp(4),
            size_hint_y=None,
            height=dp(96),
        )

        controls = [
            ("Advance", self.advance),
            ("Research", self.show_research),
            ("Values", self.show_values),
            ("History", self.show_history),
        ]

        for text, function in controls:

            button = Button(text=text, font_size=sp(15))

            button.bind(on_release=lambda _, f=function: f())

            buttons.add_widget(button)

        self.add_widget(buttons)

        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        self.message = Label(
            text="Shape the future of humanity.",
            size_hint_y=None,
            height=dp(55),
            font_size=sp(14),
        )

        self.add_widget(self.message)

        # ----------------------------------------------------
        # SAVE BUTTON
        # ----------------------------------------------------

        save_button = Button(
            text="SAVE GAME",
            size_hint_y=None,
            height=dp(48),
            font_size=sp(15),
        )

        save_button.bind(on_release=self.save_game)

        self.add_widget(save_button)

        # Android hardware back button should close an open popup
        # instead of closing the whole app.
        Window.bind(on_keyboard=self._on_keyboard)

        self.refresh()

    # ========================================================
    # BACK BUTTON HANDLING
    # ========================================================

    def _on_keyboard(self, window, key, *args):

        if key == 27 and self.open_popup is not None:

            self.open_popup.dismiss()

            return True

        return False

    def _open(self, popup):

        self.open_popup = popup

        popup.bind(on_dismiss=lambda *_: setattr(self, "open_popup", None))

        popup.open()

    # ========================================================
    # REFRESH SCREEN
    # ========================================================

    def refresh(self):

        tech_count = sum(self.civ.techs.values())

        self.info.text = (
            f"Year: {self.civ.year:,}    "
            f"Population: {self.civ.population:,.0f}\n"
            f"Government: {self.civ.government}\n"
            f"Knowledge: {self.civ.knowledge:.1f}    "
            f"Science: {self.civ.science:.1f}\n"
            f"Stability: {self.civ.stability:.0f}%    "
            f"Happiness: {self.civ.happiness:.0f}%\n"
            f"Culture: {self.civ.culture:.1f}    "
            f"Wealth: {self.civ.wealth:.1f}\n"
            f"Environment: {self.civ.environment:.0f}%    "
            f"Technologies: {tech_count}"
        )

    # ========================================================
    # ADVANCE
    # ========================================================

    def advance(self, *_):

        self.message.text = self.civ.advance()
        self.refresh()

    # ========================================================
    # RESEARCH WINDOW
    # ========================================================

    def show_research(self, *_):

        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(5))

        scroll = ScrollView(do_scroll_x=False)

        grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)

        grid.bind(minimum_height=grid.setter("height"))

        options = self.civ.available_research()

        if not options:

            grid.add_widget(
                Label(
                    text="No research is currently available.",
                    size_hint_y=None,
                    height=dp(50),
                    font_size=sp(14),
                )
            )

        for name, cost, description in options:

            button = Button(
                text=f"{name} | Cost: {cost}\n{description}",
                size_hint_y=None,
                height=dp(72),
                font_size=sp(13),
                halign="center",
            )

            button.bind(
                on_release=lambda _, n=name, c=cost: self.do_research(n, c)
            )

            grid.add_widget(button)

        scroll.add_widget(grid)
        root.add_widget(scroll)

        close = Button(text="Close", size_hint_y=None, height=dp(45))

        root.add_widget(close)

        popup = Popup(
            title="Research & Human Knowledge",
            content=root,
            size_hint=(0.94, 0.85),
        )

        close.bind(on_release=popup.dismiss)

        self._open(popup)

    # ========================================================
    # PERFORM RESEARCH
    # ========================================================

    def do_research(self, name, cost):

        success, message = self.civ.research(name, cost)

        self.message.text = message

        if self.open_popup is not None:
            self.open_popup.dismiss()

        self.refresh()

    # ========================================================
    # VALUES WINDOW
    # ========================================================

    def show_values(self, *_):

        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(5))

        scroll = ScrollView(do_scroll_x=False)

        grid = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)

        grid.bind(minimum_height=grid.setter("height"))

        for name, value in self.civ.values.items():

            grid.add_widget(
                Label(
                    text=f"{name}: {value:.0f}",
                    size_hint_y=None,
                    height=dp(27),
                    font_size=sp(13),
                )
            )

            grid.add_widget(
                ProgressBar(max=100, value=value, size_hint_y=None, height=dp(17))
            )

        grid.add_widget(
            Label(
                text=f"Government: {self.civ.government}",
                size_hint_y=None,
                height=dp(45),
                font_size=sp(14),
            )
        )

        for name in [
            "Science", "Freedom", "Authority", "Equality",
            "Tradition", "Militarism", "Religion", "Individualism",
        ]:

            button = Button(
                text=f"Promote {name}",
                size_hint_y=None,
                height=dp(44),
                font_size=sp(14),
            )

            button.bind(on_release=lambda _, n=name: self.change_value(n))

            grid.add_widget(button)

        scroll.add_widget(grid)
        root.add_widget(scroll)

        close = Button(text="Close", size_hint_y=None, height=dp(45))

        root.add_widget(close)

        popup = Popup(
            title="Society & Values",
            content=root,
            size_hint=(0.94, 0.90),
        )

        close.bind(on_release=popup.dismiss)

        self._open(popup)

    # ========================================================
    # CHANGE SOCIAL VALUE
    # ========================================================

    def change_value(self, name):

        self.civ.policy(name)

        self.message.text = f"Society changed: {name}"

        if self.open_popup is not None:
            self.open_popup.dismiss()

        self.refresh()

    # ========================================================
    # HISTORY WINDOW
    # ========================================================

    def show_history(self, *_):

        root = BoxLayout(orientation="vertical", padding=dp(8))

        history_text = "\n".join(self.civ.history[-150:]) or "No events recorded yet."

        scroll = ScrollView(do_scroll_x=False)

        label = Label(
            text=history_text,
            halign="left",
            valign="top",
            size_hint_y=None,
            size_hint_x=1,
            font_size=sp(13),
            padding=(dp(4), dp(4)),
        )

        # Wrap text to the available width instead of overflowing
        # horizontally off the screen.
        label.bind(
            width=lambda obj, w: setattr(obj, "text_size", (w, None))
        )

        label.bind(
            texture_size=lambda obj, size: setattr(obj, "height", size[1])
        )

        scroll.add_widget(label)
        root.add_widget(scroll)

        close = Button(text="Close", size_hint_y=None, height=dp(45))

        root.add_widget(close)

        popup = Popup(
            title="History of Humanity",
            content=root,
            size_hint=(0.94, 0.85),
        )

        close.bind(on_release=popup.dismiss)

        self._open(popup)

    # ========================================================
    # SAVE
    # ========================================================

    def save_game(self, *_):

        if self.civ.save():
            self.message.text = "Game saved successfully."
        else:
            self.message.text = "Error: could not save the game."

    # ========================================================
    # LOAD
    # ========================================================

    def load_game(self):

        if self.civ.load():
            self.message.text = "Saved civilization loaded."
            self.refresh()


# ============================================================
# KIVY APP
# ============================================================

class HumanLegacyApp(App):

    def build(self):

        self.title = "Human Legacy"

        civilization = Civilization()

        ui = GameUI(civilization)

        ui.load_game()

        return ui

    def on_stop(self):

        try:

            if self.root:
                self.root.civ.save()

        except Exception:

            pass


# ============================================================
# START GAME
# ============================================================

if __name__ == "__main__":

    HumanLegacyApp().run()
