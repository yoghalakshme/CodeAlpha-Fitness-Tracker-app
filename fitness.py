import sqlite3
from tkinter import *
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from datetime import date
import threading, time

# === Theme Settings ===
theme_color = "#dbe9f4"
font = ("Segoe UI", 11)

# === Splash Screen ===
def show_welcome():
    splash = Toplevel()
    splash.geometry("500x400")
    splash.overrideredirect(True)
    splash.configure(bg=theme_color)
    try:
        logo = Image.open("gym_logo.png").resize((120, 120))
        logo_photo = ImageTk.PhotoImage(logo)
        Label(splash, image=logo_photo, bg=theme_color).pack(pady=30)
        splash.logo_photo = logo_photo
    except:
        Label(splash, text="🏋️‍♂️", font=("Arial", 40), bg=theme_color).pack(pady=30)
    Label(splash, text="Welcome to FitTrack", font=("Segoe UI", 18, "bold"), bg=theme_color).pack(pady=5)
    Label(splash, text="Your daily motivation companion 💪", font=font, bg=theme_color).pack()
    splash.after(2500, splash.destroy)
    splash.mainloop()

# === Main App ===
root = Tk()
root.title("Fitness Tracker App")
root.geometry("500x700")
root.configure(bg=theme_color)

# === Database Setup ===
conn = sqlite3.connect('fitness.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS fitness (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date TEXT,
    steps INTEGER,
    workout TEXT,
    duration INTEGER,
    calories INTEGER
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY,
    step_goal INTEGER,
    calorie_goal INTEGER
)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS streaks (
    date TEXT PRIMARY KEY
)''')
conn.commit()

# === Notebook Layout ===
notebook = ttk.Notebook(root)
notebook.pack(fill=BOTH, expand=True)

tab_log = Frame(notebook, bg=theme_color)
tab_chart = Frame(notebook, bg=theme_color)
tab_cal = Frame(notebook, bg=theme_color)
tab_goal = Frame(notebook, bg=theme_color)

notebook.add(tab_log, text="🏋️ Log")
notebook.add(tab_chart, text="📊 Analytics")
notebook.add(tab_cal, text="📅 Calendar")
notebook.add(tab_goal, text="🎯 Goals")

# === Log Tab ===
try:
    logo_img = Image.open("gym_logo.png").resize((100, 100))
    logo_photo = ImageTk.PhotoImage(logo_img)
    Label(tab_log, image=logo_photo, bg=theme_color).pack(pady=10)
except:
    Label(tab_log, text="🏋️", font=("Arial", 40), bg=theme_color).pack(pady=10)

Label(tab_log, text="Steps", bg=theme_color, font=font).pack()
entry_steps = Entry(tab_log); entry_steps.pack()

Label(tab_log, text="Workout Type", bg=theme_color, font=font).pack()
entry_workout = Entry(tab_log); entry_workout.pack()

Label(tab_log, text="Duration (min)", bg=theme_color, font=font).pack()
entry_duration = Entry(tab_log); entry_duration.pack()

Label(tab_log, text="Calories Burned", bg=theme_color, font=font).pack()
entry_calories = Entry(tab_log); entry_calories.pack()

listbox = Listbox(tab_log, width=50)
listbox.pack(pady=10, fill=BOTH, expand=True)

streak_label = Label(tab_log, text="", bg=theme_color, font=font)
streak_label.pack()

# === Functions ===
def refresh_summary():
    listbox.delete(0, END)
    cursor.execute("SELECT * FROM fitness ORDER BY entry_date DESC")
    for row in cursor.fetchall():
        listbox.insert(END, f"{row[1]} | {row[2]} steps | {row[3]} {row[4]}min | {row[5]} kcal")

def update_streak_label():
    cursor.execute("SELECT COUNT(*) FROM streaks")
    count = cursor.fetchone()[0]
    streak_label.config(text=f"🔥 Streak: {count} days")

def celebrate_popup():
    win = Toplevel()
    win.title("Goal Met!")
    win.configure(bg=theme_color)
    Label(win, text="🎉 You hit your goal today!", font=("Helvetica", 14, "bold"), bg=theme_color).pack(pady=20)
    Button(win, text="Awesome!", command=win.destroy).pack()

def save_entry():
    try:
        entry_date = date.today().isoformat()
        steps = int(entry_steps.get() or 0)
        workout = entry_workout.get()
        duration = int(entry_duration.get() or 0)
        calories = int(entry_calories.get() or 0)
        cursor.execute("INSERT INTO fitness (entry_date, steps, workout, duration, calories) VALUES (?, ?, ?, ?, ?)",
                       (entry_date, steps, workout, duration, calories))
        conn.commit()
        cursor.execute("SELECT step_goal, calorie_goal FROM goals")
        goals = cursor.fetchone()
        if goals and steps >= goals[0] and calories >= goals[1]:
            cursor.execute("INSERT OR IGNORE INTO streaks (date) VALUES (?)", (entry_date,))
            conn.commit()
            celebrate_popup()
        refresh_summary()
        update_streak_label()
        messagebox.showinfo("Saved", f"Activity logged!\nCalories burned: {calories} kcal")
    except Exception as e:
        messagebox.showerror("Error", f"Problem saving entry: {e}")

Button(tab_log, text="Save Entry", command=save_entry).pack(pady=10)

# === Analytics Tab ===
def show_analytics():
    cursor.execute("SELECT entry_date, steps, workout, duration, calories FROM fitness ORDER BY entry_date")
    data = cursor.fetchall()
    if not data:
        messagebox.showinfo("No Data", "Please log an activity first.")
        return
    dates = [row[0] for row in data]
    steps = [row[1] for row in data]
    calories = [row[4] for row in data]  # Correct index
    plt.figure(figsize=(8, 4))
    plt.plot(dates, steps, label="Steps")
    plt.plot(dates, calories, label="Calories Burned", color='orange')
    plt.xlabel("Date"); plt.ylabel("Values")
    plt.title("Fitness Progress"); plt.legend()
    plt.xticks(rotation=45); plt.tight_layout()
    plt.show()

# === Add Button to Analytics Tab (outside function!)
Button(tab_chart, text="Show Analytics", command=show_analytics).pack(pady=50)

# === Calendar Tab ===
def show_calendar():
    cal = Calendar(tab_cal, selectmode='day')
    cal.pack(pady=10)
    def show_data():
        selected = cal.get_date()
        cursor.execute("SELECT * FROM fitness WHERE entry_date = ?", (selected,))
        row = cursor.fetchone()
        if row:
            messagebox.showinfo("Entry", f"Steps: {row[2]}\nWorkout: {row[3]}\nDuration: {row[4]}\nCalories: {row[5]}")
        else:
            messagebox.showinfo("No Entry", "No data for that day.")
    Button(tab_cal, text="Show Entry", command=show_data).pack()

show_calendar()

# === Goals Tab ===
def set_goals():
    win = Toplevel()
    win.title("Set Goals"); win.configure(bg=theme_color)
    Label(win, text="Step Goal", bg=theme_color).pack()
    step_input = Entry(win); step_input.pack()
    Label(win, text="Calorie Goal", bg=theme_color).pack()
    cal_input = Entry(win); cal_input.pack()
    def save():
        cursor.execute("DELETE FROM goals")
        cursor.execute("INSERT INTO goals (step_goal, calorie_goal) VALUES (?, ?)",
                       (int(step_input.get()), int(cal_input.get())))
        conn.commit(); win.destroy()
    Button(win, text="Save", command=save).pack(pady=5)

Button(tab_goal, text="Set Daily Goals", command=set_goals).pack(pady=50)

# === Reminder Loop ===
def reminder_loop():
    while True:
        if time.strftime("%H:%M") == "19:00":
            messagebox.showinfo("Reminder", "🏃 Time to log your fitness!")
        time.sleep(60)

threading.Thread(target=reminder_loop, daemon=True).start()

# === Launch App ===
show_welcome()
refresh