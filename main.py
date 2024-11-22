import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QCheckBox, QVBoxLayout, QWidget, \
    QTableWidget, QDialog, QLineEdit, QFormLayout, QLabel, QPushButton, QFileDialog, QMessageBox
from Calculations import *
import sqlite3


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)  # Загружаем дизайн
        self.setFixedSize(800, 500)
        self.stack.setCurrentIndex(0)
        self.StartWithAngle.clicked.connect(self.run)
        self.create_var.clicked.connect(self.create_pdf)
        self.redact.clicked.connect(self.open_redact_que)
        self.NameVAR.toggled.connect(self.toggle_button)
        self.class_button.setVisible(False)
        self.description.clicked.connect(self.open_desc)
        self.classes.setVisible(False)
        self.class_button.clicked.connect(self.open_redact_class)
        self.backbtn.clicked.connect(self.back_main)

    def toggle_button(self):
        if self.NameVAR.isChecked():
            self.class_button.setVisible(True)
            self.classes.setVisible(True)
            for i in range(self.kolvo_var.count()):
                widget = self.kolvo_var.itemAt(i).widget()
                if widget is not None:
                    widget.setVisible(False)  # Скрыть каждый виджет
            self.load_classes()
        else:
            self.class_button.setVisible(False)
            self.classes.setVisible(False)
            for i in range(self.kolvo_var.count()):
                widget = self.kolvo_var.itemAt(i).widget()
                if widget is not None:
                    widget.setVisible(True)  # Показать каждый виджет

    def run(self):
        self.stack.setCurrentIndex(1)

    def back_main(self):
        self.stack.setCurrentIndex(0)

    def open_redact_que(self):
        self.redact_form = QuestionApp()
        self.redact_form.show()

    def open_redact_class(self):
        self.redact_form = StudentDatabaseApp()
        self.redact_form.show()

    def open_desc(self):
        self.redact_form = Description()
        self.redact_form.show()

    def create_pdf(self):
        try:
            n_value = self.n.text()
            # Проверяем, что значение введено и является числом
            if not n_value and not self.NameVAR.isChecked():
                raise ValueError("Введите значение.")
            if self.NameVAR.isChecked():
                n_value = 1  # Пробуем преобразовать в число
            else:
                n_value = float(n_value)
            # Проверяем, что число больше 0 и меньше или равно 100
            if n_value <= 0 or n_value >= 100 and not self.NameVAR.isChecked():
                raise ValueError("Число должно быть больше 0 и меньше или меньше 100.")
            if self.NameVAR.isChecked() and self.classes.currentText() != "":
                print(self.classes.currentText())
                calculate(n_value, self.NameVAR.isChecked(), self.classes.currentText())
            else:
                calculate(n_value, self.NameVAR.isChecked())
        except ValueError as e:
            # Если возникла ошибка, показываем сообщение
            QMessageBox.critical(self, "Ошибка", str(e))
        except Exception as e:
            # Обработка других исключений (если нужно)
            QMessageBox.critical(self, "Ошибка", "Произошла ошибка: " + str(e))

    def load_classes(self):
        # Очистка текущих значений в комбобоксе
        self.classes.clear()
        # Подключение к базе данных
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        # Получение названий классов (таблиц)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        tables.pop(0)
        for table_name in tables:  # Заполнение комбобокса названиями классов
            self.classes.addItem(table_name[0])
        conn.close()  # Закрытие соединения

    def add_class(self):
        new_class_name = 'NewClass'  # Это может быть введено пользователем
        conn = sqlite3.connect('students.db')
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS {new_class_name} (id INTEGER PRIMARY KEY, name TEXT)")  # Создание новой таблицы
        conn.commit()
        conn.close()  # Закрытие соединения
        self.load_classes()  # Обновление комбобокса


class QuestionApp(QMainWindow):  # Редактирование пула вопросов
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Questions")
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)
        self.table_widget.setHorizontalHeaderLabels(["Title", "Active"])
        self.load_data()
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_data(self):
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("SELECT Title, active FROM Questions")
        rows = cursor.fetchall()
        self.table_widget.setRowCount(len(rows))
        for row_index, (title, active) in enumerate(rows):
            title_item = QTableWidgetItem(title)
            self.table_widget.setItem(row_index, 0, title_item)
            checkbox = QCheckBox()
            checkbox.setChecked(active == 1)
            checkbox.stateChanged.connect(lambda state, r=row_index: self.update_active_state(state, r))
            self.table_widget.setCellWidget(row_index, 1, checkbox)
        conn.close()

    def update_active_state(self, state, row_index):
        active_value = 1 if state == 2 else 0  # state 2 means checked
        title_item = self.table_widget.item(row_index, 0).text()
        conn = sqlite3.connect('base.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE Questions SET active = ? WHERE Title = ?", (active_value, title_item))
        conn.commit()
        conn.close()


class StudentDatabaseApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.conn = sqlite3.connect('students.db')  # Создаем или подключаемся к базе данных

    def initUI(self):
        layout = QVBoxLayout()
        self.label_class_name = QLabel('Введите название класса:')
        layout.addWidget(self.label_class_name)

        self.class_name_input = QLineEdit()
        layout.addWidget(self.class_name_input)

        self.label = QLabel('Нажмите кнопку для загрузки файла с фамилиями учащихся.')
        layout.addWidget(self.label)

        self.load_button = QPushButton('Загрузить файл')
        self.load_button.clicked.connect(self.load_file)
        layout.addWidget(self.load_button)

        self.label_class_view = QLabel('Введите название класса:')
        layout.addWidget(self.label_class_view)

        self.class_name_view_input = QLineEdit()
        layout.addWidget(self.class_name_view_input)

        self.show_students_button = QPushButton('Показать учеников')
        self.show_students_button.clicked.connect(self.show_students)
        layout.addWidget(self.show_students_button)

        self.label_remove_class = QLabel('Введите название класса для удаления:')
        layout.addWidget(self.label_remove_class)

        self.remove_class_input = QLineEdit()
        layout.addWidget(self.remove_class_input)

        self.remove_button = QPushButton('Удалить класс')
        self.remove_button.clicked.connect(self.remove_class)
        layout.addWidget(self.remove_button)

        self.setLayout(layout)
        self.setWindowTitle('Загрузка класса учеников')
        self.resize(400, 300)
        self.show()

    def create_table(self, class_name):
        with self.conn:
            self.conn.execute(f'''
                CREATE TABLE IF NOT EXISTS "{class_name}" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT NOT NULL
                )
            ''')

    def load_file(self):
        class_name = self.class_name_input.text().strip()
        if not class_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название класса.")
            return
        file_path = QFileDialog.getOpenFileName(self, 'TXT файл', '')[0]
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    names = file.readlines()
                    self.create_table(class_name)  # Создаем таблицу с именем класса
                    self.save_names_to_db(class_name, names)
                    QMessageBox.information(self, "Успех", "Фамилии успешно загружены в базу данных.")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {e}")

    def save_names_to_db(self, class_name, names):
        with self.conn:
            for name in names:
                name = name.strip()
                if name:
                    self.conn.execute(f'INSERT INTO "{class_name}" (full_name) VALUES (?)', (name,))

    def remove_class(self):
        class_name = self.remove_class_input.text().strip()
        if not class_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название класса для удаления.")
            return
        with self.conn:
            self.conn.execute(f'DROP TABLE IF EXISTS "{class_name}"')
        QMessageBox.information(self, "Успех", f"Класс '{class_name}' успешно удален.")

    def show_students(self):
        class_name = self.class_name_view_input.text().strip()
        if not class_name:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, введите название класса.")
            return
        student_window = StudentListWindow(class_name)
        student_window.exec()

    def closeEvent(self, event):
        self.conn.close()  # Закрываем соединение с базой данных при закрытии приложения
        event.accept()


class StudentListWindow(QDialog):
    def __init__(self, class_name):
        super().__init__()
        self.class_name = class_name
        self.conn = sqlite3.connect('students.db')

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.table_widget = QTableWidget()
        layout.addWidget(self.table_widget)

        save_button = QPushButton("Сохранить изменения")
        save_button.clicked.connect(self.save_changes)
        layout.addWidget(save_button)

        self.load_data()

        self.setLayout(layout)
        self.setWindowTitle(f"Ученики класса: {self.class_name}")
        self.resize(600, 400)
        self.show()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM [{self.class_name}]")
        rows = cursor.fetchall()

        if rows:
            columns = [description[0] for description in cursor.description]
            self.table_widget.setRowCount(len(rows))
            self.table_widget.setColumnCount(len(columns))
            self.table_widget.setHorizontalHeaderLabels(columns)

            for row_index, row in enumerate(rows):
                for column_index, item in enumerate(row):
                    self.table_widget.setItem(row_index, column_index, QTableWidgetItem(str(item)))

    def save_changes(self):
        row_count = self.table_widget.rowCount()

        for row in range(row_count):
            full_name_item = self.table_widget.item(row, 1)  # Предполагаем, что имя во втором столбце
            id_item = self.table_widget.item(row, 0)  # ID в первом столбце

            if full_name_item and id_item:
                full_name = full_name_item.text()
                student_id = id_item.text()

                with self.conn:
                    self.conn.execute(
                        f'UPDATE "{self.class_name}" SET full_name = ? WHERE id = ?',
                        (full_name, student_id)
                    )

        QMessageBox.information(self, "Успех", "Изменения успешно сохранены.")

    def closeEvent(self, event):
        self.conn.close()  # Закрываем соединение с базой данных при закрытии окна
        event.accept()


class Description(QWidget):
    def __init__(self):
        super().__init__()

        # Создаем виджет для отображения текста
        self.initUI()

    def initUI(self):
        # Устанавливаем заголовок окна
        self.setWindowTitle('Описние')

        # Создаем вертикальный макет
        layout = QVBoxLayout()

        text = (
            'Подсказка: Чтобы добавить учеников класса, создайте txt файл с фамилиями учащихся. Каждая фамилия на от'
            'дельной строке')

        # Создаем метку с текстом
        label = QLabel(text, self)

        # Добавляем метку в макет
        layout.addWidget(label)

        # Устанавливаем макет для главного окна
        self.setLayout(layout)

        # Устанавливаем размер окна
        self.resize(400, 200)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
