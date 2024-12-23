import flet as ft
import os
import csv
import shutil

class QuizApp:
    def __init__(self, page: ft.Page):
        self.page = page

        self.page.title = "Quiz App"
        self.page.horizontal_alignment = 'CENTER'
        self.page.window.min_width=600
        self.page.window.min_height=450
        self.page.window.height=600

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
                    'Choose a Quiz', 
                                size=40, 
                                    weight=ft.FontWeight.BOLD
                ),
                padding=ft.padding.only(top=15, bottom=30)
            )
        self.load_custom_quizzes()
        quizzes = ft.Container(
                    ft.Column(
                        self.quiz_buttons,
                            scroll=ft.ScrollMode.ADAPTIVE
                    ), 
                    height=250,
                )

        
        self.page.controls.append(header)
        self.page.controls.append(quizzes)

        buttons = ft.Column(
                        controls=[
                                    ft.Container(
                                        expand=True
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.ElevatedButton(
                                                        'DELETE', 
                                                            on_click=self.remove_csv,
                                                                height=45, 
                                                                    width=130,
                                                                        style=ft.ButtonStyle(
                                                                            text_style=ft.TextStyle(
                                                                                    size=20,
                                                                                        weight=ft.FontWeight.W_600,
                                                                                                  ),
                                                                                                color=ft.colors.WHITE,
                                                                                                    bgcolor=ft.colors.RED
                                            ),
                                            ),
                                            ft.ElevatedButton(
                                                        'upload',
                                                            on_click=self.upload_csv,
                                                                height=45, 
                                                                    width=130,
                                                                        style=ft.ButtonStyle(
                                                                            text_style=ft.TextStyle(
                                                                                    size=20,
                                                                                        weight=ft.FontWeight.W_600,
                                                                                                  ),
                                                                                                color=ft.colors.WHITE,
                                                                                                    bgcolor=ft.colors.GREEN,
                                                                        ),
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                        ],
                           expand=True,
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
                    ft.Column(
                        controls=[
                            ft.Container(  
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "FILE ERROR!", 
                                                size=50, 
                                                    color="red",
                                                        text_align=ft.TextAlign.CENTER
                                        ),
                                        ft.ElevatedButton(
                                            "BACK",
                                            on_click=lambda e: self.show_startpage(), 
                                                style=ft.ButtonStyle(
                                                    bgcolor="blue", 
                                                        color="white",
                                                            text_style=ft.TextStyle(
                                                                size=40,        
                                                            ),
                                                    padding=ft.padding.all(15)
                                            )
                                        )
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER 
                                ),
                                padding=20,
                                alignment=ft.alignment.center,
                                expand=True
                            )
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        expand=True  
                    )
                )

            self.page.update()
            
            self.correct_answer = frage_data[5]
            self.page.controls.append(
                                    ft.Container(
                                        content=
                                            ft.Text(
                                                frage_data[0], 
                                                    style=ft.TextStyle(
                                                        size=30, 
                                                            weight=ft.FontWeight.W_600, 
                                                                color=ft.colors.WHITE
                                                    )
                                                ),
                                                    alignment=ft.alignment.top_left,
                                                        padding=ft.padding.only(left=10,top=15,bottom=20),
                                                            width=self.page.window_width
                                        )                
                                    )   
            
            
            self.answer_buttons = []
            for i in range(1, 5):
                answer_text = frage_data[i]
                if answer_text:
                    btn = ft.Button(
                            answer_text,
                                style=ft.ButtonStyle(
                                    text_style=ft.TextStyle(size=30, weight=ft.FontWeight.W_500),
                                        color=ft.colors.WHITE,
                                            bgcolor=ft.colors.LIGHT_BLUE,
                                                alignment=ft.alignment.center_left,
                                                    shape=ft.RoundedRectangleBorder(radius=12),
                                                        padding=ft.padding.all(10),
                                                            side=ft.BorderSide(3, ft.Colors.BLACK),
                                                ),
                            width=self.page.window_width,
                                on_click=self.create_answer_handler(answer_text),
                        )

                    self.answer_buttons.append(btn) 
                    self.page.controls.append(btn)


            self.page.controls.append(ft.Column(controls=[
                                        ft.Container(expand=True),
                                        ft.Container(
                                            ft.Row(
                                                controls=[
                                                        ft.Text(
                                                            f"{self.current_question+1}/{len(self.fragen)}",
                                                                style=ft.TextStyle(
                                                                        size=25,
                                                                            weight=ft.FontWeight.W_500,
                                                                                color=ft.colors.GREY
                                                                )
                                                                                ),
                                                    
                                                        ft.ElevatedButton(
                                                            'NEXT', 
                                                                on_click=self.next_question,
                                                                    style=ft.ButtonStyle(
                                                                        text_style=ft.TextStyle(
                                                                            size=30,
                                                                                weight=ft.FontWeight.W_800,
                                                                        ),
                                                                                    color=ft.colors.WHITE,
                                                                                        bgcolor=ft.colors.BLUE,
                                                                                            padding=ft.padding.all(15),
                                                                                                shape=ft.RoundedRectangleBorder(radius=15)
                                                                    )
                                                                                        )
                                                            ],
                                                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                                                                )
                                                                            )                                               
                                                                        ],
                                                                    expand=True 
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
        result_text = f"{self.correct_count} of {total_questions} questions correct!"
        result_score = round(self.correct_count / total_questions * 100, 1)

        self.page.controls.clear()
        self.page.controls.append(ft.Container(
                                    ft.Text(
                                        result_text, 
                                            size=30, 
                                                weight="bold", 
                                                    color="white"),
                                                        padding=ft.padding.all(20),
                                                )
                                            )
        self.page.controls.append(ft.Text(f"Result: {result_score} %", size=50, color="white"))

        self.page.controls.append(ft.Container(
                                    ft.ElevatedButton(
                                        "BACK", on_click=lambda e: self.show_startpage(), 
                                            style = ft.ButtonStyle(
                                                text_style=
                                                    ft.TextStyle(
                                                        size=50,
                                                            weight=ft.FontWeight.BOLD
                                                    ),
                                                                color=ft.colors.BLACK,
                                                                    bgcolor=ft.colors.ORANGE_500,
                                                                        padding=ft.padding.all(5),
                                                                            shape=ft.RoundedRectangleBorder(radius=15)
                                                    )
                                                ),
                                                    expand=True, 
                                                        alignment=ft.alignment.top_center,
                                                            padding=ft.padding.only(top=50)
                                        )
                                    )
        #self.page.controls.append(ft.ElevatedButton("Beenden", on_click=lambda e: self.page.window_close()))

        self.page.update()

    def create_answer_handler(self, answer):
        def handler(e):
            self.check_answer(answer)
        return handler

ft.app(target=QuizApp)