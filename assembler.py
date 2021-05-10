from tkinter.filedialog import askopenfilename, asksaveasfile
from tkinter import Tk, Label, Button
from tkinter.messagebox import showerror
from Core import assemble, ver, AssembleSyntaxError
from os.path import exists
from traceback import format_exc


class AssemblerView(Tk):
    def __init__(self):
        super(AssemblerView, self).__init__()
        self.title(f"Assembler V{ver}")
        self.geometry("200x150")
        self.columnconfigure(1, weight=1, pad=10)
        Button(self, text="open file", command=self.open_file).grid(row=1,
                                                                    column=1)
        Label(self, text="FileName:").grid(row=2, column=1)
        self.file_name = Label(self, text="n/a")
        self.file_name.grid(row=3, column=1)
        self.active = False
        # self.ent_name = Entry(self, relief="solid", bd=1, width=20,
        #                       text="MyFile.mc")
        Button(self, text="Assemble", command=self.assemble).grid(row=4,
                                                                  column=1)

    def open_file(self):
        file_name = askopenfilename(title="choose a file to assemble",
                                    initialfile="/")
        if exists(file_name):
            self.file_name.config(text=file_name)
            self.active = True
        else:
            showerror("Error", "File Does not exist.")

    def assemble(self):
        if not self.active:
            showerror("Error", "Choose a File first.")
            return
        file_out = asksaveasfile(title="Save As", mode="wb")
        if not file_out:
            return
        # noinspection PyBroadException
        try:
            with open(self.file_name.cget("text")) as file:
                for text in assemble(file):
                    file_out.write(text)
                file.close()
        except AssembleSyntaxError as ex:
            showerror("Error At file", ex.__str__())
        except Exception:
            showerror("Exception Error", format_exc())


if __name__ == '__main__':
    win = AssemblerView()
    win.mainloop()
