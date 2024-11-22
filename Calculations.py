import math
import random
from pdfcreator import *
from main import *


def calculate(n, boolean, name_class=None):
    text = []
    otvet = []
    v_massiv = [i for i in range(100, 401, 10)]
    a_massiv = [i for i in range(20, 81, 5)]
    if boolean:
        n = take_name_in_classes(name_class)
    else:
        n = int(n)
    while n > 99:
        print("Кол-во вариантов не может привышать 99")
        n = int(input("Введите кол-во вариантов: "))
    for i in range(n):
        # ---------------------------------------Вычисление для варианта-----------------------------------------------#
        v = random.choice(v_massiv)
        a = random.choice(a_massiv)
        sin_a = float(round(math.sin(math.radians(a)), 3))
        cos_a = float(round(math.cos(math.radians(a)), 3))
        v_min = round(v * cos_a, 3)
        t_pod = round(v * sin_a / 10, 1)
        t_pol = round(2 * v * sin_a / 10, 1)
        H_max = round(v ** 2 * sin_a ** 2 / 20, 1)
        S = round(v ** 2 * math.sin(2 * math.radians(a)) / 10, 1)
        t = random.uniform(t_pod, t_pol)
        if t < 10:
            t = round(t, 1)
        else:
            t = round(t)
        x = round(v * math.cos(math.radians(a)) * t, 1)
        y = round(v * math.sin(math.radians(a)) * t - (10 * t ** 2 / 2), 1)
        v_x = round(v_min, 1)
        v_y = round(v * math.sin(math.radians(a)) - 10 * t, 1)
        v_1 = round(math.sqrt(v_x ** 2 + v_y ** 2), 1)
        b = round(math.degrees(math.atan(abs(v_y) / v_x)), 1)
        S_max = round(v ** 2 * math.sin(2 * math.radians(45)) / 10, 1)
        # -------------------------------------------------------------------------------------------------------------#
        if boolean:
            name = create_name_class(name_class)
        else:
            name = create_name_num()
        text.append((name, f"Дано:\nv0: {v} м/c\nα: {a} градусов\nt: {t} сек"))
        otvet.append((
            name,
            f"sin α и округлять до тысычных: {round(sin_a, 3)}\n"
            f"cos α и округлять до тысычных: {round(cos_a, 3)}\n"
            f"t(под): {t_pod} сек\n"
            f"t(пол): {t_pol} сек\n"
            f"Hmax: {H_max} м\n"
            f"S: {S} м\n"
            f"Smax: {S_max} м\n"
            f"X в момент времени t: {x} м\n"
            f"Y в момент времени t: {y} м\n"
            f"Vx в момент времени t: {v_x} м/с\n"
            f"Vy в момент времени t: {v_y} м/c\n"
            f"модуль скорости V в момент времени t: {v_1} м/с\n"
            f"Угол β между вектором скорости и остью х в момент времени t: {b} градусов"
        ))
        text.sort(key=lambda zxc: zxc[0])
        otvet.sort(key=lambda zxc: zxc[0])
    if 100 > n > 0:
        variant = PDFCreator()
        variant.create_text(text, otvet)
    else:
        QMessageBox.critical(None, "Ошибка", "Произошла ошибка: список учеников пуст")
