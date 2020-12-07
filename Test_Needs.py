# # пример вывода уведомления не в комндной строке
# import win10toast
#
# toaster = win10toast.ToastNotifier()
# toaster.show_toast("Заголовок", "Описание уведомления")

# # пример измерения времени выполнения
# from time import perf_counter
#
# nums = [num for num in range(10**5)]
# time_start = perf_counter()
# nums_sum = sum(map(lambda x: x**2, nums))
# print(nums_sum, perf_counter() - time_start)

# from tkinter import *
# import math
#
#
# def hard_job():
#     x = 1000
#     while True:
#         x = math.log(x) ** 2.8
#         root.update()
#         print(x)
#         break
#
#
# root = Tk()
# root.title("Методы виджетов")
# root.minsize(width=500, height=400)

button = Button(text="Обновить", command=hard_job)
button.pack()
root.after(500, hard_job)
root.mainloop()
