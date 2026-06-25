import tkinter as tk
from tkinter import messagebox

# Function to load tasks from the file
def load_tasks():
    try:
        with open("tasks.txt", "r") as file:
            lines = file.readlines()
            for line in lines:
                listbox_task.insert(tk.END, line.strip())
    except FileNotFoundError:
        pass  # If the file does not exist, just continue without loading

# Function to save tasks to a file
def save_tasks():
    with open("tasks.txt", "w") as file:
        tasks = listbox_task.get(0, tk.END)
        for task in tasks:
            file.write(task + "\n")

# Function to add a new task
def entertask():
    input_text = ""
    def add():
        input_text = entry_task.get(1.0, "end-1c")
        if input_text == "":
            messagebox.showwarning(title="Warning!", message="Please Enter some Text")
        else:
            listbox_task.insert(tk.END, input_text)
            # Close the window after adding the task
            root1.destroy()
            save_tasks()  # Save tasks to the file after adding a new one

    # Creating a new window to enter a task
    root1 = tk.Tk()
    root1.title("Add Task")
    entry_task = tk.Text(root1, width=40, height=4)
    entry_task.pack(padx=10, pady=10)
    button_temp = tk.Button(root1, text="Add Task", command=add)
    button_temp.pack(pady=10)
    root1.mainloop()

# Function to delete a selected task
def deletetask():
    try:
        selected = listbox_task.curselection()
        listbox_task.delete(selected[0])
        save_tasks()  # Save tasks after deletion
    except IndexError:
        messagebox.showwarning(title="Warning!", message="Please select a task to delete")

# Function to mark a task as completed
def markcompleted():
    try:
        marked = listbox_task.curselection()
        temp = marked[0]
        temp_marked = listbox_task.get(marked) + " ✔"
        listbox_task.delete(temp)
        listbox_task.insert(temp, temp_marked)
        save_tasks()  # Save tasks after marking as completed
    except IndexError:
        messagebox.showwarning(title="Warning!", message="Please select a task to mark as completed")

# Creating the main window
window = tk.Tk()
window.title("Python To-Do List App")
window.configure(bg="lightgrey")
window.geometry("500x600")  # Set size of the window

# Frame to hold the listbox and scrollbar
frame_task = tk.Frame(window, bg="lightgrey")
frame_task.pack(pady=20)

# Listbox to hold tasks
listbox_task = tk.Listbox(frame_task, bg="black", fg="white", height=15, width=40, font="Helvetica", selectmode=tk.SINGLE)
listbox_task.pack(side=tk.LEFT, padx=10)

# Scrollbar for the listbox
scrollbar_task = tk.Scrollbar(frame_task, orient=tk.VERTICAL, command=listbox_task.yview)
scrollbar_task.pack(side=tk.RIGHT, fill=tk.Y)
listbox_task.config(yscrollcommand=scrollbar_task.set)
scrollbar_task.config(command=listbox_task.yview)

# Buttons
button_add = tk.Button(window, text="Add Task", width=50, bg="blue", fg="white", font=("Helvetica", 12), command=entertask)
button_add.pack(pady=10)

button_delete = tk.Button(window, text="Delete Selected Task", width=50, bg="red", fg="white", font=("Helvetica", 12), command=deletetask)
button_delete.pack(pady=10)

button_mark = tk.Button(window, text="Mark as Completed", width=50, bg="green", fg="white", font=("Helvetica", 12), command=markcompleted)
button_mark.pack(pady=10)

# Load tasks on startup
load_tasks()

# Close the window and save tasks
window.protocol("WM_DELETE_WINDOW", lambda: [save_tasks(), window.destroy()])

# Run the Tkinter event loop
window.mainloop()
