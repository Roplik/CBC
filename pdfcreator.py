import random
import sqlite3
from PyQt6.QtWidgets import QMessageBox
from fpdf import FPDF

var_name = []


def create_name_num():  # создание уникального номера для варианта
    name = random.randint(1, 99)
    while name in var_name:
        name = random.randint(1, 99)
    var_name.append(name)
    return name


def create_name_class(table_name):  # Забираем фамилию для варианта
    return var_name.pop(0)


def take_name_in_classes(table_name):  # забираем фамилии из бд
    global var_name
    connection = sqlite3.connect('students.db')
    cursor = connection.cursor()
    res = cursor.execute(
        f'''SELECT full_name FROM [{table_name}]''').fetchall()
    connection.close()
    var_name = [i[0] for i in res]
    var_name = sorted(var_name)
    return len(var_name)


class PDFCreator:
    def __init__(self):
        self.pdf = FPDF()
        self.pdf.add_font('DejaVu', '', 'font/timesnewromanpsmt.ttf')
        self.pdf.add_font('DejaVu', "b", 'font/timesnewromanpsmt.ttf')
        self.pdf.set_font('DejaVu', '', 12)
        self.WithAnswer = True

    def create_text(self, a, b):
        pdf = self.pdf
        pdf.add_page()
        connect = sqlite3.connect('base.db')
        cursor = connect.cursor()
        res = cursor.execute(
            '''SELECT * FROM Questions ''').fetchall()  # Забираем из бд какие вопросы мы включили
        self.what_answer = []
        for i in range(len(res)):
            if res[i][1] == 1:
                self.what_answer.append(i)
        res = cursor.execute(
            '''SELECT Title FROM Questions WHERE active = 1''').fetchall()  # Забираем из бд какие вопросы мы включили
        quantity = len(res)  # Нужно для определения количества столбиков ответа
        res = [str(i + 1) + ". " + res[i][0] + "\n" for i in range(len(res))]  # Форматирование для записи вопросов
        line = "".join(res)
        cursor.close()
        connect.close()

        # ---------------------------------------Cоздаем уникальный вариант--------------------------------------------#
        for i in range(len(a)):
            with pdf.rotation(angle=90, x=pdf.get_x() + 5, y=pdf.get_y() + 6):  # Добавление кода варианта
                pdf.image("image/kod.png", x=pdf.get_x() - 75, y=pdf.get_y() - 2, w=93)
                current_x = pdf.get_x() - 5
                pdf.set_x(current_x)
                pdf.cell(text=str(a[i][0]))
            pdf.image("image/firstpng.png", x=20, y=pdf.get_y() + 10, w=70)  # Добавление графика
            pdf.cell(80)
            pdf.cell(30, 5, f"Вариант №{str(a[i][0])}", align="C")  # Добавление заголовка
            pdf.ln(8)
            fixed_variant_height = 80  # Установите желаемую высоту блока варианта
            start_y = pdf.get_y()  # Сохраняем текущую позицию Y
            pdf.cell(10)
            pdf.multi_cell(500, 10, max_line_height=3.9, text=a[i][1], new_x="LMARGIN", new_y="NEXT")  # Дано
            current_y = pdf.get_y() - 15
            pdf.set_y(current_y)
            pdf.cell(80)
            pdf.multi_cell(110, 10, max_line_height=3.5, text=line, new_x="LMARGIN", )  # Вопросы
            table_width = 115
            n = len(res)
            column_width = table_width / 10  # 10 столбцов
            max_columns_per_row = 10
            rows_needed = (n + max_columns_per_row - 1) // max_columns_per_row  # Округляем вверх

            for row in range(rows_needed):     # Генерируем строки таблицы
                pdf.cell(80)  # Отступ слева
                for col in range(max_columns_per_row):
                    index = row * max_columns_per_row + col
                    if index < n:
                        pdf.cell(column_width, 5, str(index + 1), border=1)  # Номер вопроса
                pdf.ln()
                pdf.cell(80)  # Отступ слева для строки ответов
                for col in range(max_columns_per_row):
                    index = row * max_columns_per_row + col
                    if index < n:
                        pdf.cell(column_width, 5, "", border=1)  # Пустая ячейка для ответа
                pdf.ln(5)
            current_variant_height = pdf.get_y() - start_y  # Вычисляем текущую высоту блока варианта
            if current_variant_height < fixed_variant_height:  # Если высота блока меньше фиксированной высоты, добавляем пустые строки
                pdf.ln(fixed_variant_height - current_variant_height)
            print(i)
            if (i + 1) % 3 == 0 and (i + 1) != len(a):
                pdf.add_page()

        if self.WithAnswer:
            self.create_answer(b)
        else:
            pass
        # -------------------------------------------------------------------------------------------------------------#

    def create_answer(self, b):
        pdf = self.pdf
        pdf.add_page()
        answer = []
        for i in b:
            qwe = i[1].split('\n')
            result = []
            for j in range(0, len(qwe)):
                if j in self.what_answer:
                    result.append(qwe[j])
            answer.append((i[0], "\n".join(result)))
        # ---------------------------------------Cоздаем ответы для вариантов------------------------------------------#
        for i in range(len(answer)):
            pdf.cell(60)
            pdf.cell(80, 5, f"Ответы на вариант №{answer[i][0]}", border=1, align="C")
            pdf.ln(5)
            pdf.multi_cell(500, 10, max_line_height=3.9, text=answer[i][1], new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
        # -------------------------------------------------------------------------------------------------------------#
        print("Дело сделано")
        pdf.output("tuto1.pdf")


'''TABLE_DATA = (
    ("Найти: ", "Ответ:"),
    ("1. sin α и округлять до тысычных", ""),
    ("2. cos α и округлять до тысычных", ""),
    ("3. Время подъема на максимальную высоту tпод", ""),
    ("4. Время полета tпол", ""),
    ("5. Максимальную высоту полета Н", ""),
    ("6. Дальность полета S", ""),
    ("7. Максимально возможную дальность полета при той же начальной скорости Sm", ""),
    ("8. Координату тела x в момент времени t", ""),
    ("9. Координату тела y в момент времени t", ""),
    ("10. Проекцию скорости Vx в момент времени t", ""),
    ("11. Проекцию скорости Vy в момент времени t", ""),
    ("12.Модуль скорости V в момент t", ""),
    ("13.Угол β между вектором скорости и осью х в момент времени t", ""),'''

