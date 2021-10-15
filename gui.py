#!/usr/bin/env python3.9


from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import json

import sys
from user_settings import user_age, user_life_expected
from PandasModel import PandasModel
import prompt_toolkit
from LiTOY import get_meta_from_content, add_new_entry
import logging
from pprint import pprint as pp

class Communicate(QObject):
    sig = pyqtSignal()

class main_window(QMainWindow):
    def __init__(self, args, litoy):
        super().__init__()
        self.initUI(args, litoy)

    def initUI(self, args, litoy):
        self.args = args
        self.litoy = litoy
        self.handler = litoy.handler
        self.setGeometry(600, 600, 500, 300)
        self.setWindowTitle('LiTOY')
        self.statusBar().showMessage(f"Loaded database {self.args['db']}")
        self.to_mainmenu(litoy)

        menuBar = self.menuBar()

        back_to_mm = QAction("Main menu", self)
        back_to_mm.triggered.connect(lambda : self.to_mainmenu(litoy))
        back_to_mm.setShortcut(Qt.Key_Escape)
        back_to_mm.setShortcut(Qt.Key_Backspace)
        back_to_mm.setShortcut("Ctrl+m")

        quit = QAction("Exit", self)
        quit.triggered.connect(self.close)
        quit.setShortcut("Ctrl+Q")

        menuBar.addAction(back_to_mm)
        menuBar.addAction(quit)


    def to_mainmenu(self, litoy):
        self.mm = main_menu(litoy)
        self.setCentralWidget(self.mm)
        self.show()


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
        btn_log    = QPushButton("Logs")

        btn_review.setAutoDefault(True)
        btn_review.setShortcut("R")
        btn_add.setShortcut("A")
        btn_browse.setShortcut("B")
        btn_browse.setShortcut("S")
        btn_q.setShortcut("Q")
        btn_log.setShortcut("L")

        btn_review.setToolTip("Start reviewing your entries")
        btn_add.setToolTip("Add new entries to LiTOY")
        btn_browse.setToolTip("browse entries")
        btn_q.setToolTip("Quit")
        btn_log.setToolTip("Show logs")

        btn_review.clicked.connect(self.launch_review)
        btn_add.clicked.connect(self.launch_add)
        btn_browse.clicked.connect(self.launch_browse)
        btn_q.clicked.connect(QApplication.quit)
        btn_log.clicked.connect(self.show_logs)

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
        vbox.addWidget(btn_log)

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

    def show_logs(self):
        p = self.parent()
        log_file = str(p.handler).split(" ")[1]
        with open(log_file) as lf:
            #content = lf.read().replace("\n", "<br>").split("")[-1000:]
            content = "<br>".join(lf.read().split("\n")[-1000:])
        content = "#"*50 + "<br>" + "#"*50 + "<br>" + "#"*10 + "CROPPED EARLIER MESSAGES" + "#"*10 + "<br>"*10 + content
        textEd = QTextEdit(content)
        textEd.setReadOnly(True)

        scr = textEd.verticalScrollBar()
        scr_max = scr.maximum()
        scr.setValue(scr_max)

        large_font = QFont()
        large_font.setPointSize(18)
        textEd.setFont(large_font)

        p.setCentralWidget(textEd)


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
        large_font.setPointSize(18)
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
        self.df = litoy.df
        self.litoy.gui_log(f"Opened review window.")

        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        ansLabel = QLabel("Input:")
        ansLabel.setAlignment(Qt.AlignBottom)
        self.userInput = QLineEdit(self)
        self.userInput.setToolTip("Enter your commands here, type \"help\" if \
you're lost.")
        self.vbox.addWidget(ansLabel)
        self.vbox.addWidget(self.userInput)

        self.vbox.addLayout(self.hbox)
        self.setLayout(self.vbox)
        self.show()

    def process_answer(self, ans):
        print(dir(self))
        pass


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
        for index in indexes:
            displayed_row = int(index.row())
            mod = self.table.model()
            entry_id = mod._df.index.tolist()[displayed_row]

        content = self.litoy.df.loc[entry_id, "content"]
        certain = QMessageBox.question(self.parent(), "Confirm removal",
                    "Are you sure you want to remove this entry?\n{content}",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if certain == QMessageBox.No:
            self.litoy.gui_log(f"Entry with ID {entry_id} was NOT removed.", False)
            return False
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
