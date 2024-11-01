import customtkinter as ctk
import pygame
import tkinter as tk
from PIL import Image

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Available Modes: "light", "dark", "system"
ctk.set_default_color_theme("dark-blue")  # Available Themes: "blue", "dark-blue", "green", "sweetkind"

default_size = "400x650"
minimized_size = "300x150"

class PomodoroTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry(default_size)  # Default window size

        # Initialize pygame for notification sound
        pygame.mixer.init()

        # State to track whether the window is minimized or not
        self.is_minimized = False

        # Load icons for minimize and maximize using CTkImage
        self.minimize_icon = ctk.CTkImage(Image.open("minimize.png"), size=(20, 20))
        self.maximize_icon = ctk.CTkImage(Image.open("maximize.png"), size=(20, 20))

        # CustomTkinter Frame with dark background color
        self.frame = ctk.CTkFrame(root)
        self.frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Minimize Button (initially set with minimize icon)
        self.minimize_button = ctk.CTkButton(self.frame, image=self.minimize_icon, text="",
                                             width=20, height=20, corner_radius=0, fg_color="transparent", command=self.toggle_minimize)
        self.minimize_button.pack(anchor="ne", padx=0, pady=0)  # Positioned in the top-right corner

        # Timer Label
        self.timer_label = ctk.CTkLabel(self.frame, text="00:00", font=("Helvetica", 48))
        self.timer_label.pack(pady=20)

        # Work Time Input
        self.work_time_label = ctk.CTkLabel(self.frame, text="Work Time (minutes):", font=("Helvetica", 14))
        self.work_time_label.pack()
        self.work_time = tk.StringVar(value="25")  # Use StringVar to handle empty input and avoid errors
        self.work_time_entry = ctk.CTkEntry(self.frame, textvariable=self.work_time)
        self.work_time_entry.pack(pady=10)

        # Break Time Input
        self.break_time_label = ctk.CTkLabel(self.frame, text="Break Time (minutes):", font=("Helvetica", 14))
        self.break_time_label.pack()
        self.break_time = tk.StringVar(value="5")  # StringVar to prevent issues with empty input
        self.break_time_entry = ctk.CTkEntry(self.frame, textvariable=self.break_time)
        self.break_time_entry.pack(pady=10)

        # Number of Rounds Input
        self.rounds_label = ctk.CTkLabel(self.frame, text="Rounds:", font=("Helvetica", 14))
        self.rounds_label.pack()
        self.rounds = tk.StringVar(value="4")
        self.rounds_entry = ctk.CTkEntry(self.frame, textvariable=self.rounds)
        self.rounds_entry.pack(pady=10)

        # Rest Time Input
        self.rest_time_label = ctk.CTkLabel(self.frame, text="Rest Time (minutes):", font=("Helvetica", 14))
        self.rest_time_label.pack()
        self.rest_time = tk.StringVar(value="30")
        self.rest_time_entry = ctk.CTkEntry(self.frame, textvariable=self.rest_time)
        self.rest_time_entry.pack(pady=10)

        # Total Work Duration Label
        self.total_work_duration = 0  # Total work duration in minutes
        self.total_work_label = ctk.CTkLabel(self.frame, text="Total Work: 0 mins", font=("Helvetica", 14))
        self.total_work_label.pack(pady=10)

        # Control Buttons (now grouped into a frame)
        self.button_frame = ctk.CTkFrame(self.frame)
        self.button_frame.pack(pady=10)

        self.start_button = ctk.CTkButton(self.button_frame, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=5, pady=5)

        self.stop_button = ctk.CTkButton(self.button_frame, text="Stop", command=self.stop_timer)
        self.stop_button.grid(row=0, column=1, padx=5, pady=5)

        self.resume_button = ctk.CTkButton(self.button_frame, text="Resume", command=self.resume_timer)
        self.resume_button.grid(row=1, column=0, padx=5, pady=5)

        self.reset_button = ctk.CTkButton(self.button_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=1, column=1, padx=5, pady=5)

        # Timer Variables
        self.time_left = 0
        self.cycle_count = 0
        self.running = False
        self.paused = False
        self.current_phase = None  # 'work', 'break', or 'rest'
        self.timer_id = None

    def toggle_minimize(self):
        """Toggle between minimized view (only showing the timer) and full view."""
        if not self.is_minimized:
            # Minimize the window to show only the timer
            self.root.geometry(minimized_size)  # Shrink the window
            self.minimize_button.configure(image=self.maximize_icon)  # Switch to maximize icon
            self.work_time_label.pack_forget()
            self.work_time_entry.pack_forget()
            self.break_time_label.pack_forget()
            self.break_time_entry.pack_forget()
            self.rounds_label.pack_forget()
            self.rounds_entry.pack_forget()
            self.rest_time_label.pack_forget()
            self.rest_time_entry.pack_forget()
            self.total_work_label.pack_forget()
            self.button_frame.pack_forget()
        else:
            # Restore the window to full size
            self.root.geometry(default_size)  # Restore original size
            self.minimize_button.configure(image=self.minimize_icon)  # Switch to minimize icon
            self.work_time_label.pack()
            self.work_time_entry.pack(pady=10)
            self.break_time_label.pack()
            self.break_time_entry.pack(pady=10)
            self.rounds_label.pack()
            self.rounds_entry.pack(pady=10)
            self.rest_time_label.pack()
            self.rest_time_entry.pack(pady=10)
            self.total_work_label.pack(pady=10)
            self.button_frame.pack(pady=10)
        self.is_minimized = not self.is_minimized  # Toggle the state

    def start_timer(self):
        if not self.running:
            self.running = True
            self.paused = False
            self.cycle_count = 0
            self.start_work()

    def stop_timer(self):
        if self.running:
            self.root.after_cancel(self.timer_id)
            self.paused = True
            self.running = False

    def resume_timer(self):
        if self.paused and not self.running:
            self.running = True
            self.paused = False
            self.count_down()

    def reset_timer(self):
        if self.timer_id is not None:  # Only cancel if there's an active timer
            self.root.after_cancel(self.timer_id)
        self.timer_label.configure(text="00:00")  # Use 'configure' instead of 'config'
        self.running = False
        self.paused = False

        # Reset input fields to default values
        self.work_time.set("25")
        self.break_time.set("5")
        self.rounds.set("4")
        self.rest_time.set("30")

        # Reset total work duration
        self.total_work_duration = 0
        self.total_work_label.configure(text="Total Work: 0 mins")  # Use 'configure'

    def start_work(self):
        self.current_phase = 'work'
        self.time_left = int(self.work_time.get()) * 60  # Ensure the input is valid
        self.count_down()

    def start_break(self):
        self.current_phase = 'break'
        self.time_left = int(self.break_time.get()) * 60  # Ensure the input is valid
        self.count_down()

    def start_rest(self):
        self.current_phase = 'rest'
        self.time_left = int(self.rest_time.get()) * 60  # Ensure the input is valid
        self.count_down()

    def count_down(self):
        if self.time_left >= 0:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")  # Use 'configure' for CTkLabel
            self.time_left -= 1
            self.timer_id = self.root.after(1000, self.count_down)
        else:
            self.end_phase()

    def end_phase(self):
        self.root.after_cancel(self.timer_id)  # Ensure the previous timer is canceled
        self.play_notification_sound()  # Play sound
        if self.current_phase == 'work':
            self.total_work_duration += int(self.work_time.get())  # Add completed work duration
            self.total_work_label.configure(text=f"Total Work: {self.total_work_duration} mins")  # Use 'configure'
            self.show_popup("End of work!", self.start_break)
        elif self.current_phase == 'break':
            self.show_popup("End of break!", self.start_work)
        elif self.current_phase == 'rest':
            self.show_popup("End of rest!", self.start_work)

    def play_notification_sound(self):
        pygame.mixer.music.load("electronic-timer-multiple-beeps.wav")  # Load the notification sound
        pygame.mixer.music.play(-1)  # Play continuously until stopped

    def stop_notification_sound(self):
        pygame.mixer.music.stop()  # Stop the sound when the user closes the popup

    def show_popup(self, message, next_phase_callback):
        self.play_notification_sound()  # Play sound when the popup appears

        popup = ctk.CTkToplevel()
        popup.title("Notification")
        ctk.CTkLabel(popup, text=message, font=("Helvetica", 24)).pack(pady=10)

        # Ensure the popup is on top
        popup.lift()
        popup.attributes('-topmost', True)

        def close_popup():
            self.stop_notification_sound()  # Stop the sound when the popup is closed
            popup.destroy()
            next_phase_callback()  # Start the next phase only after closing the popup

        ctk.CTkButton(popup, text="Go On!", command=close_popup).pack(pady=10)


if __name__ == "__main__":
    root = ctk.CTk()  # Initialize CustomTkinter window
    app = PomodoroTimer(root)
    root.mainloop()  # Start the Tkinter event loop
