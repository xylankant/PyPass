#! /usr/bin/env python3
# coding: utf-8

from tkinter import *
from tkinter.ttk import *
from colors import strip_color
import subprocess
from os.path import realpath

class PyPass(object):
    def __init__(self):
        self.version = "0.1alpha"
        self.tree_branch_1 = b"\xe2\x94\x9c\xe2\x94\x80\xe2\x94\x80 ".decode("utf-8")
        self.tree_branch_2 = b"\xe2\x94\x94\xe2\x94\x80\xe2\x94\x80 ".decode("utf-8")
        self.tree_branch_3 = b'\xe2\x94\x82'.decode("utf-8")
        self.root = Tk()
        self.root.title("PyPass")
        self.root.geometry("640x320+0+0")
        self.icon = realpath(__file__).replace(".py", ".png")
        self.root.tk.call('wm', 'iconphoto', self.root._w, PhotoImage(file=self.icon))

        menubar = Menu(self.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Password", command=self.gen_pass_popup)
        filemenu.add_command(label="Edit Password", command=self.gen_edit_popup)
        filemenu.add_separator()
        filemenu.add_separator()
        filemenu.add_command(label="Delete Password", command=self.del_pass)
        filemenu.add_separator()
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self.about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        # display the menu
        self.root.config(menu=menubar)

        m = PanedWindow(self.root, orient=HORIZONTAL)
        m.pack(fill=BOTH, expand=Y)

        left = Label(m, text="left pane")
        m.add(left)

        right = Label(m, text="right pane")
        m.add(right)

        scrollbar = Scrollbar(left, orient="vertical")
        self.lb = Listbox(left, yscrollcommand=scrollbar.set, selectmode=SINGLE)
        scrollbar.config(command=self.lb.yview)

        scrollbar.pack(side="right", fill="y")
        self.lb.pack(side="top",fill="both", expand=True)
        
        self.pw_area = Text(right, state=DISABLED, height=1)
        self.pw_area.pack(side="top", fill="x", expand=0)
        
        self.info_area = Text(right, state=DISABLED)
        self.info_area.pack(side="top", fill="both", expand=1)
        
        getButton = Button(left, text="Get Password", command=self.display_password)
        getButton.pack(side="bottom")
        self.get_pass_tree()
        
        self.root.mainloop()

    def about(self):
        window = Toplevel()
        window.grab_set()
        window.title("About")
        window.tk.call('wm', 'iconphoto', window._w, PhotoImage(file=self.icon))
        about_str = f"PyPass version {self.version}\nA simple python/tk interface to passwordstore.\n(c) Philip John Gorinski"
        text = Text(window, width=max([len(line) for line in about_str.split("\n")]), height=len(about_str.split("\n")))
        text.insert(END, about_str)
        text.config(state=DISABLED)
        text.pack()
        
    def get_selected(self):
        if self.lb.index(ACTIVE) == 0:
            return None
        cur_idx = self.lb.index(ACTIVE)
        cur_item = self.lb.get(cur_idx).replace(self.tree_branch_3, " ")
        cur_indent = len(cur_item) - len(cur_item.lstrip(" "))
        while cur_indent > 0:
            for prev_idx in range(cur_idx, 0, -1):
                prev_item = self.lb.get(prev_idx).replace(self.tree_branch_3, " ")
                prev_indent = len(prev_item) - len(prev_item.lstrip(" "))
                if prev_indent < cur_indent:
                    cur_item = prev_item + cur_item.strip()
                    cur_indent = prev_indent
                    cur_idx = prev_idx
                    break
                    
        selected = cur_item.replace(self.tree_branch_1, "/").replace(self.tree_branch_2, "/")[1:]
        return selected

    def del_pass(self):
        selected = self.get_selected()
        ret = subprocess.run(["pass", "rm", "-f", "-r", selected])
        self.get_pass_tree()
        
    def gen_pass(self, name, info, symbol_var, length_var, window):
        if not name:
            return
        if symbol_var:
            pw_cmd = [f"< /dev/urandom tr -dc A-Z-a-z-0-9\-[]\!$%^\&*_+=\(\) | head -c{length_var}"]
        else:
            pw_cmd = [f"< /dev/urandom tr -dc A-Z-a-z-0-9 | head -c{length_var}"]
        new_pw = subprocess.run(pw_cmd, shell=True, capture_output=True).stdout.decode("utf-8")
        for line in info.split("\n"):
            if line:
                new_pw += f"\n{line}"
        
        cmd = [f"printf '{new_pw}' | pass insert -m {name}"]
        p = subprocess.run(cmd, shell=True)
        window.destroy()
        self.get_pass_tree()

    def gen_pass_popup(self):
        window = Toplevel()
        window.grab_set()
        window.title("Generate New Password File")
        window.tk.call('wm', 'iconphoto', window._w, PhotoImage(file=self.icon))
        
        pw_name_var = StringVar()
        Label(window, text="Name/Path:").grid(row=0, column=0, sticky="W")
        pw_name_text = Entry(window, width=50, textvariable=pw_name_var)
        pw_name_text.grid(row=0, column=1, columnspan=2)
        
        len_var = StringVar()
        len_var.set("25")
        Label(window, text="Password length:").grid(row=2, column=0, sticky="W")
        #pw_len_text = Entry(window, width=3, validate="all", textvariable=len_var, validatecommand=lambda: _validate_num(len_var))
        pw_len_box = Combobox(window, textvariable=len_var, values=[str(i) for i in range(5,51)], width=3, state="readonly")
        pw_len_box.grid(row=2, column=1, sticky="W")
        
        use_symbols = IntVar()
        use_symbols.set(1)
        pw_symbols_box = Checkbutton(window, text="Use special symbols?", variable=use_symbols)
        pw_symbols_box.grid(row=3, column=1, sticky="W")
        
        Label(window, text="Additional info:").grid(row=1, column=0, sticky="W")
        info_text = Text(window, width=50, height=5)
        info_text.grid(row=1, column=1, sticky="W")
        
        gen_button = Button(window, text="Generate new password", command=lambda: self.gen_pass(pw_name_var.get(), info_text.get(1.0, END), use_symbols.get() == 1, len_var.get(), window))
        gen_button.grid(row=4, column=0)
        
        window.resizable(False, False)

    def gen_edit_popup(self):
        if self.lb.index(ACTIVE) == 0:
            return
        window = Toplevel()
        window.grab_set()
        window.title("Edit Password File")
        window.tk.call('wm', 'iconphoto', window._w, PhotoImage(file=self.icon))
        
        name = self.get_selected()
        
        Label(window, text="Name/Path:").grid(row=0, column=0, sticky="W")
        pw_name_text = Entry(window, width=50)
        pw_name_text.insert(END, name)
        pw_name_text.config(state=DISABLED)
        pw_name_text.grid(row=0, column=1)
        
        pass_info = self.get_password()
        
        pw_string_var = StringVar()
        Label(window, text="Password:").grid(row=1, column=0, sticky="W")
        pw = Entry(window, width=50, textvariable=pw_string_var)
        pw.insert(END, pass_info[0])
        pw.grid(row=1, column=1)
        
        Label(window, text="Additional info:").grid(row=2, column=0, sticky="NW")
        info_text = Text(window, width=50, height=5)
        if len(pass_info) > 1:
            for line in pass_info[1:]:
                info_text.insert(END, line + "\n")
        info_text.grid(row=2, column=1, sticky="W")
        
        gen_button = Button(window, text="Save changes", command=lambda: self.edit_pass(name, pw_string_var.get(), info_text.get(1.0, END), window))
        gen_button.grid(row=3, column=0)
        
        window.resizable(False, False)

    def edit_pass(self, name, pw, info, window):
        new_pw = pw
        for line in info.split("\n"):
            if line:
                new_pw += f"\n{line}"
        
        cmd = [f"printf '{new_pw}' | pass insert -m -f {name}"]
        p = subprocess.run(cmd, shell=True)
        window.destroy()
        self.get_pass_tree()
        
    def get_pass_tree(self):
        self.lb.delete(0,END)
        tree = subprocess.run(["pass", "ls"], capture_output=True).stdout.decode("utf-8").strip().split("\n")
        for item in tree:
            self.lb.insert("end", strip_color(item))

    def display_password(self):
        pass_output = self.get_password()
        pw = pass_output[0]
        self.pw_area.config(state=NORMAL)
        self.pw_area.delete('1.0', END)
        self.pw_area.insert(END, pw)
        self.pw_area.config(state=DISABLED)
        
        self.info_area.config(state=NORMAL)
        self.info_area.delete('1.0', END)
        if len(pass_output)>1:
            for info in pass_output[1:]:
                self.info_area.insert(END, f"{info}\n")
        self.info_area.config(state=DISABLED)
        self.root.clipboard_clear()
        self.root.clipboard_append(pw)
        self.root.update()
        self.root.after(10000, self.clear)

    def get_password(self):
        selected = self.get_selected()
        if None == selected:
            return [""]
        pass_output = tree = subprocess.run(["pass", selected], capture_output=True).stdout.decode("utf-8").strip().split("\n")
        return pass_output
    
    def clear(self):
        self.pw_area.config(state=NORMAL)
        self.pw_area.delete('1.0', END)
        self.pw_area.config(state=DISABLED)
        self.info_area.config(state=NORMAL)
        self.info_area.delete('1.0', END)
        self.info_area.config(state=DISABLED)
        self.root.clipboard_clear()
        self.root.update()
    
if __name__ == "__main__":
    _=PyPass()
