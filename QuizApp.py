import flet as ft
import os
import csv
import shutil

class QuizApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Quiz App"
        self.page.horizontal_alignment = 'CENTER'
        self.quiz_folder = "./quizzes"
        if not os.path.exists(self.quiz_folder):
            os.makedirs(self.quiz_folder)

        self.fragen = []
        self.current_question = 0
        self.correct_answer = ""
        self.correct_count = 0
        self.quiz_buttons = []
        
        self.show_startpage()


    def show_startpage(self):
        self.page.controls.clear()  # Entferne alte Elemente
        self.quiz_buttons.clear()

        header = ft.Container(
                ft.Text(
                    'Quizz Wählen', 
                    size=40, 
                ),
                padding=ft.padding.only(top=15, bottom=30)
            )

        self.load_custom_quizzes()
        
        self.page.controls.append(header)
        self.page.controls.extend(self.quiz_buttons)

        buttons = ft.Container(
            ft.Row(
                controls=[
                    ft.ElevatedButton(
                        'delete', 
                        on_click=self.remove_csv,
                        height=50, 
                        width=100,
                        bgcolor='red'
                    ),
                    ft.ElevatedButton(
                        'upload',
                        on_click=self.upload_csv,
                        height=50, 
                        width=100,
                        bgcolor='green'
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=100,
            padding=ft.padding.only(top=30, bottom=15, left=20, right=20)
        )
        self.page.controls.append(buttons)
        self.page.update()

    def load_custom_quizzes(self):
        self.quiz_buttons.clear()
        for file in os.listdir(self.quiz_folder):
            if file.endswith(".csv"):
                filepath = os.path.join(self.quiz_folder, file)
                button_text = file.replace(".csv", "")
                quiz_button = ft.ElevatedButton(
                    button_text,
                    bgcolor='purple',
                    color='white',
                    width=300,
                    on_click=lambda e, f=filepath: self.start_quiz(f),
                )
                self.quiz_buttons.append(quiz_button)

    def upload_csv(self, e):
        file_picker = ft.FilePicker(on_result=self.upload_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        file_picker.pick_files(allow_multiple=False)
        
    def upload_result(self, e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            selected_file = e.files[0]
            original_filename = selected_file.name
            destination = os.path.join(self.quiz_folder, original_filename)
            try:
                shutil.copy(selected_file.path, destination)
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Quiz '{original_filename}' hochgeladen!"))
                self.page.snack_bar.open = True
                self.load_custom_quizzes()
            except Exception as ex:
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Fehler beim Hochladen: {ex}"))
                self.page.snack_bar.open = True
            self.show_startpage()

    def remove_csv(self, e):
        files = [file for file in os.listdir(self.quiz_folder) if file.endswith(".csv")]
        if not files:
            self.page.snack_bar = ft.SnackBar(ft.Text("Keine Quizdaten vorhanden."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        def confirm_remove(e):
            selected_file = dropdown.value
            if selected_file:
                os.remove(os.path.join(self.quiz_folder, selected_file))
                self.page.snack_bar = ft.SnackBar(ft.Text(f"Quiz '{selected_file}' erfolgreich gelöscht."))
                self.page.snack_bar.open = True
                self.page.close(self.page.dialog)
                self.show_startpage()

        dropdown = ft.Dropdown(options=[ft.dropdown.Option(file) for file in files],label='choose a file')
        confirm_button = ft.ElevatedButton("Löschen", on_click=confirm_remove)
        cancel_button = ft.ElevatedButton("Abbrechen", on_click=lambda e: self.page.close(self.page.dialog))
        
        self.page.dialog = ft.AlertDialog(
            title=ft.Text("Quiz löschen"),
            content=dropdown,
            actions=[confirm_button, cancel_button],
        )
        self.page.dialog.open = True
        self.page.update()

    def start_quiz(self, filename):
        self.load_questions(filename)
        if self.fragen:
            self.show_question_page()

    def show_question_page(self):
        self.page.controls.clear()
        
        if self.current_question < len(self.fragen):
            frage_data = self.fragen[self.current_question]
            
            if len(frage_data) != 6:
                self.page.controls.append(
                    ft.Container(
                        content=ft.Column( 
                            [
                                ft.Text(
                                    "Fehlerhafte Frage gefunden!", 
                                    size=20, 
                                    color="red"
                                ),
                                ft.ElevatedButton(
                                    "BACK",
                                    on_click=lambda e: self.show_startpage(),
                                    bgcolor="blue",
                                    color="white"
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER 
                        ),
                        alignment=ft.alignment.center,
                        width=self.page.window_width,
                        height=self.page.window_height,
                        bgcolor='pink'
                    )
                )
                self.page.update()
                return
            
            self.correct_answer = frage_data[5]
            self.page.controls.append(ft.Container(
                                                content=
                                                   ft.Text(
                                                       frage_data[0], 
                                                       size=25, 
                                                       weight="bold", 
                                                       color="white"
                                                       ),
                                                    alignment=ft.alignment.top_left,
                                                    padding=ft.padding.only(left=20,top=10)
                                                    )
                                                    
                                    )   
            
            
            self.answer_buttons = []
            for i in range(1, 5):
                answer_text = frage_data[i]
                if answer_text:
                    btn = ft.Button(
                            answer_text,
                            style=ft.ButtonStyle(alignment=ft.alignment.center_left),
                            bgcolor="lightblue",
                            width=self.page.window_width,
                            #width=500,
                            #expand=True,
                            on_click=self.create_answer_handler(answer_text),
                        )

                    self.answer_buttons.append(btn) 
                    self.page.controls.append(btn)


            self.page.controls.append(ft.Container(
                                        ft.Row(controls=(
                                                    ft.Text(
                                                    f"{self.current_question+1}/{len(self.fragen)}",
                                                    bgcolor='grey',
                                                    size=50,
                                                            ),
                                                    ft.ElevatedButton(
                                                    'NEXT', 
                                                    on_click=self.next_question,
                                                    width=90,  
                                                    bgcolor='grey'                                      
                                                            )
                                                        ),
                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                ),
                                                bgcolor='green',
                                                #alignment=ft.alignment.bottom_right,
                                                padding=ft.padding.only(right=20, bottom=25, top=40),
                                                    )
                                        )

        else:
            self.show_result()

        self.page.update()

    def load_questions(self, filename):
        self.fragen.clear()
        try:
            with open(filename, "r", encoding='utf-8') as data:
                reader = csv.reader(data, delimiter=';')
                for zeile in reader:
                    self.fragen.append(zeile)
        except FileNotFoundError:
            self.page.snack_bar = ft.SnackBar(ft.Text(f"Datei '{filename}' nicht gefunden!"))
            self.page.snack_bar.open = True
            self.page.update()
        self.current_question = 0
        self.correct_count = 0

    def check_answer(self, answer):
        is_correct = answer == self.correct_answer
        if is_correct:
            self.correct_count += 1

        for button in self.answer_buttons:
            if button.text == answer:
                button.bgcolor = "green" if is_correct else "red"
            elif button.text == self.correct_answer:
                button.bgcolor = "green"
            button.disabled = True

        self.page.update()

    def next_question(self, e):
        self.current_question += 1
        self.show_question_page()

    def show_result(self):
        total_questions = len(self.fragen)
        result_text = f"Du hast {self.correct_count} von {total_questions} Fragen richtig beantwortet!"
        result_score = round(self.correct_count / total_questions * 100, 1)

        self.page.controls.clear()
        self.page.controls.append(ft.Text(result_text, size=30, weight="bold", color="white"))
        self.page.controls.append(ft.Text(f"Ergebnis: {result_score} %", size=25, color="white"))

        self.page.controls.append(ft.ElevatedButton("Nochmal versuchen", on_click=lambda e: self.show_startpage()))
        self.page.controls.append(ft.ElevatedButton("Beenden", on_click=lambda e: self.page.window_close()))

        self.page.update()

    def create_answer_handler(self, answer):
        def handler(e):
            self.check_answer(answer)
        return handler

ft.app(target=QuizApp)