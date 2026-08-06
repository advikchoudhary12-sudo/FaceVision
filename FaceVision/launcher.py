import customtkinter as ctk

from config import (
    CAMERA_PRESETS,
    DEFAULT_CAMERA,
    LAUNCHER_TITLE
)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


def run_launcher():

    selected_camera = {"value": None}

    app = ctk.CTk()
    app.title(LAUNCHER_TITLE)
    app.geometry("620x430")
    app.resizable(False, False)

    # ----------------------------
    # Title
    # ----------------------------

    title = ctk.CTkLabel(
        app,
        text="FaceVision",
        font=("Segoe UI", 30, "bold")
    )
    title.pack(pady=(20, 0))

    subtitle = ctk.CTkLabel(
        app,
        text="AI Facial Recognition System",
        font=("Segoe UI", 15)
    )
    subtitle.pack(pady=(0, 20))

    # ----------------------------
    # Description
    # ----------------------------

    description = (
        "FaceVision is an AI-powered facial recognition system\n"
        "capable of identifying known individuals and detecting\n"
        "unknown persons in real time.\n\n"
        "Select a camera source below."
    )

    desc = ctk.CTkLabel(
        app,
        text=description,
        justify="center",
        font=("Segoe UI", 13)
    )

    desc.pack()

    # ----------------------------
    # Camera Presets
    # ----------------------------

    ctk.CTkLabel(
        app,
        text="Camera Preset",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(25, 5))

    preset_var = ctk.StringVar(value=DEFAULT_CAMERA)

    url_var = ctk.StringVar(
        value=str(CAMERA_PRESETS[DEFAULT_CAMERA])
    )

    def preset_changed(choice):
        url_var.set(str(CAMERA_PRESETS[choice]))

    preset_box = ctk.CTkOptionMenu(
        app,
        values=list(CAMERA_PRESETS.keys()),
        variable=preset_var,
        command=preset_changed,
        width=420
    )

    preset_box.pack()

    # ----------------------------
    # OR
    # ----------------------------

    ctk.CTkLabel(
        app,
        text="OR",
        font=("Segoe UI", 13, "bold")
    ).pack(pady=(18, 5))

    # ----------------------------
    # Custom Source
    # ----------------------------

    ctk.CTkLabel(
        app,
        text="Custom Camera Source (index, URL, RTSP, or video file)",
        font=("Segoe UI", 14, "bold")
    ).pack()

    entry = ctk.CTkEntry(
        app,
        width=470,
        textvariable=url_var
    )

    entry.pack(pady=(8, 25))

    status_var = ctk.StringVar(value="Choose a preset or enter a custom source.")
    status_label = ctk.CTkLabel(
        app,
        textvariable=status_var,
        font=("Segoe UI", 12),
        text_color="gray70",
    )
    status_label.pack(pady=(-17, 12))

    # ----------------------------
    # Start Button
    # ----------------------------

    def start():

        value = url_var.get().strip()

        if not value:
            status_var.set("Enter a camera index or stream URL first.")
            status_label.configure(text_color="#ff6b6b")
            return

        if value.isdigit():
            selected_camera["value"] = int(value)
        else:
            selected_camera["value"] = value

        status_var.set(f"Starting: {selected_camera['value']}")
        status_label.configure(text_color="#75d37b")

        start_button.configure(
            text="Starting...",
            state="disabled"
        )

        app.after(300, app.destroy)

    start_button = ctk.CTkButton(
        app,
        text="START",
        width=170,
        height=40,
        command=start
    )

    start_button.pack()

    app.mainloop()

    return selected_camera["value"]


if __name__ == "__main__":
    # Running this file is the normal user-facing entry point.  `main.py`
    # imports `run_launcher`, so importing it here does not create a loop.
    from main import main

    main()
