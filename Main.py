import tkinter as tk
import clingo

from tkinter import ttk
from tkinter.constants import LEFT, RIGHT, SEPARATOR

window = tk.Tk()

grid_frame = tk.Frame()

main_lab = tk.Label(master=window, text='ASP Tenner Grid Solver')
main_lab.pack()

init_vals = {}

"""
Initializes a dictionary of empty strings on first start
"""
def create_initial_vals(n,m, vals):
    for i in range(m):
        for j in range(n):
            vals[f'{j + 1},{i + 1}'] = ''
    return vals

"""
Creates GUI grid component for visualizing solutions
"""
def create_grid(n, m, vals):
    for i in range(m):
        for j in range(n):
            frame = tk.Frame(
                master=grid_frame,
                relief=tk.RAISED,
                borderwidth=1
            )
            frame.grid(row=i, column=j)
            label = tk.Label(master=frame, text=vals[f"{j + 1},{i + 1}"], width=3)
            label.pack()

entries = []

"""
Creates the user input row
"""
def create_input_row(n):
    for i in range(n):
        frame = tk.Frame(
            master=grid_frame,
            relief=tk.RAISED,
            borderwidth=1
        )
        frame.grid(row=n + 1, column=i)
        entry = tk.Entry(master=frame, width=4)
        entry.pack()
        entries.append(entry)

"""
Start up initialization
"""
init_vals = create_initial_vals(10, 2, init_vals)
create_grid(10, 2, init_vals)
create_input_row(10)

grid_frame.pack()

seperator = ttk.Separator(window, orient='horizontal')
seperator.pack(fill='x')

controls = tk.Frame()
run = tk.Button(master=controls, text='Run', command=lambda: run())

run.pack(side=LEFT)

controls.pack()

"""
On the creation of a successful model, the model is passed into this function
where the strings are split into component parts and reassembled into a dictionary
with X,Y coordinates as the key and the solution number as the value.
"""
def on_model(m):
    m = str(m).replace('sol(', '').replace(')', ' ')
    sol_list = m.split(' ')
    sol_list = [x.split(',') for x in sol_list if x]
    sol_list = [[','.join(x[:2]), '2'.join(x[2:])] for x in sol_list]
    vals = {key: value for (key, value) in sol_list}
    create_grid(10, 2, vals)
"""
Grabs the user inputs (which are the totals to be summed) and creates the sums
in the form of sum(X,Y,N), which are just concatenated together and later interpolated
into the ASP program. 
"""
def create_sums():
    sums = ''
    x_index = 1
    for entry in entries:
        sums += f'sum({x_index},3,{entry.get()}). '
        x_index += 1
    return sums

"""
Runs the clingo program which has the sums interoplated into it.
"""
def run():
    ctl = clingo.Control()
    sums = create_sums()
    ctl.add("base", [], f"""
    n(0..9).
    x(1..10).
    y(1..2).

    {sums}

    % Here are the rules as outlined by https://www.mathinenglish.com/puzzlestenner.php

    % You can only have one number from 1 to n
    {{sol(X,Y,N):n(N)}}=1 :- x(X), y(Y).
    % Numbers can only appear once in a row (though they can be repeated in a column)
    :- sol(X,Y,N), sol(A,Y,N), X != A.
    % Numbers in the columns must add up to the given sums
    :- sol(X,Y,N), sol(X,Y+1,O), sum(X,3,Q), not N+O==Q.
    % Numbers in the connecting cells must be different (including diagonally)
    :- sol(X,Y,N), sol(X-1,Y,O), not N!=O.
    :- sol(X,Y,N), sol(X+1,Y,O), not N!=O.
    :- sol(X,Y,N), sol(X,Y-1,O), not N!=O.
    :- sol(X,Y,N), sol(X,Y+1,O), not N!=O.
    :- sol(X,Y,N), sol(X-1,Y-1,O), not N!=O.
    :- sol(X,Y,N), sol(X+1,Y+1,O), not N!=O.
    :- sol(X,Y,N), sol(X-1,Y+1,O), not N!=O.
    :- sol(X,Y,N), sol(X+1,Y+1,O), not N!=O.

    #show sol/3. 

    """)
    ctl.ground([("base", [])])
    ctl.solve(on_model=on_model)

window.mainloop()