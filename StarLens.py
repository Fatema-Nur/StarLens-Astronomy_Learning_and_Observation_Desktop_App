import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3, webbrowser
from datetime import datetime

# -----------------------------
# Database setup
# -----------------------------
conn = sqlite3.connect("astronomy_app.db")
cur = conn.cursor()

# user table
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
""")

# quiz results table
cur.execute("""
CREATE TABLE IF NOT EXISTS quiz_results (
    username TEXT,
    score INTEGER,
    total INTEGER,
    level TEXT,
    time TEXT
)
""")

# completed topics
cur.execute("""
CREATE TABLE IF NOT EXISTS completed_topics (
    username TEXT,
    topic_id INTEGER
)
""")

# schedule data
cur.execute("""
CREATE TABLE IF NOT EXISTS schedules (
    username TEXT,
    time TEXT,
    object TEXT
)
""")
conn.commit()

# -----------------------------
# Base Screen
# -----------------------------
class BaseScreen:
    def __init__(self, parent, app):
        self.app = app
        self.parent = parent
        self.frame = tk.Frame(parent, bg="#050A1A")
        self.frame.pack(fill="both", expand=True)

    def destroy(self):
        self.frame.destroy()


# -----------------------------
# Main App Class
# -----------------------------
class AstronomyApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌌 Astronomy Learning App")
        self.root.geometry("1100x700")
        self.root.config(bg="#000010")

        self.canvas = tk.Canvas(self.root, bg="#000010", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.current_screen = None
        self.username = None
        self.show_screen("LoginScreen")

    def show_screen(self, name):
        if self.current_screen:
            self.current_screen.destroy()

        screens = {
            "LoginScreen": LoginScreen,
            "MainMenuScreen": MainMenuScreen,
            "ProfileScreen": ProfileScreen,
            "QuizScreen": QuizScreen,
            "LearningScreen": LearningScreen,
            "ScheduleScreen": ScheduleScreen
        }
        ScreenClass = screens[name]
        self.current_screen = ScreenClass(self.canvas, self)

    def run(self):
        self.root.mainloop()


# -----------------------------
# Login Screen
# -----------------------------
class LoginScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        tk.Label(self.frame, text="🔭 Astronomy Explorer", font=("Segoe UI", 28, "bold"), fg="#7CC7FF", bg="#050A1A").pack(pady=30)

        tk.Label(self.frame, text="Username:", bg="#050A1A", fg="white").pack()
        self.username = tk.Entry(self.frame, width=30)
        self.username.pack(pady=6)

        tk.Label(self.frame, text="Password:", bg="#050A1A", fg="white").pack()
        self.password = tk.Entry(self.frame, width=30, show="*")
        self.password.pack(pady=6)

        tk.Button(self.frame, text="Login", bg="#1768AC", fg="white", command=self.login).pack(pady=10)
        tk.Button(self.frame, text="Create Account", bg="#1C2E4A", fg="white", command=self.create_account).pack(pady=5)

    def login(self):
        uname = self.username.get().strip()
        pwd = self.password.get().strip()

        if not uname or not pwd:
            messagebox.showerror("Error", "Please fill all fields")
            return

        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
        user = cur.fetchone()
        if user:
            self.app.username = uname
            self.app.show_screen("MainMenuScreen")
        else:
            messagebox.showerror("Error", "Invalid username or password!")

    def create_account(self):
        uname = self.username.get().strip()
        pwd = self.password.get().strip()
        if not uname or not pwd:
            messagebox.showerror("Error", "Enter username and password")
            return
        try:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (uname, pwd))
            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
        except:
            messagebox.showerror("Error", "Username already exists!")


# -----------------------------
# Main Menu
# -----------------------------
class MainMenuScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        top = tk.Frame(self.frame, bg="#050A1A")
        top.pack(fill="x", padx=20, pady=10)
        tk.Label(top, text=f"Welcome, {app.username}", bg="#050A1A", fg="#7CC7FF", font=("Segoe UI", 16, "bold")).pack(side="left")

        tk.Button(top, text="Logout", bg="#A63232", fg="white", command=self.logout).pack(side="right")

        tk.Label(self.frame, text="🌠 Main Menu", font=("Segoe UI", 26, "bold"), fg="#7CC7FF", bg="#050A1A").pack(pady=20)

        menu = tk.Frame(self.frame, bg="#050A1A")
        menu.pack(pady=20)

        tk.Button(menu, text="👤 Profile", width=25, height=2, bg="#2A4173", fg="white", font=("Segoe UI", 13),
                  command=lambda: app.show_screen("ProfileScreen")).pack(pady=10)
        tk.Button(menu, text="📅 Schedule", width=25, height=2, bg="#1C2E4A", fg="white", font=("Segoe UI", 13),
                  command=lambda: app.show_screen("ScheduleScreen")).pack(pady=10)
        tk.Button(menu, text="🧠 Quiz", width=25, height=2, bg="#1768AC", fg="white", font=("Segoe UI", 13),
                  command=lambda: app.show_screen("QuizScreen")).pack(pady=10)
        tk.Button(menu, text="📖 Learning Section", width=25, height=2, bg="#3B7A57", fg="white", font=("Segoe UI", 13),
                  command=lambda: app.show_screen("LearningScreen")).pack(pady=10)

    def logout(self):
        self.app.username = None
        self.app.show_screen("LoginScreen")


# -----------------------------
# Profile Screen
# -----------------------------
class ProfileScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        tk.Button(self.frame, text="← Back to Menu", bg="#1C2E4A", fg="white",
                  command=lambda: app.show_screen("MainMenuScreen")).pack(anchor="nw", padx=12, pady=10)
        tk.Label(self.frame, text=f"{app.username}'s Profile", font=("Segoe UI", 22, "bold"), fg="#7CC7FF", bg="#050A1A").pack(pady=15)

        frame = tk.Frame(self.frame, bg="#050A1A")
        frame.pack(pady=10)

        cur.execute("SELECT score,total,level,time FROM quiz_results WHERE username=?", (app.username,))
        data = cur.fetchall()

        total_quizzes = len(data)
        avg = round(sum(d[0]/d[1] for d in data)/total_quizzes*100, 1) if total_quizzes else 0
        best = max((d[0]/d[1])*100 for d in data) if data else 0

        tk.Label(frame, text=f"Total Quizzes: {total_quizzes}", fg="white", bg="#050A1A", font=("Segoe UI", 14)).pack()
        tk.Label(frame, text=f"Average Score: {avg}%", fg="white", bg="#050A1A", font=("Segoe UI", 14)).pack()
        tk.Label(frame, text=f"Best Score: {best}%", fg="white", bg="#050A1A", font=("Segoe UI", 14)).pack()

        tk.Label(self.frame, text="\nRecent Quiz History", bg="#050A1A", fg="#7CC7FF", font=("Segoe UI", 14, "bold")).pack()
        box = tk.Text(self.frame, height=10, width=80, bg="#0B1733", fg="white")
        box.pack(pady=8)
        for row in data[-10:]:
            box.insert("end", f"{row[3]} — {row[2]} — Score: {row[0]}/{row[1]} ({round(row[0]/row[1]*100,1)}%)\n")
        box.config(state="disabled")


# -----------------------------
# Schedule Screen
# -----------------------------
class ScheduleScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.app = app

        tk.Button(self.frame, text="← Back to Menu", bg="#1C2E4A", fg="white",
                  command=lambda: app.show_screen("MainMenuScreen")).pack(anchor="nw", padx=14, pady=10)
        tk.Label(self.frame, text="📅 Celestial Observation Schedule", font=("Segoe UI", 20, "bold"),
                 fg="#7CC7FF", bg="#050A1A").pack(pady=8)

        self.container = tk.Frame(self.frame, bg="#050A1A")
        self.container.pack(padx=20, pady=12, fill="both", expand=True)
        self.render_schedule()

        tk.Button(self.frame, text="➕ Add / Edit Schedule", bg="#1768AC", fg="white", command=self.add_edit).pack(pady=8)

    def render_schedule(self):
        for w in self.container.winfo_children():
            w.destroy()

        cur.execute("SELECT time,object FROM schedules WHERE username=?", (self.app.username,))
        rows = cur.fetchall()
        if not rows:
            rows = [("Evening (7 PM)", "Venus – The Evening Star"), ("Midnight (12 AM)", "Orion Nebula"), ("Dawn (4 AM)", "Jupiter and Saturn")]

        for t, obj in rows:
            row = tk.Frame(self.container, bg="#050A1A")
            row.pack(fill="x", pady=6)
            tk.Label(row, text=f"{t}: {obj}", bg="#050A1A", fg="white", font=("Segoe UI", 12)).pack(side="left")
            tk.Button(row, text="Edit", bg="#2A4173", fg="white",
                      command=lambda time=t, object=obj: self.edit_item(time, object)).pack(side="right")

    def add_edit(self):
        t = simpledialog.askstring("Add Schedule", "Enter new time (e.g., 9 PM):")
        o = simpledialog.askstring("Add Schedule", "Enter new celestial object:")
        if t and o:
            cur.execute("INSERT INTO schedules (username, time, object) VALUES (?, ?, ?)", (self.app.username, t, o))
            conn.commit()
            self.render_schedule()

    def edit_item(self, time, obj):
        new_t = simpledialog.askstring("Edit Time", "Edit time:", initialvalue=time)
        new_o = simpledialog.askstring("Edit Object", "Edit object:", initialvalue=obj)
        if new_t and new_o:
            cur.execute("UPDATE schedules SET time=?, object=? WHERE username=? AND time=? AND object=?",
                        (new_t, new_o, self.app.username, time, obj))
            conn.commit()
            self.render_schedule()


# -----------------------------
# Learning Screen
# -----------------------------
LEARNING_TOPICS = [
    {"id": 1, "title": "Planets", "desc": "Learn about the planets of our solar system."},
    {"id": 2, "title": "Galaxies", "desc": "Explore the vast universe of galaxies beyond the Milky Way."},
    {"id": 3, "title": "Space Missions", "desc": "Discover NASA's greatest missions and achievements."},
    {"id": 4, "title": "Stars", "desc": "Understand how stars are born, live, and die."},
]

class LearningScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)

        tk.Button(self.frame, text="← Back to Menu", bg="#1C2E4A", fg="white",
                  command=lambda: app.show_screen("MainMenuScreen")).pack(anchor="nw", padx=14, pady=10)
        tk.Label(self.frame, text="📖 Astronomy Learning Section", font=("Segoe UI", 20, "bold"),
                 fg="#7CC7FF", bg="#050A1A").pack(pady=6)

        self.topics_frame = tk.Frame(self.frame, bg="#050A1A")
        self.topics_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.render_topics()

    def render_topics(self):
        for w in self.topics_frame.winfo_children():
            w.destroy()
        for t in LEARNING_TOPICS:
            card = tk.Frame(self.topics_frame, bg="#0B1733", bd=1, relief="ridge")
            card.pack(fill="x", pady=8)

            tk.Label(card, text=t["title"], bg="#0B1733", fg="#B8D8FF",
                     font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=10, pady=4)
            tk.Label(card, text=t["desc"], bg="#0B1733", fg="#DDEEFF",
                     wraplength=900, justify="left").pack(anchor="w", padx=10)

            btn_frame = tk.Frame(card, bg="#0B1733")
            btn_frame.pack(anchor="e", padx=10, pady=6)
            tk.Button(btn_frame, text="Read More", bg="#1768AC", fg="white",
                      command=lambda tid=t["id"]: self.open_topic(tid)).grid(row=0, column=0, padx=6)
            tk.Button(btn_frame, text="Search Google", bg="#2A4173", fg="white",
                      command=lambda q=t["title"]: webbrowser.open(f"https://www.google.com/search?q={q}+astronomy")).grid(row=0, column=1, padx=6)
            complete_btn = tk.Button(btn_frame, text="Mark Complete", bg="#3B7A57", fg="white",
                                     command=lambda tid=t["id"]: self.mark_complete(tid))
            complete_btn.grid(row=0, column=2, padx=6)

    def open_topic(self, tid):
        topic = next((x for x in LEARNING_TOPICS if x["id"] == tid), None)
        if topic:
            messagebox.showinfo(topic["title"], topic["desc"])

    def mark_complete(self, tid):
        cur.execute("INSERT INTO completed_topics (username, topic_id) VALUES (?, ?)", (self.app.username, tid))
        conn.commit()
        messagebox.showinfo("Completed", "Marked as completed!")


# -----------------------------
# Quiz Screen
# -----------------------------
class QuizScreen(BaseScreen):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.app = app
        self.current_question = 0
        self.score = 0
        self.questions = []
        self.age_level = ""

        tk.Button(self.frame, text="← Back to Menu", bg="#1C2E4A", fg="white",
                  command=lambda: app.show_screen("MainMenuScreen")).pack(anchor="nw", padx=14, pady=10)
        tk.Label(self.frame, text="🧠 Astronomy Quiz", font=("Segoe UI", 22, "bold"),
                 fg="#7CC7FF", bg="#050A1A").pack(pady=8)

        entry_frame = tk.Frame(self.frame, bg="#050A1A")
        entry_frame.pack(pady=10)
        tk.Label(entry_frame, text="Enter your Age:", bg="#050A1A", fg="white").pack(side="left")
        self.age_entry = tk.Entry(entry_frame, width=8)
        self.age_entry.pack(side="left", padx=8)

        tk.Button(self.frame, text="Start Quiz", bg="#1768AC", fg="white", command=self.start_quiz).pack(pady=12)

        self.q_container = tk.Frame(self.frame, bg="#050A1A")
        self.q_container.pack(fill="both", expand=True, padx=20, pady=10)

    def start_quiz(self):
        age_str = self.age_entry.get().strip()
        if not age_str.isdigit():
            messagebox.showerror("Input Error", "Please enter a valid numeric age.")
            return
        age = int(age_str)
        if 6 <= age <= 12:
            self.age_level = "Easy"
        elif 13 <= age <= 20:
            self.age_level = "Medium"
        else:
            self.age_level = "Hard"

        self.questions = self.get_questions(self.age_level)
        self.current_question = 0
        self.score = 0
        self.show_question()

    def get_questions(self, level):
        easy = [
            ("Which planet is known as the Red Planet?", ["Earth", "Mars", "Venus", "Jupiter"], "Mars"),
            ("What is the name of our galaxy?", ["Andromeda", "Milky Way", "Whirlpool", "Sombrero"], "Milky Way"),
            ("Which star is at the center of our solar system?", ["Polaris", "Sirius", "Sun", "Alpha Centauri"], "Sun"),
            ("How many planets are in the Solar System?", ["7", "8", "9", "10"], "8"),
            ("Which planet is closest to the Sun?", ["Mercury", "Venus", "Earth", "Mars"], "Mercury"),
            ("Which planet has rings?", ["Venus", "Saturn", "Earth", "Mars"], "Saturn"),
            ("What is the Moon?", ["A planet", "A star", "A satellite", "An asteroid"], "A satellite"),
            ("Which planet is known as the Blue Planet?", ["Neptune", "Earth", "Uranus", "Venus"], "Earth"),
            ("What causes day and night?", ["Earth's rotation", "Earth's revolution", "Moonlight", "Clouds"], "Earth's rotation"),
            ("What do we call a group of stars forming a pattern?", ["Cluster", "Galaxy", "Constellation", "Nebula"], "Constellation"),
        ]
        medium = [
            ("Which planet has the most moons?", ["Earth", "Mars", "Saturn", "Jupiter"], "Jupiter"),
            ("Who was the first person to walk on the Moon?", ["Yuri Gagarin", "Neil Armstrong", "Buzz Aldrin", "Michael Collins"], "Neil Armstrong"),
            ("Which planet is famous for its Great Red Spot?", ["Mars", "Jupiter", "Neptune", "Saturn"], "Jupiter"),
            ("What galaxy is nearest to the Milky Way?", ["Andromeda", "Whirlpool", "Sombrero", "Pinwheel"], "Andromeda"),
            ("Which space telescope was launched in 1990?", ["Hubble", "Kepler", "James Webb", "Spitzer"], "Hubble"),
            ("How long does Earth take to orbit the Sun?", ["24 hours", "1 month", "1 year", "10 years"], "1 year"),
            ("Which planet spins on its side?", ["Venus", "Uranus", "Neptune", "Mars"], "Uranus"),
            ("What is a supernova?", ["A new galaxy", "A dying star explosion", "A black hole", "A comet"], "A dying star explosion"),
            ("Which planet is known as the Morning Star?", ["Venus", "Mars", "Mercury", "Saturn"], "Venus"),
            ("Which planet has the shortest day?", ["Earth", "Mars", "Jupiter", "Venus"], "Jupiter"),
        ]
        hard = [
            ("What is the closest black hole to Earth called?", ["Cygnus X-1", "Sagittarius A*", "V616 Monocerotis", "M87*"], "V616 Monocerotis"),
            ("Which is the largest known star?", ["UY Scuti", "Betelgeuse", "Antares", "Sirius"], "UY Scuti"),
            ("What is the name of the first exoplanet discovered?", ["Kepler-22b", "51 Pegasi b", "Proxima b", "Gliese 581c"], "51 Pegasi b"),
            ("What kind of galaxy is the Milky Way?", ["Elliptical", "Spiral", "Irregular", "Lenticular"], "Spiral"),
            ("What element fuels stars?", ["Oxygen", "Hydrogen", "Carbon", "Helium"], "Hydrogen"),
            ("What is the event horizon?", ["Edge of a galaxy", "Boundary of a black hole", "Edge of universe", "Star explosion"], "Boundary of a black hole"),
            ("Which planet has the largest volcano?", ["Mars", "Earth", "Venus", "Jupiter"], "Mars"),
            ("Which NASA mission landed on Pluto?", ["Voyager 1", "Cassini", "New Horizons", "Juno"], "New Horizons"),
            ("How old is the universe approximately?", ["1 billion years", "5 billion years", "13.8 billion years", "100 million years"], "13.8 billion years"),
            ("What is the densest planet in the Solar System?", ["Earth", "Jupiter", "Mercury", "Neptune"], "Earth"),
        ]
        return {"Easy": easy, "Medium": medium, "Hard": hard}[level]

    def show_question(self):
        for w in self.q_container.winfo_children():
            w.destroy()
        if self.current_question < len(self.questions):
            q, options, correct = self.questions[self.current_question]
            tk.Label(self.q_container, text=f"Question {self.current_question+1}/{len(self.questions)}",
                     bg="#050A1A", fg="#7CC7FF", font=("Segoe UI", 16, "bold")).pack(pady=8)
            tk.Label(self.q_container, text=q, bg="#050A1A", fg="white", wraplength=900, font=("Segoe UI", 14)).pack(pady=6)
            for opt in options:
                tk.Button(self.q_container, text=opt, width=30, bg="#1C2E4A", fg="white",
                          command=lambda ans=opt: self.check_answer(ans)).pack(pady=6)
        else:
            self.save_result()
            messagebox.showinfo("Quiz Completed", f"🎉 You scored {self.score} out of {len(self.questions)}")
            self.app.show_screen("ProfileScreen")

    def check_answer(self, answer):
        correct = self.questions[self.current_question][2]
        if answer == correct:
            self.score += 1
        self.current_question += 1
        self.show_question()

    def save_result(self):
        cur.execute("INSERT INTO quiz_results (username, score, total, level, time) VALUES (?, ?, ?, ?, ?)",
                    (self.app.username, self.score, len(self.questions), self.age_level, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()


# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    app = AstronomyApp()
    app.run()
