import tkinter as tk

PIXEL_FONT = ("Courier", 14, "bold")
PIXEL_FONT_SMALL = ("Courier", 10, "bold")
PIXEL_FONT_LARGE = ("Courier", 28, "bold")
PIXEL_FONT_TINY = ("Courier", 8, "bold")

BG = "#F3E8FF"
BODY = "#EDD5F5"
SCREEN_BG = "#2D1554"
SCREEN_FG = "#F0ABFC"
SCREEN_FG2 = "#C084FC"
BTN_NUM_BG = "#FFFFFF"
BTN_NUM_FG = "#6B21A8"
BTN_NUM_BORDER = "#E879F9"
BTN_NUM_TOP = "#F0ABFC"
BTN_OP_BG = "#C084FC"
BTN_OP_FG = "#FFFFFF"
BTN_OP_TOP = "#E879F9"
BTN_AC_BG = "#E879F9"
BTN_AC_FG = "#FFFFFF"
BTN_AC_TOP = "#F0ABFC"
BTN_EQ_BG = "#E879F9"
BTN_EQ_FG = "#FFFFFF"
BTN_EQ_TOP = "#F5C0FF"
BORDER_DARK = "#B07DD8"
STRIP = "#E879F9"
STAR = "#E879F9"

expression = ""
result_var = None
expr_var = None

def pixel_button(parent, text, cmd, bg, fg, top_color, width=4, height=1, font=PIXEL_FONT):
    frame = tk.Frame(parent, bg=BODY, bd=0)
    top_bar = tk.Frame(frame, bg=top_color, height=4, bd=0)
    top_bar.pack(fill="x")
    btn = tk.Button(
        frame, text=text, command=cmd,
        bg=bg, fg=fg,
        font=font,
        width=width, height=height,
        relief="flat", bd=0,
        activebackground=top_color,
        activeforeground=fg,
        cursor="hand2"
    )
    btn.pack(fill="both")
    bottom_bar = tk.Frame(frame, bg=BORDER_DARK, height=3, bd=0)
    bottom_bar.pack(fill="x")
    right_bar = tk.Frame(frame, bg=BORDER_DARK, width=3, bd=0)
    right_bar.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
    frame.configure(highlightbackground=BTN_NUM_BORDER, highlightthickness=1)
    return frame

def press(val):
    global expression
    expression += str(val)
    result_var.set(expression)
    expr_var.set("")

def clear():
    global expression
    expression = ""
    result_var.set("0")
    expr_var.set("")

def backspace():
    global expression
    expression = expression[:-1]
    result_var.set(expression if expression else "0")

def toggle_sign():
    global expression
    if expression and expression[0] == "-":
        expression = expression[1:]
    elif expression:
        expression = "-" + expression
    result_var.set(expression if expression else "0")

def percent():
    global expression
    try:
        expression = str(eval(expression) / 100)
        result_var.set(expression)
    except:
        result_var.set("Error")
        expression = ""

def calculate():
    global expression
    try:
        expr_var.set(expression + " =")
        result = eval(expression)
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        expression = str(result)
        result_var.set(expression)
    except:
        result_var.set("Error")
        expr_var.set("")
        expression = ""

def draw_pixel_stars(canvas, x, y, color, size=4):
    canvas.create_rectangle(x, y-size, x+size, y, fill=color, outline="")
    canvas.create_rectangle(x-size, y, x, y+size, fill=color, outline="")
    canvas.create_rectangle(x, y, x+size, y+size, fill=color, outline="")
    canvas.create_rectangle(x+size, y-size, x+size*2, y, fill=color, outline="")

def draw_pixel_heart(canvas, x, y, color, s=4):
    pattern = [
        "0110011",
        "1111111",
        "1111111",
        "0111110",
        "0011100",
        "0001000",
    ]
    for row_i, row in enumerate(pattern):
        for col_i, cell in enumerate(row):
            if cell == "1":
                canvas.create_rectangle(
                    x + col_i*s, y + row_i*s,
                    x + col_i*s + s, y + row_i*s + s,
                    fill=color, outline=""
                )

root = tk.Tk()
root.title("✦ Pixel Calc ✦")
root.resizable(False, False)
root.configure(bg=BG)

result_var = tk.StringVar(value="0")
expr_var = tk.StringVar(value="")

CALC_W = 300
CALC_H = 560

outer = tk.Frame(root, bg=BG, padx=20, pady=20)
outer.pack()

deco_top = tk.Canvas(outer, width=CALC_W+20, height=40, bg=BG, highlightthickness=0)
deco_top.pack()
for i, x in enumerate(range(10, CALC_W, 30)):
    deco_top.create_rectangle(x, 10, x+6, 16, fill=STAR, outline="")
    deco_top.create_rectangle(x+3, 6, x+3+6, 12, fill=STAR, outline="", stipple="")
    deco_top.create_rectangle(x, 18, x+6, 24, fill="#C084FC", outline="")
deco_top.create_rectangle(150, 2, 156, 8, fill="#F472B6", outline="")
deco_top.create_rectangle(154, 0, 160, 6, fill="#F472B6", outline="")

calc_border = tk.Frame(outer, bg=BORDER_DARK, bd=0)
calc_border.pack()

calc = tk.Frame(calc_border, bg=BODY, bd=0,
                padx=2, pady=2)
calc.pack(padx=3, pady=3)

top_strip = tk.Frame(calc, bg=STRIP, height=14)
top_strip.pack(fill="x")

px_strip_canvas = tk.Canvas(top_strip, height=14, bg=STRIP, highlightthickness=0)
px_strip_canvas.pack(fill="x")
for xi in range(0, CALC_W, 8):
    px_strip_canvas.create_rectangle(xi, 4, xi+5, 10, fill="#F0ABFC", outline="", stipple="")

gem_canvas = tk.Canvas(calc, width=CALC_W, height=30, bg=BODY, highlightthickness=0)
gem_canvas.pack()
gx, gy = CALC_W//2, 10
gem = [
    (0,0,2,1,"#F0ABFC"),(2,0,4,1,"#E879F9"),(4,0,6,1,"#F0ABFC"),
    (-1,1,1,2,"#E879F9"),(1,1,3,2,"#FFFFFF"),(3,1,5,2,"#D946EF"),
    (0,2,2,3,"#C026D3"),(2,2,4,3,"#D946EF"),(4,2,6,3,"#C026D3"),
]
s = 5
for (dx1,dy1,dx2,dy2,col) in gem:
    gem_canvas.create_rectangle(gx+dx1*s, gy+dy1*s, gx+dx2*s, gy+dy2*s, fill=col, outline="")
gem_canvas.create_rectangle(gx-28, gy+2, gx-22, gy+8, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx-20, gy+2, gx-14, gy+8, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx-32, gy+8, gx-12, gy+14, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx-30, gy+14, gx-16, gy+18, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx-26, gy+18, gx-18, gy+22, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx+14, gy+2, gx+20, gy+8, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx+22, gy+2, gx+28, gy+8, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx+12, gy+8, gx+32, gy+14, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx+16, gy+14, gx+30, gy+18, fill="#F472B6", outline="")
gem_canvas.create_rectangle(gx+18, gy+18, gx+26, gy+22, fill="#F472B6", outline="")

screen_border = tk.Frame(calc, bg=SCREEN_FG2, bd=0, padx=2, pady=2)
screen_border.pack(padx=12, pady=(4,6))

screen_inner = tk.Frame(screen_border, bg=SCREEN_BG, bd=0)
screen_inner.pack()

screen_px_top = tk.Frame(screen_inner, bg="#4B2080", height=4)
screen_px_top.pack(fill="x")

expr_label = tk.Label(screen_inner, textvariable=expr_var, bg=SCREEN_BG, fg=SCREEN_FG2,
                       font=PIXEL_FONT_SMALL, anchor="e", padx=10, pady=2, width=20)
expr_label.pack(fill="x")

result_label = tk.Label(screen_inner, textvariable=result_var, bg=SCREEN_BG, fg=SCREEN_FG,
                         font=PIXEL_FONT_LARGE, anchor="e", padx=10, pady=6, width=14)
result_label.pack(fill="x")

screen_sparkle = tk.Canvas(screen_inner, width=40, height=10, bg=SCREEN_BG, highlightthickness=0)
screen_sparkle.pack(anchor="w", padx=8)
screen_sparkle.create_rectangle(0, 3, 4, 7, fill="#A855F7", outline="")
screen_sparkle.create_rectangle(6, 1, 10, 5, fill="#E879F9", outline="")
screen_sparkle.create_rectangle(14, 4, 18, 8, fill="#A855F7", outline="")

btn_area = tk.Frame(calc, bg=BODY, padx=10)
btn_area.pack()

row0 = tk.Frame(btn_area, bg=BODY)
row0.pack(pady=3)
for text, cmd, bg, fg, top in [
    ("AC",  clear,       BTN_AC_BG, BTN_AC_FG, BTN_AC_TOP),
    ("+/-", toggle_sign, BTN_NUM_BG, BTN_NUM_FG, BTN_NUM_TOP),
    ("%",   percent,     BTN_NUM_BG, BTN_NUM_FG, BTN_NUM_TOP),
    ("÷",  lambda: press("/"), BTN_OP_BG, BTN_OP_FG, BTN_OP_TOP),
]:
    f = pixel_button(row0, text, cmd, bg, fg, top, width=4)
    f.pack(side="left", padx=3)

for row_vals in [
    [("7","8","9","×")],
    [("4","5","6","−")],
    [("1","2","3","+")],
]:
    row_f = tk.Frame(btn_area, bg=BODY)
    row_f.pack(pady=3)
    nums = row_vals[0]
    for i, ch in enumerate(nums):
        if i < 3:
            cmd = lambda v=ch: press(v)
            f = pixel_button(row_f, ch, cmd, BTN_NUM_BG, BTN_NUM_FG, BTN_NUM_TOP, width=4)
        else:
            if ch == "×": cmd = lambda: press("*")
            elif ch == "−": cmd = lambda: press("-")
            elif ch == "+": cmd = lambda: press("+")
            f = pixel_button(row_f, ch, cmd, BTN_OP_BG, BTN_OP_FG, BTN_OP_TOP, width=4)
        f.pack(side="left", padx=3)

row_last = tk.Frame(btn_area, bg=BODY)
row_last.pack(pady=3)

zero_top = tk.Frame(row_last, bg=BODY, bd=0)
zero_top.pack(side="left", padx=3)
zero_topbar = tk.Frame(zero_top, bg=BTN_NUM_TOP, height=4)
zero_topbar.pack(fill="x")
zero_btn = tk.Button(zero_top, text="0", command=lambda: press("0"),
                      bg=BTN_NUM_BG, fg=BTN_NUM_FG, font=PIXEL_FONT,
                      width=9, height=1, relief="flat", bd=0,
                      activebackground=BTN_NUM_TOP, cursor="hand2")
zero_btn.pack()
zero_btmbar = tk.Frame(zero_top, bg=BORDER_DARK, height=3)
zero_btmbar.pack(fill="x")
zero_top.configure(highlightbackground=BTN_NUM_BORDER, highlightthickness=1)

f = pixel_button(row_last, ".", lambda: press("."), BTN_NUM_BG, BTN_NUM_FG, BTN_NUM_TOP, width=4)
f.pack(side="left", padx=3)

del_top = tk.Frame(btn_area, bg=BODY, bd=0)
del_top.pack(pady=3, fill="x", padx=3)
del_topbar = tk.Frame(del_top, bg=BTN_AC_TOP, height=4)
del_topbar.pack(fill="x")
del_btn = tk.Button(del_top, text="⌫  DEL", command=backspace,
                     bg=BTN_AC_BG, fg=BTN_AC_FG, font=PIXEL_FONT_SMALL,
                     relief="flat", bd=0, width=28,
                     activebackground=BTN_AC_TOP, cursor="hand2")
del_btn.pack(fill="x")
del_btmbar = tk.Frame(del_top, bg=BORDER_DARK, height=3)
del_btmbar.pack(fill="x")
del_top.configure(highlightbackground=BTN_NUM_BORDER, highlightthickness=1)

eq_top = tk.Frame(btn_area, bg=BODY, bd=0)
eq_top.pack(pady=3, fill="x", padx=3)
eq_topbar = tk.Frame(eq_top, bg=BTN_EQ_TOP, height=4)
eq_topbar.pack(fill="x")
eq_btn = tk.Button(eq_top, text="=", command=calculate,
                    bg=BTN_EQ_BG, fg=BTN_EQ_FG, font=("Courier", 18, "bold"),
                    relief="flat", bd=0, width=28,
                    activebackground=BTN_EQ_TOP, cursor="hand2")
eq_btn.pack(fill="x")
eq_btmbar = tk.Frame(eq_top, bg=BORDER_DARK, height=4)
eq_btmbar.pack(fill="x")
eq_top.configure(highlightbackground="#C026D3", highlightthickness=2)

bot_strip = tk.Frame(calc, bg=STRIP, height=14)
bot_strip.pack(fill="x", pady=(6,0))
bot_canvas = tk.Canvas(bot_strip, height=14, bg=STRIP, highlightthickness=0)
bot_canvas.pack(fill="x")
for xi in range(0, CALC_W, 8):
    bot_canvas.create_rectangle(xi, 4, xi+5, 10, fill="#F0ABFC", outline="")

deco_bot = tk.Canvas(outer, width=CALC_W+20, height=40, bg=BG, highlightthickness=0)
deco_bot.pack()
draw_pixel_heart(deco_bot, CALC_W//2-14, 6, "#F472B6", s=4)
for xi in [40, 90, 200, 250]:
    deco_bot.create_rectangle(xi, 14, xi+4, 18, fill=STAR, outline="")
    deco_bot.create_rectangle(xi+2, 10, xi+6, 14, fill="#C084FC", outline="")
    deco_bot.create_rectangle(xi+4, 14, xi+8, 18, fill=STAR, outline="")

root.mainloop()