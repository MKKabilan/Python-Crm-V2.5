import tkinter as tk
from tkinter import ttk,messagebox,filedialog
import sqlite3
from tkcalendar import DateEntry,Calendar
from openpyxl import Workbook,load_workbook
from datetime import datetime
import matplotlib.pyplot as plt

# ---------------- LOGIN ---------------- #

def login():

    login_win=tk.Tk()
    login_win.title("CRM Login")
    login_win.geometry("300x180")
    login_win.resizable(False,False)

    tk.Label(login_win,text="Username").pack(pady=5)
    user=ttk.Entry(login_win)
    user.pack()

    tk.Label(login_win,text="Password").pack(pady=5)
    pwd=ttk.Entry(login_win,show="*")
    pwd.pack()

    def check():
        if user.get()=="admin" and pwd.get()=="admin1234":
            login_win.destroy()
        else:
            messagebox.showerror("Login Failed","Invalid Login")

    ttk.Button(login_win,text="Login",command=check).pack(pady=15)

    login_win.mainloop()

login()

# ---------------- DATABASE ---------------- #

conn=sqlite3.connect("crm_v2_5.db")
cursor=conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS clients(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
company TEXT,
phone TEXT,
service TEXT,
price REAL,
paid REAL,
remaining REAL,
status TEXT,
reference TEXT,
date TEXT,
notes TEXT,
next_followup TEXT,
followup_service TEXT,
followup_notes TEXT
)
""")

conn.commit()

# ---------------- FUNCTIONS ---------------- #

def calculate_remaining(event=None):

    try:
        price=float(price_entry.get())
    except:
        price=0

    try:
        paid=float(paid_entry.get())
    except:
        paid=0

    remaining=price-paid
    remaining_var.set(str(remaining))

# ---------------- ADD CLIENT ---------------- #

def add_client():

    if client_entry.get()=="":
        messagebox.showwarning("Warning","Client name required")
        return
    data=(
    client_entry.get(),
    company_entry.get(),
    phone_entry.get(),
    service_entry.get(),
float(price_entry.get() or 0),
float(paid_entry.get() or 0),
float(remaining_var.get() or 0),
    status_combo.get(),
    reference_entry.get(),
    date_entry.get_date().strftime("%Y-%m-%d"),
    notes_entry.get(),
    followup_date.get_date().strftime("%Y-%m-%d") if followup_service.get() else None,
    followup_service.get(),
    followup_notes.get()
    )

    cursor.execute("""
    INSERT INTO clients
    (name,company,phone,service,price,paid,remaining,status,reference,date,notes,next_followup,followup_service,followup_notes)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """,data)

    conn.commit()

    load_data()
    update_dashboard()
    clear_fields()

# ---------------- UPDATE CLIENT ---------------- #

def update_client():

    selected=table.focus()
    values=table.item(selected,"values")

    if not values:
        return

    row_id=values[0]

    cursor.execute("""
    UPDATE clients
    SET name=?,company=?,phone=?,service=?,price=?,paid=?,remaining=?,status=?,reference=?,date=?,notes=?,next_followup=?,followup_service=?,followup_notes=?
    WHERE id=?
    """,(client_entry.get(),company_entry.get(),phone_entry.get(),
    service_entry.get(),price_entry.get(),paid_entry.get(),
    remaining_var.get(),status_combo.get(),reference_entry.get(),
    date_entry.get_date().strftime("%Y-%m-%d"),notes_entry.get(),
    followup_date.get_date().strftime("%Y-%m-%d") if followup_service.get() else None,followup_service.get(),
    followup_notes.get(),row_id))

    conn.commit()

    load_data()
    update_dashboard()
    clear_fields()

# ---------------- DELETE ---------------- #

def delete_client():

    selected=table.focus()
    values=table.item(selected,"values")

    if not values:
        return

    confirm=messagebox.askyesno("Delete","Delete this client?")

    if confirm:
        cursor.execute("DELETE FROM clients WHERE id=?",(values[0],))
        conn.commit()

    load_data()
    update_dashboard()

# ---------------- LOAD DATA ---------------- #

def load_data():

    for row in table.get_children():
        table.delete(row)

    cursor.execute("SELECT * FROM clients ORDER BY id DESC")
    rows=cursor.fetchall()

    for r in rows:

        try:
            if float(r[7])>0:
                table.insert("",tk.END,values=r,tags=("pending",))
            else:
                table.insert("",tk.END,values=r)
        except:
            table.insert("",tk.END,values=r)

    table.tag_configure("pending",background="#ffe6e6")

# ---------------- SELECT ROW ---------------- #

def select_row(event):

    selected=table.focus()
    values=table.item(selected,"values")

    if not values:
        return

    client_entry.delete(0,tk.END)
    client_entry.insert(0,values[1])

    company_entry.delete(0,tk.END)
    company_entry.insert(0,values[2])

    phone_entry.delete(0,tk.END)
    phone_entry.insert(0,values[3])

    service_entry.set(values[4])

    price_entry.delete(0,tk.END)
    price_entry.insert(0,values[5])

    paid_entry.delete(0,tk.END)
    paid_entry.insert(0,values[6])

    remaining_var.set(values[7])

    status_combo.set(values[8])
    reference_entry.set(values[9])

    try:
        if values[10]:
           date_entry.set_date(values[10])
    except:
        pass

    notes_entry.delete(0,tk.END)
    notes_entry.insert(0,values[11])
    try:
        if values[12]:
            followup_date.set_date(values[12])
    except:
        pass

    followup_service.set(values[13])

    followup_notes.delete(0,tk.END)
    followup_notes.insert(0,values[14])

# ---------------- CLEAR ---------------- #

def clear_fields():

    client_entry.delete(0,tk.END)
    company_entry.delete(0,tk.END)
    phone_entry.delete(0,tk.END)
    service_entry.set("")
    price_entry.delete(0,tk.END)
    paid_entry.delete(0,tk.END)
    remaining_var.set("")
    status_combo.set("Lead")
    reference_entry.set("")
    notes_entry.delete(0,tk.END)
    followup_service.set("")
    followup_notes.delete(0,tk.END)

# ---------------- SEARCH ---------------- #

def search_client(event=None):

    keyword=search_entry.get()

    for row in table.get_children():
        table.delete(row)

    cursor.execute("""
    SELECT * FROM clients
    WHERE name LIKE ?
    OR phone LIKE ?
    OR service LIKE ?
    """,('%'+keyword+'%','%'+keyword+'%','%'+keyword+'%'))

    rows=cursor.fetchall()

    for r in rows:
        table.insert("",tk.END,values=r)

# ---------------- DASHBOARD ---------------- #

def update_dashboard():

    cursor.execute("SELECT COUNT(*) FROM clients")
    clients_var.set(cursor.fetchone()[0])

    cursor.execute("SELECT SUM(price) FROM clients")
    revenue_var.set(cursor.fetchone()[0] or 0)

    cursor.execute("SELECT SUM(paid) FROM clients")
    paid_var.set(cursor.fetchone()[0] or 0)

    cursor.execute("SELECT SUM(remaining) FROM clients")
    pending_var.set(cursor.fetchone()[0] or 0)

# ---------------- SMART FOLLOWUP NOTIFICATION ---------------- #

def check_followups():

    today=datetime.today().strftime("%Y-%m-%d")

    cursor.execute("""
    SELECT name,followup_service,next_followup 
    FROM clients 
    WHERE next_followup IS NOT NULL
    AND next_followup <= ?
    """,(today,))

    rows=cursor.fetchall()

    if rows:

        text="Follow-up Alerts\n\n"

        for r in rows:
            text+=f"{r[0]} → {r[1]} ({r[2]})\n"

        messagebox.showinfo("Follow-ups",text)

# ---------------- FOLLOWUP CALENDAR ---------------- #

def followup_calendar():

    win=tk.Toplevel(root)
    win.title("Follow-up Calendar")

    cal=Calendar(win,date_pattern="yyyy-mm-dd")
    cal.pack(pady=10)

    def show_followups():

        selected=cal.get_date()

        cursor.execute("""
        SELECT name,followup_service
        FROM clients
        WHERE next_followup IS NOT NULL
        AND next_followup=?
        """,(selected,))

        rows=cursor.fetchall()

        text=""

        for r in rows:
            text+=f"{r[0]} → {r[1]}\n"

        if text=="":
            text="No follow-ups"

        messagebox.showinfo(selected,text)

    ttk.Button(win,text="View Followups",command=show_followups).pack(pady=10)

# ---------------- SERVICE PERFORMANCE ---------------- #

def service_dashboard():

    cursor.execute("SELECT service,COUNT(*),SUM(price) FROM clients GROUP BY service")
    rows=cursor.fetchall()

    if not rows:
        messagebox.showinfo("No Data","No service data available")
        return

    services=[r[0] for r in rows]
    revenue=[r[2] for r in rows]

    plt.figure(figsize=(8,5))
    plt.bar(services,revenue)
    plt.title("Service Revenue Performance")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# ---------------- EXPORT ---------------- #

def export_excel():

    wb=Workbook()
    ws=wb.active

    ws.append(["Name","Company","Phone","Service","Price","Paid","Remaining","Status","Reference","Date","Notes","Next Followup","Follow Service","Follow Notes"])

    cursor.execute("SELECT name,company,phone,service,price,paid,remaining,status,reference,date,notes,next_followup,followup_service,followup_notes FROM clients")
    rows=cursor.fetchall()

    for r in rows:
        ws.append(r)

    wb.save("crm_export.xlsx")

    messagebox.showinfo("Export","Excel Exported")

# ---------------- UI ---------------- #

root=tk.Tk()
root.title("Professional CRM v2.5")
root.geometry("1400x750")

# Dashboard

dash=tk.Frame(root)
dash.pack(fill="x")

clients_var=tk.StringVar()
revenue_var=tk.StringVar()
paid_var=tk.StringVar()
pending_var=tk.StringVar()

def dash_box(title,var):

    frame=tk.Frame(dash,bd=1,relief="solid")
    frame.pack(side="left",padx=10,pady=10)

    tk.Label(frame,text=title).pack(padx=20)
    tk.Label(frame,textvariable=var,font=("Arial",16,"bold")).pack()

dash_box("Clients",clients_var)
dash_box("Revenue",revenue_var)
dash_box("Paid",paid_var)
dash_box("Pending",pending_var)

# FORM

form=tk.Frame(root)
form.pack(pady=10)

client_entry=ttk.Entry(form)
client_entry.focus()

company_entry=ttk.Entry(form)
phone_entry=ttk.Entry(form)

service_entry=ttk.Combobox(form,values=["GST Filing","IT Return","Company Registration","MSME Registration","Trademark","Digital Signature","PAN Card","Other"])

price_entry=ttk.Entry(form)
price_entry.bind("<KeyRelease>",calculate_remaining)

paid_entry=ttk.Entry(form)
paid_entry.bind("<KeyRelease>",calculate_remaining)

remaining_var=tk.StringVar()
remaining_entry=ttk.Entry(form,textvariable=remaining_var,state="readonly")

status_combo=ttk.Combobox(form,values=["Lead","Follow Up","Ongoing","Completed","Cancelled"])
status_combo.set("Lead")

reference_entry=ttk.Combobox(form)

date_entry=DateEntry(form,date_pattern="yyyy-mm-dd")

notes_entry=ttk.Entry(form,width=50)

followup_date=DateEntry(form,date_pattern="yyyy-mm-dd")

followup_service=ttk.Combobox(form,values=["GST Filing","IT Return","Company Registration","MSME Registration","Trademark","Digital Signature","PAN Card","Other"])

followup_notes=ttk.Entry(form,width=50)

labels=["Client","Company","Phone","Service","Price","Paid","Remaining","Status","Reference","Date","Notes","Next Follow-up","Follow Service","Follow Notes"]

entries=[client_entry,company_entry,phone_entry,service_entry,price_entry,paid_entry,remaining_entry,status_combo,reference_entry,date_entry,notes_entry,followup_date,followup_service,followup_notes]

for i,(l,e) in enumerate(zip(labels,entries)):
    tk.Label(form,text=l).grid(row=i//2,column=(i%2)*2)
    e.grid(row=i//2,column=(i%2)*2+1,padx=10,pady=5)

# BUTTONS

btn=tk.Frame(root)
btn.pack()

ttk.Button(btn,text="Add",command=add_client).grid(row=0,column=0,padx=10)
ttk.Button(btn,text="Update",command=update_client).grid(row=0,column=1,padx=10)
ttk.Button(btn,text="Delete",command=delete_client).grid(row=0,column=2,padx=10)
ttk.Button(btn,text="Clear",command=clear_fields).grid(row=0,column=3,padx=10)
ttk.Button(btn,text="Export Excel",command=export_excel).grid(row=0,column=4,padx=10)
ttk.Button(btn,text="Followup Calendar",command=followup_calendar).grid(row=0,column=5,padx=10)
ttk.Button(btn,text="Service Dashboard",command=service_dashboard).grid(row=0,column=6,padx=10)

# SEARCH

search_frame=tk.Frame(root)
search_frame.pack(pady=10)

tk.Label(search_frame,text="Search").pack(side="left")
search_entry=ttk.Entry(search_frame,width=40)
search_entry.pack(side="left",padx=5)
search_entry.bind("<KeyRelease>",search_client)

# TABLE

columns=("ID","Name","Company","Phone","Service","Price","Paid","Remaining","Status","Reference","Date","Notes","Next Followup","Follow Service","Follow Notes")

table_frame=tk.Frame(root)
table_frame.pack(fill="both",expand=True)

y_scroll=ttk.Scrollbar(table_frame,orient="vertical")
y_scroll.pack(side="right",fill="y")

x_scroll=ttk.Scrollbar(table_frame,orient="horizontal")
x_scroll.pack(side="bottom",fill="x")

table=ttk.Treeview(table_frame,columns=columns,show="headings",yscrollcommand=y_scroll.set,xscrollcommand=x_scroll.set)

table.pack(fill="both",expand=True)

y_scroll.config(command=table.yview)
x_scroll.config(command=table.xview)

for col in columns:
    table.heading(col,text=col)
    table.column(col,width=140)

table.bind("<Double-1>",select_row)

load_data()
update_dashboard()
check_followups()

root.mainloop()