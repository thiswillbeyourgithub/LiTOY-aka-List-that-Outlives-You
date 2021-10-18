#!/usr/bin/env python3.9

import json
from itertools import chain
import sys
from pathlib import Path


from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout, QAction, QMenu, QProgressBar, QMessageBox, QTabWidget, QGridLayout, QLineEdit, QCheckBox, QTableView, QTextEdit, QCompleter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPalette, QFont, QPixmap

from user_settings import user_age, user_life_expected, shortcuts, n_session, n_to_review, questions, gui_font_size
from PandasModel import PandasModel
from LiTOY import get_meta_from_content, add_new_entry, pick_entries
from pprint import pprint as pp

class main_window(QMainWindow):
    def __init__(self, args, litoy):
        super().__init__()
        self.initUI(args, litoy)

    def initUI(self, args, litoy):
        self.args = args
        self.litoy = litoy
        self.handler = litoy.handler
        self.orig_font_size = gui_font_size
        self.current_font_size = gui_font_size
        self.setGeometry(600, 600, 500, 300)
        self.setWindowTitle('LiTOY')
        self.statusBar().showMessage(f"Loaded database {self.args['db']}")
        self.to_mainmenu(litoy)

        menuBar = self.menuBar()

        back_to_mm = QAction("Main menu", self)
        back_to_mm.triggered.connect(lambda : self.to_mainmenu(litoy))
        back_to_mm.setShortcut("Ctrl+M")

        open_logs = QAction("Show logs", self)
        open_logs.triggered.connect(lambda : self.show_logs(litoy.handler, self.current_font_size, litoy))
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
        sett.triggered.connect(lambda : self.open_settings(litoy))
        sett.setShortcut("Ctrl+?")

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
                except:
                    print(f"Failed to resize {w}")

    def keyPressEvent(self, event):
        "to handle multiple shortcuts for the same action"
        if event.key() in [Qt.Key_Escape, Qt.Key_Backspace]:
            self.to_mainmenu(self.litoy)
        if event.text() == "b":
            self.mm.launch_browse()


    def open_settings(self, litoy):
        self.sett_window = settings_w(litoy)
        self.change_font_size(0)

    def to_mainmenu(self, litoy):
        self.mm = main_menu(litoy)
        self.setCentralWidget(self.mm)
        self.show()

    def show_logs(self, handler, fontsize, litoy):
        self.logs_window = logs_w(handler, fontsize, litoy)

class settings_w(QWidget):
    def __init__(self, litoy):
        super().__init__()
        self.initUI(litoy)

    def initUI(self, litoy):
        litoy.gui_log(f"Opened settings window.")
        sett_file = Path("./user_settings.py")
        with open(sett_file) as lf:
            content = lf.read()
        self.editor = QTextEdit(self)
        self.editor.setText(content)

        self.btn_save = QPushButton("Save", self)
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.clicked.connect(self.cancel_settings)

        large_font = QFont()
        large_font.setPointSize(gui_font_size)
        self.editor.setFont(large_font)

        vbox = QVBoxLayout()
        vbox.addWidget(self.editor)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.btn_save)
        hbox.addWidget(self.btn_cancel)
        hbox.setAlignment(Qt.AlignBottom)
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        self.show()

    def save_settings(self):
        pass

    def cancel_settings(self):
        confirmation = QMessageBox.question(self,
                "Cancel", "Not saved.", QMessageBox.Ok, QMessageBox.Ok)
        self.close()

class logs_w(QWidget):
    def __init__(self, handler, fontsize, litoy):
        super().__init__()
        self.initUI(handler, fontsize, litoy)

    def initUI(self, handler, fontsize, litoy):
        litoy.gui_log(f"Opened settings window.")
        self.log_file = str(handler).split(" ")[1]
        self.current_font_size = fontsize

        self.textEd = QTextEdit(self)
        self.textEd.setReadOnly(True)
        large_font = QFont()
        large_font.setPointSize(fontsize)
        self.textEd.setFont(large_font)

        self.btn_full = QPushButton("Show full", self, checkable=True)
        self.btn_full.clicked.connect(self.show_full_logs)
        self.btn_fontp = QPushButton("Font +", self)
        self.btn_fontp.clicked.connect(lambda : self.change_font_size(1))
        self.btn_fontp.setShortcut("Ctrl++")
        self.btn_fontm = QPushButton("Font -", self)
        self.btn_fontm.clicked.connect(lambda : self.change_font_size(-1))
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
                except:
                    print(f"Failed to resize {w}")

class main_menu(QWidget):
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
        btn_add    = QPushButton("Add")
        btn_browse = QPushButton("browse")
        btn_q      = QPushButton("Quit")

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
        btn_browse.clicked.connect(self.launch_browse)
        btn_q.clicked.connect(QApplication.quit)

        self.tab_widget = tab_widget(self.litoy)

        # layout
        vbox = QVBoxLayout()
        vbox.addWidget(title)
        vbox.addWidget(self.pbar)
        vbox.addWidget(self.tab_widget)
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

    def launch_review(self):
        p = self.parent()
        p.setCentralWidget(review_w(self.litoy, p))

    def launch_add(self):
        p = self.parent()
        p.setCentralWidget(add_w(self.litoy, p))

    def launch_browse(self):
        p = self.parent()
        p.setCentralWidget(browse_w(self.litoy, p))


class tab_widget(QTabWidget):
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

      # podium
      cols = ["content", "gELO", "iELO", "tELO", "tags", "media_title"]
      to_show = dfp.sort_values(by="gELO", ascending=False)[0:10]
      grid = QGridLayout(self)
      for x, idx in enumerate(to_show.index):
          for y, col in enumerate(cols):
              widget = QLabel(str(dfp.loc[idx, col]))
              grid.addWidget(widget, x+1, y)
      [grid.addWidget(QLabel(f"<b>{s}</b>"), 0, y) for y, s in enumerate(cols)]
      self.tab_podium.setLayout(grid)

      # important
      cols = ["content", "gELO", "iELO", "tELO", "tags", "media_title"]
      to_show = dfp.sort_values(by="iELO", ascending=False)[0:10]
      grid = QGridLayout(self)
      for x, idx in enumerate(to_show.index):
          for y, col in enumerate(cols):
              widget = QLabel(str(dfp.loc[idx, col]))
              grid.addWidget(widget, x+1, y)
      [grid.addWidget(QLabel(f"<b>{s}</b>"), 0, y) for y, s in enumerate(cols)]
      self.tab_imp.setLayout(grid)

      # quick
      cols = ["content", "gELO", "iELO", "tELO", "tags", "media_title"]
      to_show = dfp.sort_values(by="iELO", ascending=False)[0:10]
      grid = QGridLayout(self)
      for x, idx in enumerate(to_show.index):
          for y, col in enumerate(cols):
              widget = QLabel(str(dfp.loc[idx, col]))
              grid.addWidget(widget, x+1, y)
      [grid.addWidget(QLabel(f"<b>{s}</b>"), 0, y) for y, s in enumerate(cols)]
      self.tab_quick.setLayout(grid)
      return True


class add_w(QWidget):
    def __init__(self, litoy, p):
        super().__init__()
        self.litoy = litoy
        self.litoy.gui_log(f"Opened adding window.")

        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:"+tags for tags in cur_tags]
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
        metacontent = get_meta_from_content(query, gui_log = self.litoy.gui_log)
        if not self.litoy.entry_duplicate_check(self.litoy.df,
                                           query,
                                           metacontent):
            newID = add_new_entry(self.litoy.df, query, metacontent, self.litoy, self.litoy.gui_log)
            msg = f"ID: {newID}: {query}\n"
        else:
            msg = "Database already contains this entry, not added.\n"
        self.litoy.gui_log(msg)
        self.logEnt.append(msg)


class review_w(QWidget):
    def __init__(self, litoy, p):
        super().__init__()
        self.litoy = litoy
        df = litoy.df
        self.litoy.gui_log(f"Opened review window.")

        self.large_font = QFont()
        self.large_font.setPointSize(18)
        self.n_review_done = 0
        self.n_session_done = 0
        self.mode = "importance"
        self.picked_ids = pick_entries(litoy)

        self.entry_display = QTabWidget(self)

        self.question = QLabel("")
        self.question.setFont(self.large_font)
        ansLabel = QLabel("Answer:")
        ansLabel.setAlignment(Qt.AlignBottom)
        self.userInput = QLineEdit(self)
        self.userInput.setToolTip("Enter your commands here, type \"help\" if \
you're lost.")
        available_shortcut = list(chain.from_iterable(shortcuts.values()))
        compl = QCompleter(available_shortcut, self)
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
        self.show()

    def process_answer(self, ans):
        #TODO
        self.n_review_done += 1
        if self.n_review_done == n_to_review:
            self.n_review_done = 0
            self.n_session_done += 1
            if self.n_session_done == n_session:
                self.finished()
            else:
                self.picked_ids = pick_entries(self.litoy)
        if self.mode == "time":
            self.mode = "importance"
        elif self.mode == "importance":
            self.mode = "time"
        self.display_next_entries()

    def finished(self):
        grid = QGridLayout(self)
        grid.addWidget(QLabel("Finished!"), 0, 0)
        self.entry_display.setLayout(grid)

    def display_next_entries(self):
        grid = QGridLayout(self)
        cols = ["ID", "tags", "starred", "content", "iELO", "tELO", "K"]
        self.run = []
        self.run.append(self.picked_ids[0])
        if self.mode == "importance":
            self.question.setText(questions["importance"])
            self.run.append(self.picked_ids[1])
        if self.mode == "time":
            self.question.setText(questions["time"])
            self.question.setText(questions["importance"])
            self.run.append(self.picked_ids[2])
        self.run
        for y, idx in enumerate([0] + self.run):
            for x, col in enumerate(cols):
                if y == 0:
                    l = QLabel(f"<b>{col}</b>")
                    l.setFont(self.large_font)
                    grid.addWidget(l, x, 0)
                else:
                    widget = QLabel(str(self.litoy.df.reset_index().loc[idx, col]))
                    widget.setWordWrap(True)
                    widget.setFont(self.large_font)
                    grid.addWidget(widget, x, y)
        grid.setColumnStretch(0, -1)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 1)
        self.entry_display.setLayout(grid)


class browse_w(QWidget):
    def __init__(self, litoy, p):
        super().__init__()
        self.litoy = litoy
        self.df = litoy.df
        self.litoy.gui_log(f"Opened browsing window.")

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
            model = PandasModel(df=self.litoy.df.loc[:, self.litoy.df.columns], litoy=self.litoy)
        else:
            model = PandasModel(df=self.litoy.df.loc[:, ["content"]], litoy=self.litoy)
        self.table.setModel(model)
        self.table.resizeColumnsToContents()

        self.vbox.addWidget(self.table)

        self.setLayout(self.vbox)
        self.show()
        self.queryIn.setFocus()
        self.queryIn.setFocusPolicy(Qt.StrongFocus)

    def process_query(self):
        df = self.df
        query = self.queryIn.text().lower()
        self.litoy.gui_log(f"Searched for {query}")

        match = [x for x in df.index if query in str(df.loc[x, "content"]).lower()
                or query in str(df.loc[x, "metacontent"]).lower()]
        t = self.table
        if self.allFields.isChecked() is False:
            model = PandasModel(df=df.loc[match, df.columns], litoy=self.litoy)
        else:
            model = PandasModel(df=df.loc[match, ["content"]], litoy=self.litoy)
        t.setModel(model)

        t.resizeColumnsToContents()
        self.queryIn.setFocus()
        self.queryIn.setFocusPolicy(Qt.StrongFocus)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        add_ent = context_menu.addAction("Add new entry")
        remove_ent = context_menu.addAction("Remove entry")
        action = context_menu.exec_(self.mapToGlobal(event.pos()))
        if action == add_ent:
            self.browse_add_entry()

        if action == remove_ent:
            self.browse_remove_entry()

    def browse_add_entry(self):
        litoy = self.litoy
        self.litoy.gui_log(f"Browser: adding entry")

        dialog = QInputDialog(self)
        dialog.setWindowTitle("Add entry")
        dialog.setLabelText("Content of the new entry:")
        dialog.setTextValue("")
        le = dialog.findChild(QLineEdit)
        cur_tags = litoy.get_tags(litoy.df)
        autocomplete_list = ["tags:"+tags for tags in cur_tags]
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

        metacontent = get_meta_from_content(entry, gui_log = self.litoy.gui_log)
        if not self.litoy.entry_duplicate_check(self.litoy.df,
                                           entry,
                                           metacontent):
            newID = add_new_entry(self.litoy.df, entry, metacontent, self.litoy, self.litoy.gui_log)
            msg = f"ID: {newID}: {entry}\n"
            title = "Added"
        else:
            msg = f"Database already contains entry '{entry}', not added.\n"
            title = "Error"

        confirmation = QMessageBox.question(self,
                title, msg, QMessageBox.Yes, QMessageBox.Yes)
        self.litoy.gui_log(msg)
        self.df = self.litoy.df
        self.process_query()
        return True

    def browse_remove_entry(self):
        self.litoy.gui_log(f"Browser: removing entry")

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
                confirmation = QMessageBox.question(self,
                        "Removed", msg, QMessageBox.Yes, QMessageBox.Yes)
                self.df = self.litoy.df
                self.process_query()
        return True

def launch_gui(args, litoy):
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

if __name__ == '__main__':
    launch_gui(sys.argv)
