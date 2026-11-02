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

def calculate_partial_sum(numbers: list[int], start: int, end: int, results: list[int], index_to_write: int) -> None:
    local_sum = 0
    for i in range(start, end):
        local_sum += numbers[i]
    results[index_to_write] = local_sum

def main():
    threads = 4
    print(f"Number of samples: {N_SAMPLES}")
    print(f"Number of threads: {threads}")

    numbers = sample(N_SAMPLES)
    threads = []
    results = [0] * 4

    start_time = time.time()

    thread1 = threading.Thread(target=calculate_partial_sum, args=(numbers, 0, N_SAMPLES//4, results, 0))
    thread2 = threading.Thread(target=calculate_partial_sum, args=(numbers, N_SAMPLES//4, N_SAMPLES//4 * 2, results, 1))
    thread3 = threading.Thread(target=calculate_partial_sum, args=(numbers, N_SAMPLES//4 * 2, N_SAMPLES//4 * 3, results, 2))
    thread4 = threading.Thread(target=calculate_partial_sum, args=(numbers, N_SAMPLES//4 * 3, N_SAMPLES, results, 3))

    threads.append(thread1)
    threads.append(thread2)
    threads.append(thread3)
    threads.append(thread4)

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    sum = results.sum()
    average = sum/N_SAMPLES

    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print("-------------------------------------")
    print(f"AVerage of our samples: {average}")
    print(f"Time took to take average: {elapsed_time}")
    print("-------------------------------------")
