import re
import sys, shutil
from typing import Optional


import argplusplus.console.color as clr
from argplusplus.console.input.keys import KeyReader
from argplusplus.console.input.progress_bar import ProgressBar
from argplusplus.console.input.spinner import Spinner
from argplusplus.console.types.widgets import SpinnerType

class OutputConsole:
    def __init__(self) -> None:
        self.stdout = sys.stdout
        self.stdin = sys.stdin
        self.raw = KeyReader(self.stdin, self.stdout)
        self.nl = "\n"
        self._input_history: list[str] = []
        self._lines_made = 0
        self._sticky_line: str | None = None
    @property
    def size(self) -> tuple[int, int]:
        sz= shutil.get_terminal_size()
        return (sz.lines, sz.columns)


    def checkbox(self, options: list[str] | dict[str, bool], prompt: str = "Please choose an option", multiple: bool = False) -> list | None:
        def _check(state: bool):
            if state:
                return "[green][X][/green]"
            return "[red][O][/red]"
        states: dict[str, bool] = options if isinstance(options, dict) else {s: False for s in options}
        cursor: int = 0
        
        def _get(ind: int) -> str:
            return list(states.keys())[ind]
        def _render(lines_count: int):
            self.move_cursor(lines=-(lines_count))
            for i in range(lines_count):
                self.clear_line()
                if i == 0:
                    self.raw_print("\r" + prompt + "\n", flush=False)
                else:
                    opt = _get(i-1)
                    val = states[opt]
                    if cursor == (i-1):
                        self.raw_print("\033[1m")
                    content = self.format(f"  - {opt}: {_check(val)}")
                    self.raw_print("\r" + content, flush=False)
                    if cursor == (i-1):
                        self.raw_print("\033[0m")
                    self.newline()
                
            if cursor == lines_count-1:
                self.pprint("\r[bold][Enter][/bold]",end="")
            else:
                self.pprint("\r[Enter]",end="")
            self.flush()
        self.hide_cursor()
        try:
            with self.raw:
                lines_count = len(states) + 1
                self.print(prompt)
                for opt, val in states.items():
                    self.print(f"{opt}: {_check(val)}")
                _render(lines_count)
                for key in self.raw:
                    if key == '\x1b[A':  # Left arrow
                        if cursor > 0:
                            cursor -= 1

                    elif key == "\x1b[B":  # Right arrow
                        if cursor < len(options):
                            cursor += 1
                    if key == "\r":
                        if cursor == len(states):
                            return [s for s, v in states.items() if v]
                        states[_get(cursor)] = not states[_get(cursor)]
                    _render(lines_count)
        except KeyboardInterrupt as e:
            return [s for s, v in states.items() if v]
        finally:
            self.show_cursor()
            self.newline()

    def confirm(self, question: str = "", preferred: bool = True) -> bool:
        y = "Y" if preferred else "y"
        n = "n" if preferred else "N"
        truthy = ["true", "yes", "y"]
        falsy = ["false", "no", "n"]
        prop = f"{question} [{y}/{n}]> "
        final: bool = preferred
        rep = False
        while True:
            user = self.input(prop)
            if user.lower() in truthy:
                final = True
                break
            elif user.lower() in falsy:
                final = False
                break
            elif user.strip(" ") == "":
                rep = True
                break
            else:
                print("Please provide a yes/no answer!")


        val = y if final else n
        if rep:
            self.move_cursor(lines=-1)
            self.replace_line(prop + val)
        return final
    
    def choice(self, choices: list[str] | tuple[str, ...], *,  question: str = "Choose an option listed", case_sensitive: bool = False):
        choices = tuple(choices)
        answer = ""
        while True:
            answer = self.input(prompt=f"{question} [{"/".join(choices)}] > ")
            ranswer = answer
            if not case_sensitive:
                ranswer = answer.lower()
            if ranswer in choices:
                return ranswer
            
            self.print("Please choose a valid choice!")
        return ""
    
    def progress_bar(self, *, start: int = 0, end: int = 100, steps: int = 10, label: str = "") -> ProgressBar:
        return ProgressBar(
            self,
            start=start,
            end=end,
            steps=steps,
            label=label
        )
    
    def spinner(self, *, label: str = "", type: SpinnerType = "square") -> Spinner:
        return Spinner(self, label=label, spinner_type=type)

    def hide_cursor(self):
        self.raw_print("\033[?25l")
    def show_cursor(self):
        self.raw_print("\033[?25h")

    def move_cursor(self, *, lines: int = 0, horiz: int = 0):
        if lines < 0:
            self.raw_print(f"\033[{abs(lines)}F")
        elif lines > 0:
            self.raw_print(f"\033[{lines}E")

        if horiz < 0:
            self.raw_print(f"\033[{abs(horiz)}D")
        elif horiz > 0:
            self.raw_print(f"\033[{horiz}C")

        self.flush()

    def clear_line(self):
        self.stdout.write("\r\033[K")  # clear line
    
    def flush(self):
        self.stdout.flush()

    def replace_line(self, new: str, newline: bool = True, bottom: bool = False):
        if bottom:
            self._sticky_line = new
        self.clear_line()
        self.raw_print(new)
        if newline:
            self.newline()

    def format(self, text: str) -> str:
        pattern = r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|-?\d+(?:\.\d+)?'

        def repl(match):
            text = match.group()

            if text[0] in "\"'":
                return f"[yellow]{text}[/yellow]"
            else:
                return f"[cyan]{text}[/cyan]"

        result = re.sub(pattern, repl, text)
        return clr.process_tags(result)

    def pprint(self, pretty_text: str, end: str | None = None):
        self.print(self.format(pretty_text), end=end)

    def newline(self):
        self.stdout.write(self.nl)


    def password(self, prompt: str, *, censor: Optional[str] = None) -> str:
        self.raw_print(prompt)
        if self.piped:
            return self.stdin.readline().strip("\n")
        typed = ""
        cursor = 0
        buf =[]
        input_h = len(self._input_history)
        with self.raw:
            #print(self._input_history)
            for key in self.raw:
                HORIZ_MOVEMENT = 0
                if key == "\r":
                    self.newline()
                    self.clear_line()
                    return "".join(buf)
                
                if key == "\x7f":  # Backspace
                    if cursor > 0:
                        del buf[cursor - 1]
                        cursor -= 1
                    HORIZ_MOVEMENT -= 1
                else: # Any other key
                    buf.append(key)
                    cursor += 1
                    HORIZ_MOVEMENT += 1             

                text = ''.join(buf)
                if censor:
                    self.raw_print('\r\033[K' + prompt + (len(text)* censor))
                else:
                    self.raw_print('\r\033[K' + prompt)

                move_left = len(text) - cursor
                if move_left > 0:
                    self.raw_print(f'\033[{move_left}D')

                self.flush()

        return typed
    
    def input(self, prompt: str) -> str:
        self.raw_print(prompt)
        if self.piped:
            return self.stdin.readline().strip("\n")
        typed = ""
        cursor = 0
        buf =[]
        input_h = len(self._input_history)
        with self.raw:
            #print(self._input_history)
            for key in self.raw:
                HORIZ_MOVEMENT = 0
                if key == "\r":
                    self.newline()
                    self.clear_line()
                    self._input_history.append("".join(buf))
                    return "".join(buf)
                
                
                if key == "\x7f":  # Backspace
                    if cursor > 0:
                        del buf[cursor - 1]
                        cursor -= 1
                    HORIZ_MOVEMENT -= 1

                elif key == '\x1b[D':  # Left arrow
                    if cursor > 0:
                        cursor -= 1
                    HORIZ_MOVEMENT -= 1


                elif key == '\x1b[A':  # Up arrow
                    try:
                        input_h -= 1
                        if input_h < 0:
                            input_h = 0
                        buf = list(self._input_history[input_h])
                        if input_h <= 0:
                            input_h = 0
                    except IndexError:
                        continue
                    cursor = len(buf)

                elif key == '\x1b[B':  # Down arrow
                    input_h += 1
                    if input_h > len(self._input_history)-1:
                        input_h = len(self._input_history)-1
                        buf = []
                    else:
                        buf = list(self._input_history[input_h])
                    cursor = len(buf)


                elif key == "\x1b[C":  # Right arrow
                    if cursor < len(buf):
                        cursor += 1
                    HORIZ_MOVEMENT += 1
                else:
                    buf.append(key)
                    cursor += 1
                    HORIZ_MOVEMENT += 1             

                text = ''.join(buf)
                self.raw_print('\r\033[K' + prompt + text)

                move_left = len(text) - cursor
                if move_left > 0:
                    self.raw_print(f'\033[{move_left}D')

                self.flush()

        return typed + self.nl

    def raw_print(self, content: str, flush: bool = True):
        self.stdout.write(content)
        if flush:
            self.flush()

    def print(self, content: str, flush: bool = True, end: str | None = None):
        end = self.nl if end is None else end
        text = content + end

        if self._sticky_line is not None:
            self.raw_print("\r\033[K", flush=False)

        self.stdout.write(text)
        self._lines_made += text.count(self.nl)

        if self._sticky_line is not None:
            if not text.endswith(self.nl):
                self.stdout.write(self.nl)
                self._lines_made += 1

            self.raw_print("\r\033[K" + self._sticky_line, flush=False)

        if flush:
            self.flush()

    
    @property
    def piped(self):
        return not self.stdin.isatty()