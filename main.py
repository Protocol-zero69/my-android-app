from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
import sqlite3
from datetime import datetime

# =========================
# DATABASE SETUP
# =========================

conn = sqlite3.connect("survey_assistant.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY,
    age INTEGER,
    education TEXT,
    employment TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS survey_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    survey_name TEXT,
    completion_date TEXT
)
""")

conn.commit()

# =========================
# ATTENTION CHECK PATTERNS
# =========================

patterns = [
    "please select",
    "read carefully",
    "attention check",
    "choose strongly agree",
    "to show you are paying attention"
]


def show_popup(title, message):
    popup = Popup(
        title=title,
        content=Label(text=message),
        size_hint=(0.8, 0.4)
    )
    popup.open()


class SurveyAssistant(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = 10
        self.spacing = 8

        # ---------- PROFILE SECTION ----------
        self.add_widget(Label(text="Profile", size_hint_y=None, height=30))

        self.age_entry = TextInput(hint_text="Age", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.age_entry)

        self.education_entry = TextInput(hint_text="Education", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.education_entry)

        self.employment_entry = TextInput(hint_text="Employment", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.employment_entry)

        save_profile_btn = Button(text="Save Profile", size_hint_y=None, height=45)
        save_profile_btn.bind(on_press=self.save_profile)
        self.add_widget(save_profile_btn)

        # ---------- QUESTION ANALYZER ----------
        self.add_widget(Label(text="Question Analyzer", size_hint_y=None, height=30))

        self.question_box = TextInput(hint_text="Paste survey question here", size_hint_y=None, height=100)
        self.add_widget(self.question_box)

        analyze_btn = Button(text="Analyze", size_hint_y=None, height=45)
        analyze_btn.bind(on_press=self.analyze_question)
        self.add_widget(analyze_btn)

        self.result_label = Label(text="", size_hint_y=None, height=50)
        self.add_widget(self.result_label)

        # ---------- SURVEY HISTORY ----------
        self.add_widget(Label(text="Survey History", size_hint_y=None, height=30))

        self.survey_entry = TextInput(hint_text="Survey name", multiline=False, size_hint_y=None, height=40)
        self.add_widget(self.survey_entry)

        save_survey_btn = Button(text="Save Survey", size_hint_y=None, height=45)
        save_survey_btn.bind(on_press=self.save_survey)
        self.add_widget(save_survey_btn)

        view_history_btn = Button(text="View History", size_hint_y=None, height=45)
        view_history_btn.bind(on_press=self.view_history)
        self.add_widget(view_history_btn)

        self.history_box = TextInput(text="", readonly=True, size_hint_y=None, height=150)
        scroll = ScrollView(size_hint_y=None, height=150)
        scroll.add_widget(self.history_box)
        self.add_widget(scroll)

        self.load_profile()

    # ---------- DATABASE FUNCTIONS ----------

    def save_profile(self, instance):
        age = self.age_entry.text
        education = self.education_entry.text
        employment = self.employment_entry.text

        cursor.execute("DELETE FROM profile")
        cursor.execute("""
        INSERT INTO profile(age, education, employment)
        VALUES (?, ?, ?)
        """, (age, education, employment))
        conn.commit()

        show_popup("Success", "Profile saved successfully.")

    def load_profile(self):
        cursor.execute("SELECT age, education, employment FROM profile LIMIT 1")
        result = cursor.fetchone()

        if result:
            self.age_entry.text = str(result[0]) if result[0] is not None else ""
            self.education_entry.text = result[1] or ""
            self.employment_entry.text = result[2] or ""

    def save_survey(self, instance):
        survey_name = self.survey_entry.text

        if not survey_name:
            return

        cursor.execute("""
        INSERT INTO survey_history(survey_name, completion_date)
        VALUES (?, ?)
        """, (survey_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()

        self.survey_entry.text = ""
        show_popup("Saved", "Survey history recorded.")

    def view_history(self, instance):
        cursor.execute("""
        SELECT survey_name, completion_date
        FROM survey_history
        ORDER BY id DESC
        """)
        records = cursor.fetchall()

        lines = [f"{survey} - {date}" for survey, date in records]
        self.history_box.text = "\n".join(lines)

    # ---------- ATTENTION CHECK DETECTOR ----------

    def analyze_question(self, instance):
        question = self.question_box.text.lower()
        found = any(pattern in question for pattern in patterns)

        if found:
            self.result_label.text = "Possible attention-check wording detected. Read carefully."
        else:
            self.result_label.text = "No common attention-check phrases found."


class SurveyAssistantApp(App):
    def build(self):
        return SurveyAssistant()

    def on_stop(self):
        conn.close()


if __name__ == "__main__":
    SurveyAssistantApp().run()
