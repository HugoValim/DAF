from dataclasses import dataclass
from os import path
from qtpy.QtWidgets import QApplication, QWidget


def format_5_dec(val):
    return "{:.5f}".format(float(val))


def center_screen(widget: QWidget):
    """Center the launched GUI in the midle of the current screen"""
    frameGm = widget.frameGeometry()
    screen = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
    centerPoint = QApplication.desktop().screenGeometry(screen).center()
    frameGm.moveCenter(centerPoint)
    widget.move(frameGm.topLeft())


class Counter:
    """Class to be inherited and used to execute a statement after n interaction"""

    def execute_after_n_iter(self, number_of_iters: int) -> bool:
        if self.iter_counter == 0:
            self.iter_counter += 1
            return True
        self.iter_counter += 1
        if self.iter_counter == number_of_iters:
            self.iter_counter = 0
        return False


@dataclass
class Icons:
    pixmap_path: path = path.join(path.dirname(path.realpath(__file__)), "ui/icons")
    check: path = path.join(pixmap_path, "check.svg")
    add: path = path.join(pixmap_path, "add.svg")
    ban: path = path.join(pixmap_path, "ban.svg")
    check: path = path.join(pixmap_path, "check.svg")
    pen: path = path.join(pixmap_path, "pen.svg")
    refresh: path = path.join(pixmap_path, "cached1.svg")
    folder: path = path.join(pixmap_path, "folder-open.svg")
