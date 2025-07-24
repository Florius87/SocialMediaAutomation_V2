import csv
from tracker import TRACKER_FILE
from webparsing import extract_page_data
from PyQt5.QtCore import QThread, pyqtSignal

class ScriptRunner(QThread):
    output_signal = pyqtSignal(str)
    input_request_signal = pyqtSignal()
    finished_signal = pyqtSignal()

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None
        self.waiting_for_input = False

    def run(self):
        import subprocess
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                stdin=subprocess.PIPE,
                bufsize=1,
                universal_newlines=True,
                encoding="utf-8"
            )
            while True:
                line = self.process.stdout.readline()
                if not line:
                    break
                self.output_signal.emit(line)
                if "Approve, Deny, Skip, or Quit? [a/d/s/q]:" in line:
                    self.waiting_for_input = True
                    self.input_request_signal.emit()
                    while self.waiting_for_input:
                        self.msleep(100)
            self.process.stdout.close()
            self.process.wait()
        except Exception as e:
            self.output_signal.emit(f"Error: {e}\n")
        self.finished_signal.emit()

    def send_input(self, text):
        if self.process and self.process.stdin:
            self.process.stdin.write(text + '\n')
            self.process.stdin.flush()
        self.waiting_for_input = False

def get_next_pending_title(platform="twitter"):
    try:
        with open(TRACKER_FILE, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        for row in reversed(rows):
            approved = row.get(f"{platform}_approved", "").strip().upper() == "TRUE"
            uploaded = row.get(f"{platform}_uploaded", "").strip().upper() == "TRUE"
            if approved and not uploaded:
                url = row.get("url", "")
                if url:
                    data = extract_page_data(url)
                    return data.get("title", "(none)") or "(none)"
        return "(none)"
    except Exception as e:
        print(f"Error fetching next pending title: {e}")
        return "(none)"

def refresh_all_next_labels(platforms, next_labels):
    for platform in platforms:
        title = get_next_pending_title(platform)
        next_labels[platform].setText(f"Next: {title}")

def set_action_bar_enabled(enabled, btn_action_approve, btn_action_deny, btn_action_skip, btn_action_quit):
    btn_action_approve.setEnabled(enabled)
    btn_action_deny.setEnabled(enabled)
    btn_action_skip.setEnabled(enabled)
    btn_action_quit.setEnabled(enabled)

def enable_buttons(btn_crawl, btn_posts, btn_approve, send_buttons):
    btn_crawl.setEnabled(True)
    btn_posts.setEnabled(True)
    btn_approve.setEnabled(True)
    for btn in send_buttons.values():
        btn.setEnabled(True)

def wait_for_action(set_action_bar_enabled_func, btns, label_waiting):
    set_action_bar_enabled_func(True, *btns)
    label_waiting.setText("Waiting for your action...")

def send_action_input(letter, runner, set_action_bar_enabled_func, btns, label_waiting):
    if runner and runner.isRunning():
        runner.send_input(letter)
    set_action_bar_enabled_func(False, *btns)
    label_waiting.setText("")

def run_script(command, runner_ref, textedit, enable_buttons_func, set_action_bar_enabled_func, label_waiting, refresh_labels_func, output_handler=None):
    runner = runner_ref['runner']
    if runner is not None and runner.isRunning():
        runner.terminate()
        runner.wait()
    runner = ScriptRunner(command)
    runner_ref['runner'] = runner
    if output_handler:
        runner.output_signal.connect(output_handler)
    else:
        runner.output_signal.connect(lambda s: textedit.append(s.rstrip()))
    runner.finished_signal.connect(lambda: [enable_buttons_func(), set_action_bar_enabled_func(False, *runner_ref['action_bar_btns']), label_waiting.setText(""), refresh_labels_func()])
    runner.input_request_signal.connect(lambda: wait_for_action(set_action_bar_enabled_func, runner_ref['action_bar_btns'], label_waiting))
    set_action_bar_enabled_func(False, *runner_ref['action_bar_btns'])
    enable_buttons_func()
    textedit.clear()
    runner.start()

def on_close_event(event, runner_ref):
    runner = runner_ref['runner']
    if runner is not None and runner.isRunning():
        runner.terminate()
        runner.wait()
    event.accept()

def crawl(run_script_func):
    run_script_func(['python', 'crawler.py'])

def posts(run_script_func, spin_posts):
    count = spin_posts.value()
    run_script_func(['python', 'main.py', str(count)])

def approve(run_script_func):
    run_script_func(['python', 'Approve.py'])

def send(run_script_func, platform="twitter"):
    run_script_func(['python', 'send.py', platform])

# ---- Figure row helpers (plug in your FigureParsing.py etc) ----
def crawl_figures(run_script_func):
    run_script_func(['python', 'FigureParsing.py'])

def figure_posts(run_script_func, spin_posts):
    count = spin_posts.value()
    run_script_func(['python', 'figure_prep.py', str(count)])

def approve_figures(run_script_func):
    run_script_func(['python', 'FigureApprove.py'])
