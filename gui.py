#!/usr/bin/env python3.9


from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QLabel, QPushButton, QWidget, QHBoxLayout
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys
from user_settings import user_age, user_life_expected
from PandasModel import PandasModel
import prompt_toolkit
from LiTOY import get_meta_from_content, add_new_entry
import logging
from pprint import pprint

class Communicate(QObject):
    sig = pyqtSignal()

class main_window(QMainWindow):
    def __init__(self, args, litoy, handler):
        super().__init__()
        self.initUI(args, litoy, handler)

    def initUI(self, args, litoy, handler):
        self.args = args
        self.litoy = litoy
        self.handler = handler
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


        # layout
        vbox = QVBoxLayout()
        vbox.addWidget(title)
        vbox.addWidget(self.pbar)
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
            model = PandasModel(df.loc[match, df.columns], self.litoy)
        else:
            model = PandasModel(df.loc[match, ["content"]], self.litoy)
        t.setModel(model)
        t.resizeColumnsToContents()
        self.queryIn.setFocus()
        self.queryIn.setFocusPolicy(Qt.StrongFocus)


def launch_gui(args, litoy, handler):
    app = QApplication(sys.argv)
    win = main_window(args, litoy, handler)
    sys.exit(app.exec_())

if __name__ == '__main__':
    launch_gui(sys.argv)
