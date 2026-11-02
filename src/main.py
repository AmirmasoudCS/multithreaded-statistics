import random
import threading
import time

N_SAMPLES = 1000000

def sample(number_of_samples: int) -> list[int]:
    numbers = []
    for i in range(number_of_samples):
        randomly_generated_number = int(random.random() * 100)
        numbers.append(randomly_generated_number)
    return numbers

def calculate_partial_sum(numbers: list[int], start: int, end: int) -> int:
    local_sum = 0
    for i in range(start, end):
        local_sum += numbers[i]
    return local_sum

def main():
    threads = 4
    print(f"Number of samples: {N_SAMPLES}")
    print(f"Number of threads: {threads}")

    threads = []

    start_time = time.time()

    thread1 = threading.Thread(target=calculate_partial_sum, args=(0, N_SAMPLES/4 -1))
    thread2 = threading.Thread(target=calculate_partial_sum, args=(N_SAMPLES/4, N_SAMPLES/4 * 2 - 1))
    thread3 = thrading.Thread(target=calculate_partial_sum, args=(N_SAMPLES/4 * 2, N_SAMPLES/4 * 3 - 1))
    thread4 = threading.Thread(target=calculate_partial_sum, args=(N_SAMPLES/4 * 3, N_SAMPLES - 1))

    threads.append(thread1)
    threads.append(thread2)
    threads.append(thread3)
    threads.append(thread4)

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    

    end_time = time.time()
    elapsed_time = end_time - start_time
    