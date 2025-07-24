import sys
import os
import re
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit,
    QSpinBox, QLabel, QGroupBox
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from GUI_module import (
    ScriptRunner, get_next_pending_title, refresh_all_next_labels,
    set_action_bar_enabled, enable_buttons, wait_for_action, send_action_input,
    run_script, on_close_event, crawl, posts, approve, send,
    crawl_figures, figure_posts, approve_figures
)
from config import get_platforms_from_config
platforms = get_platforms_from_config()

print("GUI started")

app = QApplication(sys.argv)
window = QWidget()
window.setWindowTitle("Workflow Control")
window.resize(900, 480)

btn_width = 140

# ---- Top Workflow Controls (Article Row) ----
label_articles = QLabel("Articles")
label_articles.setStyleSheet("font-weight: bold; margin-right: 8px;")
label_articles.setFixedWidth(60)

btn_crawl = QPushButton("Crawl")
btn_crawl.setFixedWidth(btn_width)

btn_posts = QPushButton("Generate Posts")
btn_posts.setFixedWidth(btn_width)

spin_posts = QSpinBox()
spin_posts.setMinimum(1)
spin_posts.setMaximum(20)
spin_posts.setValue(1)
spin_posts.setFixedWidth(60)

btn_approve = QPushButton("Approve")
btn_approve.setFixedWidth(btn_width)

top_bar = QHBoxLayout()
top_bar.setSpacing(8)
top_bar.setContentsMargins(10, 10, 10, 2)
top_bar.addWidget(label_articles)
top_bar.addWidget(btn_crawl)
top_bar.addWidget(btn_posts)
top_bar.addWidget(QLabel("How many:"))
top_bar.addWidget(spin_posts)
top_bar.addWidget(btn_approve)
top_bar.addStretch()

# ---- Top Workflow Controls (Figure Row) ----
label_figures = QLabel("Figures")
label_figures.setStyleSheet("font-weight: bold; margin-right: 8px;")
label_figures.setFixedWidth(60)

btn_crawl_figures = QPushButton("Crawl Fig.")
btn_crawl_figures.setFixedWidth(btn_width)

btn_fig_posts = QPushButton("Generate Fig. Posts")
btn_fig_posts.setFixedWidth(btn_width)

spin_fig_posts = QSpinBox()
spin_fig_posts.setMinimum(1)
spin_fig_posts.setMaximum(3)
spin_fig_posts.setValue(1)
spin_fig_posts.setFixedWidth(60)

btn_fig_approve = QPushButton("Approve Fig.")
btn_fig_approve.setFixedWidth(btn_width)

fig_top_bar = QHBoxLayout()
fig_top_bar.setSpacing(8)
fig_top_bar.setContentsMargins(10, 2, 10, 10)
fig_top_bar.addWidget(label_figures)
fig_top_bar.addWidget(btn_crawl_figures)
fig_top_bar.addWidget(btn_fig_posts)
fig_top_bar.addWidget(QLabel("How many:"))
fig_top_bar.addWidget(spin_fig_posts)
fig_top_bar.addWidget(btn_fig_approve)
fig_top_bar.addStretch()

# ---- Combine Both Rows in Workflow Actions ----
workflow_vbox = QVBoxLayout()
workflow_vbox.addLayout(top_bar)
workflow_vbox.addLayout(fig_top_bar)

workflow_box = QGroupBox("Workflow Actions")
workflow_box.setLayout(workflow_vbox)
workflow_box.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #aac; margin-top: 12px; }")

# ---- Social Media Send Buttons & "Next" Labels ----
PLATFORMS = get_platforms_from_config()
send_buttons = {}
next_labels = {}

v_send_layout = QVBoxLayout()
for platform in platforms:
    h_send_layout = QHBoxLayout()
    btn = QPushButton(f"Send ({platform.capitalize()})")
    btn.setFixedWidth(btn_width)
    h_send_layout.addWidget(btn)
    label = QLabel("Next: (none)")
    label.setStyleSheet("color: #335; font-weight: bold; margin-left: 8px;")
    h_send_layout.addWidget(label)
    v_send_layout.addLayout(h_send_layout)
    send_buttons[platform] = btn
    next_labels[platform] = label

send_box = QGroupBox("Send to Social Platforms")
send_box.setLayout(v_send_layout)
send_box.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #6cf; margin-top: 12px; }")

# ---- Output Area ----
textedit = QTextEdit()
textedit.setPlaceholderText("Output will appear here")
textedit.setFixedHeight(270)
textedit.setReadOnly(True)
textedit.setStyleSheet("background: #fafcff; font-family: monospace; font-size: 13px;")

output_box = QGroupBox("Output Log")
output_layout = QVBoxLayout()
output_layout.setContentsMargins(8, 18, 8, 8)  # Nice spacing below title
output_layout.addWidget(textedit)
output_box.setLayout(output_layout)
output_box.setStyleSheet("QGroupBox { font-weight: bold; border: 1px solid #ccc; margin-top: 12px; }")

# ---- Inline Image Preview ----
image_label = QLabel()
image_label.setFixedSize(400, 250)
image_label.setAlignment(Qt.AlignCenter)
image_label.setStyleSheet("border: 1px solid #aaa; background: #fff; margin-top: 8px;")
image_label.setText("(Image preview)")

def update_image_label_from_output(line):
    m = re.match(r"Image:\s*(\S+)", line)
    if m:
        url = m.group(1)
        pixmap = QPixmap()
        if url.startswith("http"):
            try:
                resp = requests.get(url, timeout=8)
                if resp.status_code == 200:
                    pixmap.loadFromData(resp.content)
            except Exception as e:
                image_label.setText("(Error loading image from web)")
                return
        elif os.path.exists(url):
            pixmap.load(url)
        if not pixmap.isNull():
            image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            image_label.setText("")
        else:
            image_label.setPixmap(QPixmap())
            image_label.setText("(Image not found)")
    # If "Approve, Deny, Skip..." line or another line, do not clear—keep previous image

# ---- Action Bar (Approve/Deny/Skip/Quit) ----
action_bar = QHBoxLayout()
btn_action_approve = QPushButton("Approve")
btn_action_deny = QPushButton("Deny")
btn_action_skip = QPushButton("Skip")
btn_action_quit = QPushButton("Quit")
for b in [btn_action_approve, btn_action_deny, btn_action_skip, btn_action_quit]:
    b.setFixedWidth(110)
    action_bar.addWidget(b)

# ----------- ACTION BAR WRAPPER FIX -----------
def set_action_bar(enabled, *args):
    set_action_bar_enabled(enabled, btn_action_approve, btn_action_deny, btn_action_skip, btn_action_quit)

set_action_bar(False)  # Start disabled

label_waiting = QLabel("")
label_waiting.setStyleSheet("color: #666; margin-top: 4px; margin-bottom: 4px;")

# ---- Layout All ----
v_layout = QVBoxLayout()
v_layout.addWidget(workflow_box)
v_layout.addWidget(send_box)
v_layout.addWidget(output_box)
v_layout.addWidget(image_label)         # <<--- Added here!
v_layout.addWidget(label_waiting)
v_layout.addLayout(action_bar)
window.setLayout(v_layout)

# ---- Refresh labels for all platforms ----
def do_refresh_all_next_labels():
    refresh_all_next_labels(platforms, next_labels)
do_refresh_all_next_labels()

# ---- Thread-safe runner management ----
runner_ref = {'runner': None, 'action_bar_btns': [btn_action_approve, btn_action_deny, btn_action_skip, btn_action_quit]}

def enable_buttons_wrapper():
    enable_buttons(btn_crawl, btn_posts, btn_approve, send_buttons)

def run_script_wrapper(command):
    run_script(
        command,
        runner_ref,
        textedit,
        enable_buttons_wrapper,
        set_action_bar,  # The fixed wrapper!
        label_waiting,
        do_refresh_all_next_labels,
        output_handler=handle_output  # Pass custom handler
    )

# --- Custom output handler: show image preview if line contains "Image: ..."
def handle_output(s):
    textedit.append(s.rstrip())
    update_image_label_from_output(s.rstrip())

# --- Articles row connects
btn_crawl.clicked.connect(lambda: crawl(run_script_wrapper))
btn_posts.clicked.connect(lambda: posts(run_script_wrapper, spin_posts))
btn_approve.clicked.connect(lambda: approve(run_script_wrapper))
# --- Figures row connects
btn_crawl_figures.clicked.connect(lambda: crawl_figures(run_script_wrapper))
btn_fig_posts.clicked.connect(lambda: figure_posts(run_script_wrapper, spin_fig_posts))
btn_fig_approve.clicked.connect(lambda: approve_figures(run_script_wrapper))
# --- Social send connects
for platform, btn in send_buttons.items():
    btn.clicked.connect(lambda _, p=platform: send(run_script_wrapper, p))
# --- Action bar connects
btn_action_approve.clicked.connect(lambda: send_action_input('a', runner_ref['runner'], set_action_bar, runner_ref['action_bar_btns'], label_waiting))
btn_action_deny.clicked.connect(lambda: send_action_input('d', runner_ref['runner'], set_action_bar, runner_ref['action_bar_btns'], label_waiting))
btn_action_skip.clicked.connect(lambda: send_action_input('s', runner_ref['runner'], set_action_bar, runner_ref['action_bar_btns'], label_waiting))
btn_action_quit.clicked.connect(lambda: send_action_input('q', runner_ref['runner'], set_action_bar, runner_ref['action_bar_btns'], label_waiting))

# ---- Clean up thread on window close ----
window.closeEvent = lambda event: on_close_event(event, runner_ref)

window.show()
app.exec_()
