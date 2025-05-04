import tkinter as tk
import sys
import threading
import atexit
import time

class LogStream:
    def __init__(self, log_widget, buffer_size=1000, file=None, flush_interval=2.0):
        self.log_widget = log_widget
        self.buffer_size = buffer_size
        self.buffer = []
        self.file = file
        self.original_stdout = sys.__stdout__
        self.lock = threading.Lock()
        self.running = True
        self._flush_interval = flush_interval
        self._flush_event = threading.Event()

        # Start periodic flushing
        self._flush_thread = threading.Thread(target=self._auto_flush, daemon=True)
        self._flush_thread.start()

        # Ensure final flush at exit
        atexit.register(self._final_flush_and_wait)

    def write(self, message):
        with self.lock:
            self.buffer.append(message)

        self.original_stdout.write(message)
        self.original_stdout.flush()

        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        with self.lock:
            combined = ''.join(self.buffer)
            self.buffer.clear()

        if combined:
            # GUI output (only if GUI still exists)
            if self.log_widget:
                try:
                    self.log_widget.after(0, self._write_to_widget, combined)
                except Exception:
                    pass

            # File output
            if self.file:
                try:
                    with open(self.file, 'a') as f:
                        f.write(combined)
                except Exception as e:
                    self.original_stdout.write(f"[LogStream Error] Could not write to file: {e}\n")

    def _write_to_widget(self, text):
        try:
            if self.log_widget and self.log_widget.winfo_exists():
                self.log_widget.config(state='normal')
                self.log_widget.insert(tk.END, text)
                self.log_widget.yview(tk.END)
                self.log_widget.config(state='disabled')
        except tk.TclError:
            pass  # GUI is gone

    def _auto_flush(self):
        while self.running:
            self.flush()
            time.sleep(self._flush_interval)

    def _final_flush_and_wait(self):
        self.running = False
        self.flush()
        time.sleep(0.1)  # Give time for final async flush to GUI/file

    def __del__(self):
        self._final_flush_and_wait()
