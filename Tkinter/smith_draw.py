import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import os

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

CANVAS_BG  = "#1a1a1a"
TOOLBAR_BG = "#111111"
APP_BG     = "#0d0d0d"
ACCENT     = "#c8a96e"
BTN_BG     = "#1a1a1a"
BTN_FG     = "#aaaaaa"
SEP_COLOR  = "#333333"
BOTTOM_BG  = "#0e0e0e"


class CanvasTab:
    def __init__(self, parent, tab_id):
        self.tab_id = tab_id
        self.drawing_history = [[]]
        self.redo_stack      = []
        self.temp_shape      = None
        self.last_x = self.last_y   = None
        self.start_x = self.start_y = None

        self.selected_item   = None
        self.drag_start_x    = None
        self.drag_start_y    = None
        self.drag_item_start = None

        self.frame = tk.Frame(parent, bg=APP_BG)
        wrapper    = tk.Frame(self.frame, bg="#252525", bd=1, relief=tk.FLAT)
        wrapper.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(wrapper, bg=CANVAS_BG, cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw_grid())

    def _redraw_grid(self):
        self.canvas.delete("grid")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for x in range(0, w, 40):
            self.canvas.create_line(x, 0, x, h, fill="#1e1e1e", tags="grid")
        for y in range(0, h, 40):
            self.canvas.create_line(0, y, w, y, fill="#1e1e1e", tags="grid")
        self.canvas.tag_lower("grid")

    def save_snapshot(self):
        items    = self.canvas.find_withtag("drawing")
        snapshot = []
        for item in items:
            itype  = self.canvas.type(item)
            coords = self.canvas.coords(item)
            cfg    = {}
            for key in ("fill", "outline", "width", "capstyle", "smooth", "text", "font", "anchor"):
                try:
                    cfg[key] = self.canvas.itemcget(item, key)
                except Exception:
                    pass
            snapshot.append((itype, coords, cfg))
        self.drawing_history.append(snapshot)
        self.redo_stack.clear()

    def restore_snapshot(self, snapshot):
        self.canvas.delete("drawing")
        self.selected_item = None
        for itype, coords, cfg in snapshot:
            if itype == "line":
                self.canvas.create_line(*coords, tags="drawing",
                    **{k: v for k, v in cfg.items() if k in ("fill", "width", "capstyle", "smooth")})
            elif itype == "rectangle":
                self.canvas.create_rectangle(*coords, tags="drawing",
                    **{k: v for k, v in cfg.items() if k in ("fill", "outline", "width")})
            elif itype == "oval":
                self.canvas.create_oval(*coords, tags="drawing",
                    **{k: v for k, v in cfg.items() if k in ("fill", "outline", "width")})
            elif itype == "text":
                self.canvas.create_text(*coords, tags="drawing",
                    **{k: v for k, v in cfg.items() if k in ("fill", "text", "font", "anchor")})

    def undo(self):
        if len(self.drawing_history) > 1:
            self.redo_stack.append(self.drawing_history.pop())
            self.restore_snapshot(self.drawing_history[-1])

    def redo(self):
        if self.redo_stack:
            snap = self.redo_stack.pop()
            self.drawing_history.append(snap)
            self.restore_snapshot(snap)

    def clear(self):
        self.save_snapshot()
        self.canvas.delete("drawing")
        self.selected_item = None
        self.save_snapshot()


class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smith Draw")
        self.root.geometry("1280x820")
        self.root.minsize(800, 550)
        self.root.resizable(True, True)
        self.root.configure(bg=APP_BG)

        self.current_tool     = tk.StringVar(value="pen")
        self.brush_size       = tk.IntVar(value=4)
        self.brush_color      = "#ffffff"
        self.fill_color       = None
        self.eraser_on        = False
        self.text_font_family = tk.StringVar(value="Arial")
        self.text_font_size   = tk.IntVar(value=18)
        self.text_bold        = tk.BooleanVar(value=False)
        self.text_italic      = tk.BooleanVar(value=False)

        self.tabs         = {}
        self.tab_counter  = 0
        self.active_tab   = None

        self._build_ui()
        self._bind_global_events()
        self._new_tab()

    def _build_ui(self):
        self._build_toolbar()
        self._build_tab_bar()
        self._build_main_area()
        self._build_bottom_bar()

    def _build_toolbar(self):
        toolbar = tk.Frame(self.root, bg=TOOLBAR_BG)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        inner = tk.Frame(toolbar, bg=TOOLBAR_BG)
        inner.pack(fill=tk.X, padx=8, pady=7)

        tk.Label(inner, text="◈ Smith Draw", font=("Courier New", 13, "bold"),
                 fg=ACCENT, bg=TOOLBAR_BG).pack(side=tk.LEFT, padx=(4, 24))

        tools = [
            ("✏", "pen",     "Pen"),
            ("↖", "select",  "Select"),
            ("T",  "text",   "Text"),
            ("╱",  "line",   "Line"),
            ("▭",  "rect",   "Rect"),
            ("◯",  "ellipse","Ellipse"),
            ("⌫",  "eraser", "Eraser"),
        ]
        self.tool_buttons = {}
        for icon, tool, tip in tools:
            btn = tk.Button(inner, text=f"{icon}  {tip}",
                font=("Courier New", 9, "bold"),
                fg=BTN_FG, bg=BTN_BG,
                activeforeground=ACCENT, activebackground="#222222",
                relief=tk.FLAT, cursor="hand2", padx=10, pady=6,
                command=lambda t=tool: self._select_tool(t))
            btn.pack(side=tk.LEFT, padx=2)
            self.tool_buttons[tool] = btn

        self._sep(inner)

        size_f = tk.Frame(inner, bg=TOOLBAR_BG)
        size_f.pack(side=tk.LEFT, padx=4)
        tk.Label(size_f, text="SIZE", font=("Courier New", 7, "bold"),
                 fg="#555555", bg=TOOLBAR_BG).pack()
        tk.Scale(size_f, variable=self.brush_size, from_=1, to=80,
                 orient=tk.HORIZONTAL, length=100, font=("Courier New", 7),
                 fg=BTN_FG, bg=TOOLBAR_BG, troughcolor="#1e1e1e",
                 highlightthickness=0, activebackground=ACCENT).pack()

        self._sep(inner)

        col_f = tk.Frame(inner, bg=TOOLBAR_BG)
        col_f.pack(side=tk.LEFT, padx=4)
        tk.Label(col_f, text="STROKE", font=("Courier New", 7, "bold"),
                 fg="#555555", bg=TOOLBAR_BG).pack()
        self.color_preview = tk.Canvas(col_f, width=44, height=26, bg=self.brush_color,
            highlightthickness=1, highlightbackground="#444444", cursor="hand2")
        self.color_preview.pack()
        self.color_preview.bind("<Button-1>", self._pick_color)

        fil_f = tk.Frame(inner, bg=TOOLBAR_BG)
        fil_f.pack(side=tk.LEFT, padx=6)
        tk.Label(fil_f, text="FILL", font=("Courier New", 7, "bold"),
                 fg="#555555", bg=TOOLBAR_BG).pack()
        self.fill_preview = tk.Canvas(fil_f, width=44, height=26, bg=APP_BG,
            highlightthickness=1, highlightbackground="#444444", cursor="hand2")
        self.fill_preview.pack()
        self.fill_preview.bind("<Button-1>", self._pick_fill_color)

        self._sep(inner)

        self.text_opt = tk.Frame(inner, bg=TOOLBAR_BG)

        tk.Label(self.text_opt, text="FONT", font=("Courier New", 7, "bold"),
                 fg="#555555", bg=TOOLBAR_BG).grid(row=0, column=0, sticky="w")
        tk.Label(self.text_opt, text="SIZE", font=("Courier New", 7, "bold"),
                 fg="#555555", bg=TOOLBAR_BG).grid(row=0, column=1, sticky="w", padx=(6, 0))

        families  = ["Arial", "Courier New", "Times New Roman", "Helvetica", "Georgia", "Verdana"]
        font_menu = tk.OptionMenu(self.text_opt, self.text_font_family, *families)
        font_menu.config(font=("Courier New", 8), fg=BTN_FG, bg="#1e1e1e",
                         activeforeground=ACCENT, activebackground="#222222",
                         relief=tk.FLAT, highlightthickness=0, width=10)
        font_menu["menu"].config(bg="#1e1e1e", fg=BTN_FG, font=("Courier New", 8))
        font_menu.grid(row=1, column=0, sticky="w")

        tk.Spinbox(self.text_opt, textvariable=self.text_font_size,
                   from_=6, to=120, width=4,
                   font=("Courier New", 9), fg=BTN_FG, bg="#1e1e1e",
                   buttonbackground="#222222", relief=tk.FLAT).grid(row=1, column=1, padx=(6, 0))

        tk.Checkbutton(self.text_opt, text="B", variable=self.text_bold,
                       font=("Courier New", 9, "bold"), fg=BTN_FG, bg=TOOLBAR_BG,
                       activeforeground=ACCENT, selectcolor="#222222",
                       relief=tk.FLAT).grid(row=1, column=2, padx=(6, 0))
        tk.Checkbutton(self.text_opt, text="I", variable=self.text_italic,
                       font=("Courier New", 9, "italic"), fg=BTN_FG, bg=TOOLBAR_BG,
                       activeforeground=ACCENT, selectcolor="#222222",
                       relief=tk.FLAT).grid(row=1, column=3, padx=(2, 0))

    def _sep(self, parent):
        tk.Frame(parent, bg=SEP_COLOR, width=1).pack(side=tk.LEFT, padx=12, fill=tk.Y, pady=4)

    def _build_tab_bar(self):
        self.tab_bar = tk.Frame(self.root, bg="#0d0d0d", height=34)
        self.tab_bar.pack(side=tk.TOP, fill=tk.X)
        self.tab_bar.pack_propagate(False)
        self.tab_buttons_frame = tk.Frame(self.tab_bar, bg="#0d0d0d")
        self.tab_buttons_frame.pack(side=tk.LEFT, padx=8, pady=4)

    def _build_main_area(self):
        container = tk.Frame(self.root, bg=APP_BG)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 0))

        pal_frame = tk.Frame(container, bg=TOOLBAR_BG, width=54)
        pal_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        pal_frame.pack_propagate(False)

        tk.Label(pal_frame, text="PAL", font=("Courier New", 6, "bold"),
                 fg="#444444", bg=TOOLBAR_BG).pack(pady=(8, 4))

        for color in [
            "#ffffff", "#c8a96e", "#e05252", "#52c0e0",
            "#7ee052", "#c452e0", "#e09652", "#5266e0",
            "#e0d152", "#52e0b4", "#e05296", "#888888",
            "#444444", "#000000", "#1a1a2e", "#16213e",
        ]:
            sw = tk.Canvas(pal_frame, width=30, height=16, bg=color,
                           highlightthickness=1, highlightbackground="#2a2a2a", cursor="hand2")
            sw.pack(pady=1)
            sw.bind("<Button-1>", lambda e, c=color: self._set_color(c))

        self.canvas_container = tk.Frame(container, bg=APP_BG)
        self.canvas_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def _build_bottom_bar(self):
        bottom = tk.Frame(self.root, bg=BOTTOM_BG, height=46)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)
        bottom.pack_propagate(False)

        self.status_lbl = tk.Label(bottom, text="  Ready",
            font=("Courier New", 8), fg="#444444", bg=BOTTOM_BG, anchor=tk.W)
        self.status_lbl.pack(side=tk.LEFT, padx=12)

        right_bar = tk.Frame(bottom, bg=BOTTOM_BG)
        right_bar.pack(side=tk.RIGHT, padx=10)

        pil_txt = "Pillow ✓" if PIL_AVAILABLE else "Pillow ✗"
        tk.Label(right_bar, text=pil_txt, font=("Courier New", 8),
                 fg="#333333", bg=BOTTOM_BG).pack(side=tk.RIGHT, padx=(0, 16))

        actions = [
            ("＋ New Tab",  self._new_tab),
            ("↩ Undo",      self._undo),
            ("↪ Redo",      self._redo),
            ("⊘ Clear",     self._clear_canvas),
            ("⇓  Save As",  self._save_canvas),
        ]
        for label, cmd in actions:
            tk.Button(right_bar, text=label, font=("Courier New", 9, "bold"),
                fg=BTN_FG, bg="#1e1e1e",
                activeforeground=ACCENT, activebackground="#252525",
                relief=tk.FLAT, cursor="hand2",
                padx=14, pady=4, command=cmd).pack(side=tk.LEFT, padx=3, pady=6)

    def _bind_global_events(self):
        self.root.bind("<Control-z>", lambda e: self._undo())
        self.root.bind("<Control-y>", lambda e: self._redo())
        self.root.bind("<Control-s>", lambda e: self._save_canvas())
        self.root.bind("<Control-t>", lambda e: self._new_tab())
        self.root.bind("<Escape>",    lambda e: self._deselect_item())

    def _new_tab(self):
        self.tab_counter += 1
        tid = self.tab_counter
        tab = CanvasTab(self.canvas_container, tid)
        self.tabs[tid] = tab

        tbf = tk.Frame(self.tab_buttons_frame, bg="#1a1a1a")
        tbf.pack(side=tk.LEFT, padx=2)

        lbl = tk.Button(tbf, text=f"  Canvas {tid}  ",
            font=("Courier New", 8, "bold"), fg=BTN_FG, bg="#1a1a1a",
            activeforeground=ACCENT, activebackground="#222222",
            relief=tk.FLAT, cursor="hand2",
            command=lambda t=tid: self._switch_tab(t))
        lbl.pack(side=tk.LEFT)

        tk.Button(tbf, text="✕",
            font=("Courier New", 8), fg="#555555", bg="#1a1a1a",
            activeforeground="#ff5555", activebackground="#222222",
            relief=tk.FLAT, cursor="hand2",
            command=lambda t=tid: self._close_tab(t)).pack(side=tk.LEFT, padx=(0, 2))

        tab.tab_btn_frame = tbf
        tab.tab_lbl       = lbl
        self._switch_tab(tid)

    def _switch_tab(self, tid):
        if self.active_tab and self.active_tab in self.tabs:
            self.tabs[self.active_tab].frame.pack_forget()
            self.tabs[self.active_tab].tab_lbl.config(fg=BTN_FG, bg="#1a1a1a")

        self.active_tab = tid
        tab = self.tabs[tid]
        tab.frame.pack(fill=tk.BOTH, expand=True)
        tab.tab_lbl.config(fg=ACCENT, bg="#252525")

        tab.canvas.bind("<ButtonPress-1>",   self._on_press)
        tab.canvas.bind("<B1-Motion>",       self._on_drag)
        tab.canvas.bind("<ButtonRelease-1>", self._on_release)
        tab.canvas.bind("<Motion>",          self._on_move)
        tab.canvas.bind("<Double-Button-1>", self._on_double_click)

    def _close_tab(self, tid):
        if len(self.tabs) == 1:
            messagebox.showinfo("Info", "Cannot close the last tab.")
            return
        tab = self.tabs.pop(tid)
        tab.frame.destroy()
        tab.tab_btn_frame.destroy()
        if self.active_tab == tid:
            self._switch_tab(list(self.tabs.keys())[-1])

    def _current_tab(self):
        return self.tabs.get(self.active_tab)

    def _select_tool(self, tool):
        self.eraser_on = (tool == "eraser")
        self.current_tool.set(tool)
        for t, btn in self.tool_buttons.items():
            btn.config(fg=ACCENT if t == tool else BTN_FG,
                       bg="#252525" if t == tool else BTN_BG)
        if tool == "text":
            self.text_opt.pack(side=tk.LEFT, padx=4)
        else:
            self.text_opt.pack_forget()
        tab = self._current_tab()
        if tab and tool != "select":
            self._deselect_item()

    def _deselect_item(self):
        tab = self._current_tab()
        if tab and tab.selected_item:
            try:
                tab.canvas.itemconfig(tab.selected_item, outline=self.brush_color if tab.canvas.type(tab.selected_item) != "text" else "")
            except Exception:
                pass
            tab.canvas.delete("sel_handle")
            tab.selected_item = None

    def _on_press(self, event):
        tab  = self._current_tab()
        if not tab:
            return
        tool = self.current_tool.get()

        if tool == "select":
            self._try_select_item(event, tab)
            return

        if tool == "text":
            self._place_text(event, tab)
            return

        tab.last_x,  tab.last_y  = event.x, event.y
        tab.start_x, tab.start_y = event.x, event.y

        if tool in ("pen", "eraser"):
            tab.save_snapshot()

    def _try_select_item(self, event, tab):
        tab.canvas.delete("sel_handle")
        closest = tab.canvas.find_closest(event.x, event.y)
        if closest:
            item = closest[0]
            tags = tab.canvas.gettags(item)
            if "drawing" in tags:
                tab.selected_item  = item
                tab.drag_start_x   = event.x
                tab.drag_start_y   = event.y
                itype              = tab.canvas.type(item)
                coords             = tab.canvas.coords(item)
                if itype != "text" and len(coords) >= 4:
                    x1, y1, x2, y2 = coords[0], coords[1], coords[-2], coords[-1]
                    tab.canvas.create_rectangle(x1-3, y1-3, x2+3, y2+3,
                        outline=ACCENT, dash=(4, 2), tags="sel_handle", width=1)
                else:
                    cx, cy = coords[0], coords[1] if len(coords) >= 2 else (event.x, event.y)
                    tab.canvas.create_rectangle(cx-6, cy-6, cx+6, cy+6,
                        outline=ACCENT, dash=(4, 2), tags="sel_handle", width=1)
                tab.canvas.tag_raise(item)
                return
        tab.selected_item = None

    def _on_drag(self, event):
        tab  = self._current_tab()
        if not tab:
            return
        tool = self.current_tool.get()

        if tool == "select" and tab.selected_item:
            dx = event.x - tab.drag_start_x
            dy = event.y - tab.drag_start_y
            tab.canvas.move(tab.selected_item, dx, dy)
            tab.canvas.move("sel_handle",      dx, dy)
            tab.drag_start_x = event.x
            tab.drag_start_y = event.y
            return

        if tool in ("text", "select"):
            return

        x, y  = event.x, event.y
        color = CANVAS_BG if self.eraser_on else self.brush_color
        size  = self.brush_size.get()

        if tool in ("pen", "eraser"):
            if tab.last_x is not None:
                tab.canvas.create_line(tab.last_x, tab.last_y, x, y,
                    fill=color, width=size, capstyle=tk.ROUND,
                    smooth=True, tags="drawing")
        elif tool in ("line", "rect", "ellipse"):
            if tab.temp_shape:
                tab.canvas.delete(tab.temp_shape)
            fill = self.fill_color or ""
            if tool == "line":
                tab.temp_shape = tab.canvas.create_line(tab.start_x, tab.start_y, x, y,
                    fill=color, width=size, tags="temp")
            elif tool == "rect":
                tab.temp_shape = tab.canvas.create_rectangle(tab.start_x, tab.start_y, x, y,
                    outline=color, fill=fill, width=size, tags="temp")
            elif tool == "ellipse":
                tab.temp_shape = tab.canvas.create_oval(tab.start_x, tab.start_y, x, y,
                    outline=color, fill=fill, width=size, tags="temp")

        tab.last_x, tab.last_y = x, y

    def _on_release(self, event):
        tab  = self._current_tab()
        if not tab:
            return
        tool = self.current_tool.get()

        if tool == "select" and tab.selected_item:
            tab.save_snapshot()
            return

        if tool in ("line", "rect", "ellipse"):
            tab.save_snapshot()
            if tab.temp_shape:
                tab.canvas.itemconfig(tab.temp_shape, tags="drawing")
                tab.temp_shape = None

        tab.last_x = tab.last_y = None

    def _on_move(self, event):
        self.status_lbl.config(
            text=f"  Tool: {self.current_tool.get().capitalize()}  |  "
                 f"Brush: {self.brush_size.get()}px  |  X: {event.x}  Y: {event.y}")

    def _on_double_click(self, event):
        tab  = self._current_tab()
        if not tab:
            return
        tool = self.current_tool.get()
        if tool != "select":
            return
        closest = tab.canvas.find_closest(event.x, event.y)
        if not closest:
            return
        item  = closest[0]
        tags  = tab.canvas.gettags(item)
        itype = tab.canvas.type(item)
        if "drawing" not in tags:
            return
        if itype == "text":
            self._edit_text_item(item, tab)

    def _edit_text_item(self, item, tab):
        old_text = tab.canvas.itemcget(item, "text")
        old_font = tab.canvas.itemcget(item, "font")

        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Text")
        dialog.geometry("400x180")
        dialog.configure(bg=TOOLBAR_BG)
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Edit text:", font=("Courier New", 9, "bold"),
                 fg=BTN_FG, bg=TOOLBAR_BG).pack(pady=(16, 4))

        entry = tk.Entry(dialog, font=("Courier New", 12), fg="#ffffff", bg="#1e1e1e",
                         insertbackground="#ffffff", relief=tk.FLAT, width=34)
        entry.insert(0, old_text)
        entry.select_range(0, tk.END)
        entry.pack(padx=20, ipady=6)
        entry.focus_set()

        def confirm(e=None):
            txt = entry.get().strip()
            if txt:
                tab.save_snapshot()
                tab.canvas.itemconfig(item, text=txt)
                tab.save_snapshot()
            dialog.destroy()

        entry.bind("<Return>", confirm)
        btn_row = tk.Frame(dialog, bg=TOOLBAR_BG)
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="  Save  ", font=("Courier New", 9, "bold"),
                  fg=ACCENT, bg="#252525", relief=tk.FLAT, cursor="hand2",
                  command=confirm).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="  Cancel  ", font=("Courier New", 9, "bold"),
                  fg=BTN_FG, bg=BTN_BG, relief=tk.FLAT, cursor="hand2",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=6)

    def _place_text(self, event, tab):
        dialog = tk.Toplevel(self.root)
        dialog.title("Insert Text")
        dialog.geometry("400x180")
        dialog.configure(bg=TOOLBAR_BG)
        dialog.resizable(False, False)
        dialog.grab_set()

        tk.Label(dialog, text="Enter text:", font=("Courier New", 9, "bold"),
                 fg=BTN_FG, bg=TOOLBAR_BG).pack(pady=(16, 4))

        entry = tk.Entry(dialog, font=("Courier New", 12), fg="#ffffff", bg="#1e1e1e",
                         insertbackground="#ffffff", relief=tk.FLAT, width=34)
        entry.pack(padx=20, ipady=6)
        entry.focus_set()

        def confirm(e=None):
            txt = entry.get().strip()
            if txt:
                parts = []
                if self.text_bold.get():
                    parts.append("bold")
                if self.text_italic.get():
                    parts.append("italic")
                style    = " ".join(parts)
                font_spec = (self.text_font_family.get(), self.text_font_size.get(), style) if style \
                            else (self.text_font_family.get(), self.text_font_size.get())
                tab.save_snapshot()
                tab.canvas.create_text(event.x, event.y, text=txt,
                    fill=self.brush_color, font=font_spec,
                    anchor=tk.NW, tags="drawing")
                tab.save_snapshot()
            dialog.destroy()

        entry.bind("<Return>", confirm)
        btn_row = tk.Frame(dialog, bg=TOOLBAR_BG)
        btn_row.pack(pady=12)
        tk.Button(btn_row, text="  Insert  ", font=("Courier New", 9, "bold"),
                  fg=ACCENT, bg="#252525", relief=tk.FLAT, cursor="hand2",
                  command=confirm).pack(side=tk.LEFT, padx=6)
        tk.Button(btn_row, text="  Cancel  ", font=("Courier New", 9, "bold"),
                  fg=BTN_FG, bg=BTN_BG, relief=tk.FLAT, cursor="hand2",
                  command=dialog.destroy).pack(side=tk.LEFT, padx=6)

    def _pick_color(self, event=None):
        color = colorchooser.askcolor(color=self.brush_color, title="Stroke Color")[1]
        if color:
            self._set_color(color)

    def _set_color(self, color):
        self.brush_color = color
        self.color_preview.config(bg=color)
        self.eraser_on = False
        if self.current_tool.get() == "eraser":
            self._select_tool("pen")

    def _pick_fill_color(self, event=None):
        color = colorchooser.askcolor(title="Fill Color")[1]
        if color:
            self.fill_color = color
            self.fill_preview.config(bg=color)
        else:
            self.fill_color = None
            self.fill_preview.config(bg=APP_BG)

    def _undo(self):
        tab = self._current_tab()
        if tab:
            tab.undo()

    def _redo(self):
        tab = self._current_tab()
        if tab:
            tab.redo()

    def _clear_canvas(self):
        tab = self._current_tab()
        if tab and messagebox.askyesno("Clear Canvas", "Clear everything on this canvas?"):
            tab.clear()

    def _save_canvas(self):
        tab = self._current_tab()
        if not tab:
            return

        if PIL_AVAILABLE:
            filetypes   = [("PNG Image", "*.png"), ("JPEG Image", "*.jpg"),
                           ("PostScript", "*.ps"), ("All Files", "*.*")]
            default_ext = ".png"
        else:
            filetypes   = [("PostScript", "*.ps"), ("All Files", "*.*")]
            default_ext = ".ps"

        path = filedialog.asksaveasfilename(
            defaultextension=default_ext,
            filetypes=filetypes,
            title="Save Canvas As"
        )
        if not path:
            return

        ext = os.path.splitext(path)[1].lower()

        if ext == ".ps":
            tab.canvas.postscript(file=path, colormode="color")
            messagebox.showinfo("Saved", f"Saved:\n{path}")
            return

        if PIL_AVAILABLE and ext in (".png", ".jpg", ".jpeg"):
            ps_tmp = path + "_tmp.ps"
            tab.canvas.postscript(file=ps_tmp, colormode="color")
            try:
                img = Image.open(ps_tmp)
                if ext in (".jpg", ".jpeg"):
                    img = img.convert("RGB")
                img.save(path)
                messagebox.showinfo("Saved", f"Saved:\n{path}")
            except Exception:
                self._save_via_grab(tab, path, ext)
            finally:
                if os.path.exists(ps_tmp):
                    os.remove(ps_tmp)
        else:
            messagebox.showerror("Error", "Unsupported format.")

    def _save_via_grab(self, tab, path, ext):
        try:
            tab.canvas.update()
            x  = tab.canvas.winfo_rootx()
            y  = tab.canvas.winfo_rooty()
            w  = tab.canvas.winfo_width()
            h  = tab.canvas.winfo_height()
            img = ImageGrab.grab(bbox=(x, y, x + w, y + h))
            if ext in (".jpg", ".jpeg"):
                img = img.convert("RGB")
            img.save(path)
            messagebox.showinfo("Saved", f"Saved:\n{path}")
        except Exception as ex:
            messagebox.showerror("Save Failed", str(ex))


if __name__ == "__main__":
    root = tk.Tk()
    app  = DrawingApp(root)
    root.mainloop()