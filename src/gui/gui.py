#!/usr/bin/env python3.9

import json
from itertools import chain
import sys
from pathlib import Path
import webbrowser
from pprint import pprint as pp

from PyQt5.QtWidgets import (QMainWindow, QApplication, QVBoxLayout, QLabel,
                             QPushButton, QWidget, QHBoxLayout, QAction, QMenu,
                             QProgressBar, QMessageBox, QTabWidget,
                             QGridLayout, QLineEdit, QCheckBox, QTableView,
                             QTextEdit, QCompleter, QInputDialog, QDialog,
                             QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPalette, QFont, QPixmap, QColor, QKeySequence

from user_settings import (user_age, user_life_expected, shortcuts, n_session,
                           n_to_review, questions, gui_font_size)
from src.gui.PandasModel import PandasModel
from src.backend.backend import (pick_entries, get_meta_from_content,
                                 add_new_entry, shortcut_and_action)

from src.cli.cli import print_2_entries

# MISCELANEOUS
##############################################################################


def launch_gui(args, litoy):
    """
    used to launch the gui, called from LiTOY.py
    """
    app = QApplication(sys.argv)

    if args['darkmode']:
        # https://stackoverflow.com/questions/48256772/dark-theme-for-qt-widgets
        app.setStyle("Fusion")
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.black)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)
        app.setPalette(palette)

    win = main_window(args, litoy)
    sys.exit(app.exec_())


class Communicate(QObject):
    """
    used for communication between classes
    """
    open_browser_to_select = pyqtSignal(int)


# MAIN WINDOW AND MAIN MENU
##############################################################################


class main_window(QMainWindow):
    def __init__(self, args, litoy):
        super().__init__()
        self.initUI(args, litoy)

    def initUI(self, args, litoy):
        self.args = args
        self.litoy = litoy
        self.handler = "logs/rotating_log"
        self.orig_font_size = gui_font_size
        self.current_font_size = gui_font_size
        self.setGeometry(600, 600, 500, 300)
        self.setWindowTitle('LiTOY')
        self.statusBar().showMessage(f"Loaded database {self.args['db']}")
        self.to_mainmenu(litoy)

        menuBar = self.menuBar()

        back_to_mm = QAction("Main menu", self)
        back_to_mm.triggered.connect(lambda: self.to_mainmenu(litoy))
        back_to_mm.setShortcut("Ctrl+M")
        back_to_mm_shortcut = QShortcut(Qt.Key_Escape, self)
        back_to_mm_shortcut.activated.connect(lambda: self.to_mainmenu(litoy))
        back_to_mm_shortcut2 = QShortcut(Qt.Key_Backspace, self)
        back_to_mm_shortcut2.activated.connect(lambda: self.to_mainmenu(litoy))

        open_logs = QAction("Show logs", self)
        open_logs.triggered.connect(lambda: self.show_logs(
            self.handler, self.current_font_size, litoy))
        open_logs.setShortcut("Ctrl+L")

        quit = QAction("Exit", self)
        quit.triggered.connect(self.close)
        quit.setShortcut("Ctrl+Q")

        fontMenu = QMenu("Font", self)

        increaseFont = QAction("Increase font size", self)
        increaseFont.triggered.connect(lambda: self.change_font_size(1))
        increaseFont.setShortcut("Ctrl++")
        fontMenu.addAction(increaseFont)

        decreaseFont = QAction("Decrease font size", self)
        decreaseFont.triggered.connect(lambda: self.change_font_size(-1))
        decreaseFont.setShortcut("Ctrl+-")
        fontMenu.addAction(decreaseFont)

        sett = QAction("Settings", self)
        sett.triggered.connect(lambda: self.open_settings(litoy))
        sett.setShortcut("Ctrl+?")
        sett_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        sett_shortcut.activated.connect(lambda: self.open_settings(litoy))

        menuBar.addAction(back_to_mm)
        menuBar.addMenu(fontMenu)
        menuBar.addAction(open_logs)
        menuBar.addAction(sett)
        menuBar.addAction(quit)

        self.change_font_size(0)

    def change_font_size(self, incr):
        allW = self.findChildren(QWidget)
        self.current_font_size += incr
        new_font = QFont()
        new_font.setPointSize(self.current_font_size)
        for w in allW:
            try:
                w.setFont(new_font)
            except Exception:
                print(f"Failed to resize {w}")

    def open_settings(self, litoy):
        self.sett_window = settings_w(litoy)
        self.change_font_size(0)

    def to_mainmenu(self, litoy):
        self.mm = main_menu(litoy)
        self.setCentralWidget(self.mm)
        self.change_font_size(0)
        self.show()

    def show_logs(self, handler, fontsize, litoy):
        self.logs_window = logs_w(handler, fontsize, litoy)


class main_menu(QWidget):
    """
    central widget of the main window, with choice between review,
    add, browse, etc
    """
    def __init__(self, litoy):
        super().__init__()
        self.initUI(litoy)

    def initUI(self, litoy):
        self.litoy = litoy
        # widgets
        self.pbar = QProgressBar(self)
        self.pbar_age = 0
        self.pbar.setStyleSheet("QProgressBar {\
                                color:white;\
                                background-color: black;\
                                }\
                                QProgressBar::chunk {\
                                background:darkred;}")
        self.pbar.setValue(user_age)
        self.pbar.setMaximum(user_life_expected)
        self.pbar.setFormat("Already at %p% of your life")

        title = QLabel(self)
        title.setPixmap(QPixmap("logo.png"))
        title.setAlignment(Qt.AlignCenter)

        btn_review = QPushButton("Review")
        btn_add = QPushButton("Add")
        btn_browse = QPushButton("browse")
        btn_q = QPushButton("Quit")

        btn_review.setAutoDefault(True)
        btn_review.setShortcut("R")
        btn_add.setShortcut("A")
        btn_browse.setShortcut("S")
        btn_q.setShortcut("Q")

        btn_review.setToolTip("Start reviewing your entries")
        btn_add.setToolTip("Add new entries to LiTOY")
        btn_browse.setToolTip("browse entries")
        btn_q.setToolTip("Quit")

        btn_review.clicked.connect(self.launch_review)
        btn_add.clicked.connect(self.launch_add)
        btn_browse.clicked.connect(lambda: self.launch_browse(select=None))
        btn_q.clicked.connect(QApplication.quit)

        browser_shortcut = QShortcut("b", self)
        browser_shortcut.activated.connect(lambda: self.launch_browse(select=None))


        self.tab_podium_widget = tab_podium_widget(self.litoy)

        # layout
        vbox = QVBoxLayout()
        vbox.addWidget(title)
        vbox.addWidget(self.pbar)
        vbox.addWidget(self.tab_podium_widget)
        vbox.addStretch()
        vbox.addWidget(btn_review)
        vbox.addStretch()
        vbox.addWidget(btn_add)
        vbox.addStretch()
        vbox.addWidget(btn_browse)
        vbox.addStretch()
        vbox.addWidget(btn_q)
        vbox.addStretch()

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(vbox)
        hbox.addStretch()

        self.setLayout(hbox)
        self.show()

        self.c = Communicate()
        self.c.open_browser_to_select.connect(lambda idx: self.launch_browse(select=idx))

    def launch_review(self):
        p = self.parent()
        p.setCentralWidget(review_w(self.litoy, p))

    def launch_add(self):
        p = self.parent()
        p.setCentralWidget(add_w(self.litoy, p))

    def launch_browse(self, select=None):
        p = self.parent()
        p.setCentralWidget(browse_w(litoy=self.litoy,
                                    p=p,
                                    select=select))


class tab_podium_widget(QTabWidget):
    """
    used in the main menu to display the podium
    """
    def __init__(self, litoy):
        super().__init__()
        self.litoy = litoy
        df = self.litoy.df
        self.tab_podium = QWidget()
        self.tab_imp = QWidget()
        self.tab_quick = QWidget()
        self.addTab(self.tab_podium, "Podium")
        self.addTab(self.tab_imp, "Important")
        self.addTab(self.tab_quick, "Quick")
        self.tab_init_ui(df)

    def tab_init_ui(self, df):
        dfp = df.loc[:, ["content", "gELO", "iELO", "tELO",
                         "tags", "disabled", "metacontent"]
                     ][df["disabled"] == 0]
        dfp["media_title"] = [(lambda x: json.loads(x)["title"]
                               if "title" in json.loads(x).keys()
                               else "")(x)
                              for x in dfp.loc[:, "metacontent"]]
        dfp["tags"] = [", ".join(json.loads(x)) for x in dfp["tags"]]

        def cl_lab(t, idx):
            """ create a clickable QLabel """
            return clickable_QLabel(t, idx,
                                    whenClicked=self.open_browser)

        # podium
        cols = ["content", "gELO", "iELO", "tELO", "tags", "media_title"]
        to_show = dfp.sort_values(by="gELO", ascending=False)[0:10]
        grid = QGridLayout(self)
        for x, idx in enumerate(to_show.index):
            for y, col in enumerate(cols):
                widget = cl_lab(str(dfp.loc[idx, col]), idx)
                grid.addWidget(widget, x + 1, y)
        [grid.addWidget(QLabel(f"<b>{s}</b>"), 0, y)
         for y, s in enumerate(cols)]
        self.tab_podium.setLayout(grid)

        # important
        cols = ["content", "gELO", "iELO", "tELO", "tags", "media_title"]
        to_show = dfp.sort_values(by="iELO", ascending=False)[0:10]
        grid = QGridLayout(self)
        for x, idx in enumerate(to_show.index):
            for y, col in enumerate(cols):
                widget = cl_lab(str(dfp.loc[idx, col]), idx)
                grid.addWidget(widget, x + 1, y)
        [grid.addWidget(QLabel(f"<b>{s}</b>"), 0, y)
         for y, s in enumerate(cols)]
        self.tab_imp.setLayout(grid)

        # quick
        cols = ["content", "gELO", "iELO", "tELO", "tags", "media_title"]
        to_show = dfp.sort_values(by="tELO", ascending=False)[0:10]
        grid = QGridLayout(self)
        for x, idx in enumerate(to_show.index):
            for y, col in enumerate(cols):
                widget = cl_lab(str(dfp.loc[idx, col]), idx)
                grid.addWidget(widget, x + 1, y)
        [grid.addWidget(QLabel(f"<b>{s}</b>"), 0, y)
         for y, s in enumerate(cols)]
        self.tab_quick.setLayout(grid)
        return True

    def open_browser(self, event, idx):
        # TODO: open browser to the right entry
        # super().mm.launch_browse(select=idx)
        self.c = Communicate()
        self.c.open_browser_to_select.emit(idx)


class clickable_QLabel(QLabel):
    def __init__(self, t, idx, whenClicked):
        super().__init__(t)
        self.setWordWrap(True)
        self.idx = idx
        self._whenclicked = whenClicked

    def mouseReleaseEvent(self, event):
        self._whenclicked(event, self.idx)


# WINDOWS
##############################################################################


class settings_w(QWidget):
    def __init__(self, litoy):
        super().__init__()
        self.initUI(litoy)

    def initUI(self, litoy):
        self.litoy = litoy
        self.litoy.gui_log("Opened settings window.")
        self.sett_path = "./user_settings.py"

        self.editor = QTextEdit(self)
        self.editor.setText(Path(self.sett_path).read_text())

        self.btn_save = QPushButton("Save", self)
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.cancel_settings)
        self.btn_reset = QPushButton("Reset default", self)
        self.btn_reset.clicked.connect(self.reset_default_settings)
        self.btn_cancel.setAutoDefault(True)

        large_font = QFont()
        large_font.setPointSize(gui_font_size)
        self.editor.setFont(large_font)

        vbox = QVBoxLayout()
        vbox.addWidget(self.editor)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.btn_save)
        hbox.addWidget(self.btn_cancel)
        hbox.addWidget(self.btn_reset)
        hbox.setAlignment(Qt.AlignBottom)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.show()

    def save_settings(self):
        self.litoy.gui_log("Saving settings.")
        new_sett = self.editor.toPlainText()
        new_path = self.sett_path + ".temp"
        Path(new_path).write_text(new_sett)
        Path(self.sett_path).unlink()  # remove old file
        Path(new_path).rename(self.sett_path[2:])  # rename temp file
        QMessageBox.question(self, "Ok", "New settings will apply on next \
start.", QMessageBox.Ok, QMessageBox.Ok)
        self.close()

    def cancel_settings(self):
        self.litoy.gui_log("Didn't save settings.")
        QMessageBox.question(self, "Cancel", "Not saved.",
                             QMessageBox.Ok, QMessageBox.Ok)
        self.close()

    def reset_default_settings(self):
        self.litoy.gui_log("Resetting settings.")
        to_replace = Path(self.sett_path)
        default_file = Path("./src/backend/default_user_settings.py")
        if not default_file.exists():
            QMessageBox.question(self, "Ok", "No default settings file found!",
                                 QMessageBox.Ok, QMessageBox.Ok)
        else:
            to_replace.write_text(default_file.read_text())
            QMessageBox.question(self, "Ok", "Settings have been reset to the default \
values.", QMessageBox.Ok, QMessageBox.Ok)
        self.close()


class logs_w(QWidget):
    def __init__(self, handler, fontsize, litoy):
        super().__init__()
        self.initUI(handler, fontsize, litoy)

    def initUI(self, handler, fontsize, litoy):
        litoy.gui_log("Opened settings window.")
        self.log_file = handler
        self.current_font_size = fontsize

        self.textEd = QTextEdit(self)
        self.textEd.setReadOnly(True)
        large_font = QFont()
        large_font.setPointSize(fontsize)
        self.textEd.setFont(large_font)

        self.btn_full = QPushButton("Show full", self, checkable=True)
        self.btn_full.clicked.connect(self.show_full_logs)
        self.btn_fontp = QPushButton("Font +", self)
        self.btn_fontp.clicked.connect(lambda: self.change_font_size(1))
        self.btn_fontp.setShortcut("Ctrl++")
        self.btn_fontm = QPushButton("Font -", self)
        self.btn_fontm.clicked.connect(lambda: self.change_font_size(-1))
        self.btn_fontm.setShortcut("Ctrl+-")

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Logs:"))
        hbox.addWidget(self.btn_full)
        hbox.addWidget(self.btn_fontp)
        hbox.addWidget(self.btn_fontm)
        hbox.addStretch()
        vbox.addLayout(hbox)
        vbox.addWidget(self.textEd)
        self.setLayout(vbox)

        self.show_full_logs()
        self.show()

        scr = self.textEd.verticalScrollBar()
        scr_max = scr.maximum()
        scr.setValue(scr_max)

    def show_full_logs(self):
        if self.btn_full.isChecked() is True:
            msg = "FULL LOGS"
            nlimit = 0
        else:
            msg = "CROPPED EARLIER LOGS"
            nlimit = 1000
        with open(self.log_file) as lf:
            content = "#"*50 + "<br>" + "#"*50 + "<br>" + "#"*10 + msg + "#"*10 + "<br>"*10 + "<br>".join(lf.read().split("\n")[-nlimit:])
        self.textEd.setText(content)
        return True

    def change_font_size(self, incr):
        allW = self.findChildren(QWidget)
        self.current_font_size += incr
        new_font = QFont()
        new_font.setPointSize(self.current_font_size)
        for w in allW:
            try:
                w.setFont(new_font)
            except Exception:
                print(f"Failed to resize {w}")


class add_w(QWidget):
    def __init__(self, litoy, p):
        super().__init__()
        self.litoy = litoy
        self.litoy.gui_log("Opened adding window.")

        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:" + tags for tags in cur_tags]
        compl = QCompleter(autocomplete_list, self)
        compl.setCompletionMode(QCompleter.InlineCompletion)

        vbox = QVBoxLayout()
        self.editor = QLineEdit(self)
        self.editor.editingFinished.connect(self.process_add)
        self.editor.setCompleter(compl)
        self.logEnt = QTextEdit("Entry added:\n", self)
        self.logEnt.setReadOnly(True)

        large_font = QFont()
        large_font.setPointSize(gui_font_size)
        self.logEnt.setFont(large_font)

        vbox.addWidget(self.editor)
        vbox.addWidget(self.logEnt)
        self.setLayout(vbox)
        self.show()

    def process_add(self):
        query = self.editor.text()

        query = query.replace("tags:tags:", "tags:").strip()
        metacontent = get_meta_from_content(query)
        if not self.litoy.entry_duplicate_check(self.litoy.df,
                                                query,
                                                metacontent):
            newID = add_new_entry(self.litoy, query, metacontent)
            msg = f"ID: {newID}\ncontent: {query}\nmetacontent: \
{metacontent}\n\n"
        else:
            msg = "Database already contains this entry, not added.\n\n"
        self.litoy.gui_log(msg)
        self.logEnt.append(msg)


class review_w(QWidget):
    def __init__(self, litoy, p):
        super().__init__()
        self.litoy = litoy
        self.litoy.gui_log("Opened review window.")
        self.p = p

        self.large_font = QFont()
        self.large_font.setPointSize(gui_font_size+2)
        self.all_fields = False
        self.n_review_done = 0
        self.n_session_done = 0
        self.mode = "importance"
        self.picked_ids = pick_entries(litoy.df)

        self.entry_display = QTabWidget(self)

        self.question = QLabel("")
        self.question.setFont(self.large_font)
        ansLabel = QLabel("Answer:")
        ansLabel.setAlignment(Qt.AlignBottom)
        self.userInput = QLineEdit(self)
        self.userInput.setToolTip("Enter your commands here, type \"help\" if \
you're lost.")
        self.userInput.returnPressed.connect(self.process_answer)
        self.available_shortcut = list(chain.from_iterable(shortcuts.values()))
        compl = QCompleter(self.available_shortcut, self)
        compl.setCompletionMode(QCompleter.InlineCompletion)
        self.userInput.setCompleter(compl)

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.entry_display)
        self.vbox.addWidget(self.question)

        self.hbox.addWidget(ansLabel)
        self.hbox.addWidget(self.userInput)
        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)

        self.display_next_entries()

    def process_answer(self):
        ans = self.userInput.text()
        self.userInput.setText("")
        self.litoy.gui_log(f"Input: {ans}")

        out = shortcut_and_action(id_left=self.run[0],
                                  id_right=self.run[1],
                                  mode=self.mode,
                                  progress=None,
                                  litoy=self.litoy,
                                  shortcut_auto_completer=None,
                                  available_shortcut=None,
                                  cli=False)

        self.n_review_done += 1
        if self.n_review_done == n_to_review:
            self.n_review_done = 0
            self.n_session_done += 1
            if self.n_session_done == n_session:
                self.finished()
                return
            self.picked_ids = pick_entries(self.litoy.df)

        if self.mode == "time":
            self.mode = "importance"
        elif self.mode == "importance":
            self.mode = "time"
        self.display_next_entries()

    def finished(self):
        self.p.to_mainmenu(self.litoy)
        QMessageBox.question(self, "Finished", "Finished your reviews!",
                QMessageBox.Ok, QMessageBox.Ok)

    def display_next_entries(self):
        grid = QGridLayout(self)

        self.current_disp = []
        self.current_disp.append(self.picked_ids[0])
        if self.mode == "importance":
            self.question.setText(questions["importance"])
            self.current_disp.append(self.picked_ids[1])
        if self.mode == "time":
            self.question.setText(questions["time"])
            self.question.setText(questions["importance"])
            self.current_disp.append(self.picked_ids[2])

        self.litoy.gui_log(f"Printing entries {self.current_disp[0]} \
{self.current_disp[1]}")
        to_print = print_2_entries(self.current_disp[0], self.current_disp[1],
                                   mode=self.mode, litoy=self.litoy,
                                   all_fields=self.all_fields, cli=False)

        cols = [x[0] for x in to_print]
        for y, idx in enumerate([0] + self.current_disp):
            for x, col in enumerate(cols):
                if y == 0:
                    lab = QLabel(f"<b>{col}</b>")
                    lab.setFont(self.large_font)
                    grid.addWidget(lab, x, 0)
                else:
                    widget = QLabel(str(to_print[x][1][y - 1]))
                    widget.setWordWrap(True)
                    widget.setFont(self.large_font)
                    grid.addWidget(widget, x, y)
        grid.setColumnStretch(0, -1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        if self.n_review_done > 0:
            QWidget().setLayout(self.entry_display.layout())
        self.entry_display.setLayout(grid)
        self.show()


class browse_w(QWidget):
    def __init__(self, litoy, p, select=None):
        super().__init__()
        self.litoy = litoy
        self.df = litoy.df
        if select is not None:
            self.df = self.df.loc[select, :]
        self.litoy.gui_log("Opened browsing window.")

        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()

        lab = QLabel("Query:")
        self.allFields = QCheckBox("Only content", self, checkable=True)
        self.allFields.setChecked(True)
        self.queryIn = QLineEdit(self)

        self.queryIn.editingFinished.connect(self.process_query)
        self.allFields.stateChanged.connect(self.process_query)
        lab.setAlignment(Qt.AlignTop)
        self.queryIn.setAlignment(Qt.AlignTop)

        self.hbox.addWidget(lab)
        self.hbox.addWidget(self.queryIn)
        self.hbox.addWidget(self.allFields)

        self.vbox.addLayout(self.hbox)

        self.table = QTableView(self)
        if self.allFields.isChecked() is False:
            model = PandasModel(df=self.litoy.df.loc[:, self.litoy.df.columns],
                                litoy=self.litoy)
        else:
            model = PandasModel(df=self.litoy.df.loc[:, ["content"]],
                                litoy=self.litoy)
        self.table.setModel(model)
        self.table.resizeColumnsToContents()

        #self.color_rows(self.litoy.df)

        self.vbox.addWidget(self.table)

        self.setLayout(self.vbox)
        self.show()
        self.queryIn.setFocus()
        self.queryIn.setFocusPolicy(Qt.StrongFocus)

#    def color_rows(self, df):
#        dis = df[df["disabled"]==1].index.tolist()
#        table = self.table
#        model = table.model()
#        pp(dir(model.index()))
#        #pp(dir(table))
#        for row in range(model.rowCount(self.table.rootIndex())):
#            if row in dis:
#                pass
#                #model.itemData(row, 0).setBackground(QColor(1,1,250))
#                #print(dir(model.index(row, 0).row())) #.setBackground(QColor(1,1,1))
#                #raise SystemExit()
#                #child_index = self.table.index(row, 0, self.table.rootIndex()) # for column 0
#            #self.table.index(row, 0).setBackground(QColor(1,1,1))

    def process_query(self):
        df = self.df
        query = self.queryIn.text().lower()
        self.litoy.gui_log(f"Searched for {query}")

        match = [x
                 for x in df.index
                 if query in str(df.loc[x, "content"]).lower()
                 or query in str(df.loc[x, "metacontent"]).lower()]
        t = self.table
        if self.allFields.isChecked() is False:
            model = PandasModel(df=df.loc[match, df.columns],
                                litoy=self.litoy)
        else:
            model = PandasModel(df=df.loc[match, ["content"]],
                                litoy=self.litoy)
        t.setModel(model)

        t.resizeColumnsToContents()
        self.queryIn.setFocus()
        self.queryIn.setFocusPolicy(Qt.StrongFocus)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        add_ent = context_menu.addAction("Add new entry")
        remove_ent = context_menu.addAction("Remove entry")
        open_link = context_menu.addAction("Open media")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == add_ent:
            self.browse_add_entry()

        if action == remove_ent:
            self.browse_remove_entry()

        if action == open_link:
            select = self.table.selectionModel()
            indexes = select.selectedIndexes()
            entry_idx = []
            for index in indexes:
                displayed_row = int(index.row())
                mod = self.table.model()
                entry_idx.append(mod._df.index.tolist()[displayed_row])

                metacontent = json.loads(self.df.loc[entry_idx[-1], "metacontent"])
                self.litoy.gui_log(f"Browser: openning media of entry {entry_idx[-1]}")
                if "url" in metacontent.keys():
                    webbrowser.open(str(metacontent["url"]))
                else:
                    print(f"No link found for {entry_idx[-1]}")

    def browse_add_entry(self):
        litoy = self.litoy
        self.litoy.gui_log("Browser: adding entry")

        dialog = QInputDialog(self)
        dialog.setWindowTitle("Add entry")
        dialog.setLabelText("Content of the new entry:")
        dialog.setTextValue("")
        le = dialog.findChild(QLineEdit)
        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:" + tags for tags in cur_tags]
        compl = QCompleter(autocomplete_list, self)
        compl.setCompletionMode(QCompleter.InlineCompletion)
        le.setCompleter(compl)
        dialog.show()

        ok, entry = (
            dialog.exec_() == QDialog.Accepted,
            str(dialog.textValue()),
        )
        if ok is False:
            return False

        entry = entry.replace("tags:tags:", "tags:").strip()

        metacontent = get_meta_from_content(entry)
        if not self.litoy.entry_duplicate_check(self.litoy.df,
                                                entry,
                                                metacontent):
            newID = add_new_entry(self.litoy, entry, metacontent)
            msg = f"ID: {newID}: {entry}\n"
            title = "Added"
        else:
            msg = f"Database already contains entry '{entry}', not added.\n"
            title = "Error"

        QMessageBox.question(self, title, msg, QMessageBox.Yes,
                             QMessageBox.Yes)
        self.litoy.gui_log(msg)
        self.df = self.litoy.df
        self.process_query()
        return True

    def browse_remove_entry(self):
        self.litoy.gui_log("Browser: removing entry")

        select = self.table.selectionModel()
        indexes = select.selectedIndexes()
        entry_idx = []
        for index in indexes:
            displayed_row = int(index.row())
            mod = self.table.model()
            entry_idx.append(mod._df.index.tolist()[displayed_row])

        for entry_id in entry_idx:
            content = self.litoy.df.loc[entry_id, "content"]
            certain = QMessageBox.question(self.parent(), "Confirm removal",
                                           f"Are you sure you want to remove this entry?\n{content}",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if certain == QMessageBox.No:
                self.litoy.gui_log(f"Entry with ID {entry_id} was NOT removed.", False)
            elif certain == QMessageBox.Yes:
                self.litoy.save_to_file(self.litoy.df.drop(entry_id))
                self.litoy.gui_log(f"Entry with ID {entry_id} was removed.", False)

                msg = f"Successfuly removed entry {entry_id}"
                QMessageBox.question(self,
                        "Removed", msg, QMessageBox.Yes, QMessageBox.Yes)
                self.df = self.litoy.df
                self.process_query()
        return True
