import tkinter as tk
from tkinter import ttk, messagebox
from sympy import (
    symbols, parse_expr, diff, integrate, limit, series, Function,
    dsolve, Eq, latex
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sympy.printing.latex import LatexPrinter

class PrimeLatexPrinter(LatexPrinter):
    def _print_Derivative(self, expr):
        if len(expr.variables) == 1 and expr.variables.count(expr.variables[0]) == 1:
            func_latex = self._print(expr.expr)
            return func_latex + "'"
        else:
            return super()._print_Derivative(expr)

def prime_latex(expr):
    return PrimeLatexPrinter().doprint(expr)

x, y, z = symbols('x y z')
f = Function('f')

def safe_parse(expr_str):
    try:
        return parse_expr(expr_str, evaluate=True)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

def calculate_derivative(expr_str, var_str, order):
    expr = safe_parse(expr_str)
    var = symbols(var_str)
    return diff(expr, var, order)

def calculate_integral(expr_str, var_str, lower=None, upper=None):
    expr = safe_parse(expr_str)
    var = symbols(var_str)
    if lower is not None and upper is not None:
        lower = safe_parse(lower)
        upper = safe_parse(upper)
        return integrate(expr, (var, lower, upper))
    else:
        return integrate(expr, var)

def calculate_limit(expr_str, var_str, point_str, direction):
    expr = safe_parse(expr_str)
    var = symbols(var_str)
    point = safe_parse(point_str)
    dir_map = {'both': None, 'left': '-', 'right': '+'}
    return limit(expr, var, point, dir_map.get(direction))

def calculate_taylor(expr_str, var_str, point_str, order):
    expr = safe_parse(expr_str)
    var = symbols(var_str)
    point = safe_parse(point_str)
    order = int(order)
    return series(expr, var, point, order+1).removeO()

def solve_ode(ode_str, func_str):
    func = Function(func_str)
    ode_expr = safe_parse(ode_str)
    ode = Eq(ode_expr, 0)
    sol = dsolve(ode, func(x))
    return sol

def on_calculate():
    try:
        expr_str = entry_expr.get()
        var_str = entry_var.get()
        order = int(entry_order.get()) if entry_order.get() else 1
        lower = entry_lower.get().strip() or None
        upper = entry_upper.get().strip() or None
        point = entry_point.get().strip() or None
        direction = combo_direction.get()
        func_str = entry_func.get().strip() or 'f'
        ode_str = entry_ode.get().strip()

        derivative = calculate_derivative(expr_str, var_str, order)
        if lower and upper:
            integral = calculate_integral(expr_str, var_str, lower, upper)
        else:
            integral = calculate_integral(expr_str, var_str)
        if point:
            lim = calculate_limit(expr_str, var_str, point, direction)
        else:
            lim = None
        taylor = calculate_taylor(expr_str, var_str, point if point else '0', order)

        if ode_str:
            ode_solution = solve_ode(ode_str, func_str)
        else:
            ode_solution = None

        ax.clear()
        ax.axis('off')

        y_pos = 1.0
        line_spacing_title = 0.07
        line_spacing_expr = 0.15

        def draw_title(text):
            nonlocal y_pos
            ax.text(0, y_pos, text, fontsize=14, fontweight='bold', va='top', ha='left')
            y_pos -= line_spacing_title

        def draw_expr(latex_expr):
            nonlocal y_pos
            ax.text(0.02, y_pos, f"${latex_expr}$", fontsize=14, va='top', ha='left')
            y_pos -= line_spacing_expr

        draw_title(f"Derivative (order {order}):")
        draw_expr(prime_latex(derivative))

        draw_title("Integral:")
        draw_expr(prime_latex(integral))

        draw_title("Limit:")
        if lim is not None:
            draw_expr(prime_latex(lim))
        else:
            draw_expr("N/A")

        draw_title(f"Taylor Series (order {order}):")
        draw_expr(prime_latex(taylor))

        draw_title("ODE Solution:")
        if ode_solution is not None:
            draw_expr(prime_latex(ode_solution))
        else:
            draw_expr("N/A")

        canvas.draw()

    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("calc calc")

frame = ttk.Frame(root, padding=20)
frame.grid()

ttk.Label(frame, text="Expression (in terms of variable):").grid(column=0, row=0, sticky="w")
entry_expr = ttk.Entry(frame, width=50)
entry_expr.grid(column=1, row=0, pady=5)

ttk.Label(frame, text="Variable:").grid(column=0, row=1, sticky="w")
entry_var = ttk.Entry(frame, width=10)
entry_var.grid(column=1, row=1, sticky="w", pady=5)
entry_var.insert(0, 'x')

ttk.Label(frame, text="Derivative order:").grid(column=0, row=2, sticky="w")
entry_order = ttk.Entry(frame, width=10)
entry_order.grid(column=1, row=2, sticky="w", pady=5)
entry_order.insert(0, '1')

ttk.Label(frame, text="Integral lower bound (optional):").grid(column=0, row=3, sticky="w")
entry_lower = ttk.Entry(frame, width=10)
entry_lower.grid(column=1, row=3, sticky="w", pady=5)

ttk.Label(frame, text="Integral upper bound (optional):").grid(column=0, row=4, sticky="w")
entry_upper = ttk.Entry(frame, width=10)
entry_upper.grid(column=1, row=4, sticky="w", pady=5)

ttk.Label(frame, text="Limit point (optional):").grid(column=0, row=5, sticky="w")
entry_point = ttk.Entry(frame, width=10)
entry_point.grid(column=1, row=5, sticky="w", pady=5)

ttk.Label(frame, text="Limit direction:").grid(column=0, row=6, sticky="w")
combo_direction = ttk.Combobox(frame, values=["both", "left", "right"], width=7)
combo_direction.grid(column=1, row=6, sticky="w", pady=5)
combo_direction.current(0)

ttk.Label(frame, text="ODE to solve (optional):").grid(column=0, row=7, sticky="w")
entry_ode = ttk.Entry(frame, width=50)
entry_ode.grid(column=1, row=7, pady=5)

ttk.Label(frame, text="Function name for ODE (default f):").grid(column=0, row=8, sticky="w")
entry_func = ttk.Entry(frame, width=10)
entry_func.grid(column=1, row=8, sticky="w", pady=5)
entry_func.insert(0, 'f')

btn_calculate = ttk.Button(frame, text="Calculate", command=on_calculate)
btn_calculate.grid(column=0, row=9, columnspan=2, pady=10)

fig, ax = plt.subplots(figsize=(6, 6))
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.get_tk_widget().grid(column=2, row=0, rowspan=15, padx=10)

root.mainloop()