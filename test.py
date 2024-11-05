import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
root.title('cuteluluWindow')
root.configure(bg="#7AFEC6")
root.iconbitmap('heart_green.ico')
root.geometry('500x200')

tree=ttk.Treeview(root,columns=("節日"))
tree.heading("#0",text="節日")
tree.heading("#1",text="日期")

tree.insert("",index="end",text="國慶日",values="10/10")
tree.insert("",index="end",text="聖誕節",values="12/25")
tree.insert("",index="end",text="元旦",values="1/1")
tree.insert("",index="end",text="愚人節",values="4/1")
tree.insert("",index="end",text="兒童節",values="4/4")

tree.pack()
root.mainloop()