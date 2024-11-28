import os
import shutil
import csv
from tkinter import Tk, Label, Button, messagebox, filedialog, Toplevel, StringVar, OptionMenu

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz App")
        self.root.minsize(1100, 500)
        self.root.maxsize(1100, 0)
        self.root.config(bg="gray17")
        self.root.resizable(False, False)

        #folder for quizzes
        self.quiz_folder = "./quizzes"
        if not os.path.exists(self.quiz_folder):
            os.makedirs(self.quiz_folder)

        #variables for the quiz
        self.fragen = []
        self.current_question = 0
        self.correct_answer = ""
        self.correct_count = 0

        #start
        self.show_start_page()

    def load_questions(self, filename):
        self.fragen.clear()
        try:
            with open(filename, "r", encoding='utf-8') as data:
                reader = csv.reader(data, delimiter=';')
                for zeile in reader:
                    self.fragen.append(zeile)
        except FileNotFoundError:
            messagebox.showerror("Error", f"Data {filename} not found.")
        self.current_question = 0
        self.correct_count = 0

    def show_start_page(self):
        self.clear_window()

        label = Label(self.root, text="Choose a quiz from the list or upload a new one:", font=("Arial", 25, 'bold'), fg='azure', bg='gray17')
        label.pack(pady=20, padx=40)

        self.load_custom_quizzes()

        #upload button bottom right
        upload_button = Button(self.root, text="Upload quiz", bg="goldenrod1", command=self.upload_csv,font=('Arial',12,'bold'))
        upload_button.place(relx=0.95, rely=0.9, anchor="e")

        #delete button bottom left
        remove_button = Button(self.root, text="Delete quiz", bg="firebrick1", command=self.remove_csv,font=('Arial',12,'bold'))
        remove_button.place(relx=0.05, rely=0.9, anchor="w")

    def upload_csv(self):
        filepath = filedialog.askopenfilename(
            title="Select CSV-data",
            filetypes=(("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*"))
        )
        if filepath:
            original_filename = os.path.basename(filepath)
            button_text = original_filename.replace(".csv", "")

            destination = os.path.join(self.quiz_folder, original_filename)
            try:
                shutil.copy(filepath, destination)
                messagebox.showinfo("Success", f"Quiz '{original_filename}' successfully uploaded.")
                self.create_quiz_button(button_text, destination)
            except Exception as e:
                messagebox.showerror("Error", f"Quiz not uploaded: {e}")

    def load_custom_quizzes(self):
        for file in os.listdir(self.quiz_folder):
            if file.endswith(".csv"):
                filepath = os.path.join(self.quiz_folder, file)
                button_text = file.replace(".csv", "")
                self.create_quiz_button(button_text, filepath)

    def create_quiz_button(self, button_text, filepath):
        new_button = Button(self.root, text=button_text, bg="purple", fg="white", command=lambda: self.start_quiz(filepath), width=30, font=('Arial',10,'bold'))
        new_button.pack(pady=5)

    def remove_csv(self):
        files = [file for file in os.listdir(self.quiz_folder) if file.endswith(".csv")]
        if not files:
            messagebox.showinfo("INFO", "No data available.")
            return

        remove_window = Toplevel(self.root)
        remove_window.title("Delete a quizz")
        remove_window.geometry("300x200")

        label = Label(remove_window, text="Choose a quiz from the list:", font=("Arial", 14))
        label.pack(pady=10)

        selected_file = StringVar(value='Quizz list')
        dropdown = OptionMenu(remove_window, selected_file, *files)
        dropdown.pack(pady=10)

        def confirm_removal():
            file_to_remove = selected_file.get()
            confirm = messagebox.askyesno(
                "Confirm",
                f"Are you sure you want to delete: '{file_to_remove}'?"
            )
            if confirm:
                try:
                    os.remove(os.path.join(self.quiz_folder, file_to_remove))
                    messagebox.showinfo("Success", f"Quizz '{file_to_remove}' successfully deleted.")
                    remove_window.destroy()
                    self.show_start_page()
                except Exception as e:
                    messagebox.showerror("Error", f"Quizz is not deleted: {e}")

        confirm_button = Button(remove_window, text="Delete", bg="red", command=confirm_removal)
        confirm_button.pack(side="left", padx=20, pady=10)

        cancel_button = Button(remove_window, text="Cancel", bg="gray", command=remove_window.destroy)
        cancel_button.pack(side="right", padx=20, pady=10)

    def start_quiz(self, filename):
        self.load_questions(filename)
        if self.fragen:
            self.show_question_page()

    def show_question_page(self):
        self.clear_window()
        if self.current_question < len(self.fragen):
            frage_data = self.fragen[self.current_question]
            self.correct_answer = frage_data[5]

            frage_label = Label(self.root, text=self.wrap_text(frage_data[0], 75), font=("Arial", 20, 'bold'), anchor="w",justify='left', bg="RoyalBlue1", fg='white')
            frage_label.pack(pady=40, anchor='w', padx=50, ipady=10,fill="x")
            
            self.answer_buttons = []
            for i in range(1, 5):
                answer_text = frage_data[i].strip()
                if answer_text:
                    answer_button = Button(self.root, text=self.wrap_text(answer_text, 70), command=lambda x=answer_text: self.check_answer(x), font=("Arial", 20, 'bold'), anchor="w",
                    bg="ghost white",fg='SteelBlue4', justify='left', width=60)
                    answer_button.pack(pady=10, padx=50)
                    self.answer_buttons.append(answer_button)

            next_button = Button(self.root, text="NEXT", bg="dodger blue", fg="white", command=self.next_question, font='bold')
            next_button.pack(anchor='e', padx=50, pady=5, ipady=5)

            total_questions = len(self.fragen)

            number_Label = Label(self.root,text=f"{self.current_question+1}/{total_questions}", bg='gray17', fg='white', font=('Arial', 10))
            number_Label.pack(side='bottom', pady=12)

        else:
            self.show_result()

    def wrap_text(self, text, line_length):
        words = text.split()
        wrapped_text = ""
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= line_length:
                current_line += (word + " ")
            else:
                wrapped_text += (current_line.strip() + "\n")
                current_line = word + " "

        wrapped_text += current_line.strip()
        return wrapped_text

    def check_answer(self, answer):
        if answer == self.correct_answer:
            self.correct_count += 1

        for button in self.answer_buttons:
            if button["text"] == answer:
                if answer == self.correct_answer:
                    button.configure(bg="lime green")
                else:
                    button.configure(bg="firebrick1")
            if button["text"] == self.correct_answer:
                button.configure(bg="lime green")

        for b in self.answer_buttons:
            b.configure(state="disabled")

    def next_question(self):
        self.current_question += 1
        if self.current_question < len(self.fragen):
            self.show_question_page()
        else:
            self.show_result()

    def show_result(self):
        self.clear_window()

        total_questions = len(self.fragen)
        result_text = f"You answered {self.correct_count} out of {total_questions} questions correctly!"
        result_score = round(self.correct_count/total_questions*100, 1)

        result_label = Label(self.root, text=result_text, font=("Arial", 35,'bold'), fg="azure", bg='gray17')
        result_label.pack(pady=40, padx=20)

        score_lable = Label(self.root, text=f"Score: {result_score} %", font=('Arial',50,'bold'), fg='light cyan' ,bg='gray17')
        score_lable.pack(pady=10)

        # restart button on score page
        restart_button = Button(self.root, text="Try Again!", bg="dodger blue", fg="white", command=self.show_start_page, font=('Arial', 20))
        restart_button.pack(pady=20)

        # exit button on score page
        exit_button = Button(self.root, text="EXIT",font=('Arial', 15), bg="brown1", fg="white", command=self.root.quit)
        exit_button.pack(pady=10)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = Tk()
    app = QuizApp(root)
    root.mainloop()
