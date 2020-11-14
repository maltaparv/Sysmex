# пример измерения времени выполнения
from time import perf_counter

nums = [num for num in range(10**5)]
time_start = perf_counter()
nums_sum = sum(map(lambda x: x**2, nums))
print(nums_sum, perf_counter() - time_start)