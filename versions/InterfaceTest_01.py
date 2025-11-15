import tkinter as tk

win_Main = tk.Tk()

win_Main.geometry("500x500")
win_Main.title("CocatenM8er")

label=tk.Label(win_Main, text="CocatenM8er", font=('Arial',20))
label.pack(padx=20, pady=20)

textbox=tk.Text(win_Main, height=1, font=('Arial',16))
textbox.pack(padx=10, pady=10) 


btn_Exit = tk.Button(win_Main, text="Exit", font=('Arial',20))
btn_Exit.pack(padx=10, pady=10)

btn_Select = tk.Button(win_Main, text="Select Wavs", font=('Arial',20))
btn_Select.pack(padx=10, pady=10)




win_Main.mainloop()

