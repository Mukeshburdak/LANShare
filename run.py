import os

from database.db import create_database
from gui.main import root


def setup():

    folders = [
        "received_files",
        "database"
    ]

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    create_database()


if __name__ == "__main__":

    setup()

    root.mainloop()
