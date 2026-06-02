"""MorningRush-IELTS — desktop IELTS vocabulary trainer."""

import sys
from db import init_db
from ui import run_ui


def main():
    init_db()
    if "--notray" in sys.argv:
        run_ui()
    else:
        try:
            from tray import run_with_tray
            run_with_tray()
        except ImportError:
            run_ui()


if __name__ == "__main__":
    main()
