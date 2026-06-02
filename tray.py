"""System tray support (optional, requires pystray + Pillow)."""

from ui import VocabApp


def run_with_tray():
    try:
        import pystray
        from PIL import Image, ImageDraw
    except ImportError:
        print("pystray not installed, running without tray icon")
        from ui import run_ui
        run_ui()
        return

    app = VocabApp()

    def create_icon():
        img = Image.new("RGB", (64, 64), "#7C3AED")
        draw = ImageDraw.Draw(img)
        draw.rectangle([8, 8, 56, 56], fill="white")
        draw.text((14, 14), "I", fill="#7C3AED")
        return img

    def on_show(icon, item):
        icon.notify("Opening...")
        app.root.after(0, app.show_window)

    def on_quit(icon, item):
        icon.stop()
        app.root.after(0, app.root.destroy)

    icon = pystray.Icon(
        "IELTS Vocab",
        create_icon(),
        "IELTS 每日单词",
        menu=pystray.Menu(
            pystray.MenuItem("显示", on_show),
            pystray.MenuItem("退出", on_quit),
        ),
    )

    import threading
    threading.Thread(target=icon.run, daemon=True).start()
    app.run()
