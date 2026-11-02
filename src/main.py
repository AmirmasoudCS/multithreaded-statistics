
import random
import threading
import multiprocessing
import time

N_SAMPLES = 10000000
NUMBER_OF_THREADS = 4

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

def calculate_partial_sum_thread(numbers: list[int], start: int, end: int, results: list[int], index_to_write: int) -> None:
    results[index_to_write] = calculate_partial_sum(numbers, start, end)

def calculate_partial_sum_process(numbers: list[int], start: int, end: int, results_queue) -> None:
    local_sum = calculate_partial_sum(numbers, start, end)
    results_queue.put(local_sum)

def main():
    number_of_threads = NUMBER_OF_THREADS

    print("Select execution method:")
    print("1. Multithreading")
    print("2. Multiprocessing")

    execution_mode = input("Your choice: ")

    while execution_mode not in ["1", "2"]:
        print("Invalid choice!")
        execution_mode = input("Your choice: ")

    print(f"Number of samples: {N_SAMPLES}")
    print(f"Number of threads/processes: {number_of_threads}")

    numbers = sample(N_SAMPLES)
    workers = []
    results = [0] * number_of_threads

    chunk_size = (N_SAMPLES + number_of_threads - 1) // number_of_threads

    start_time = time.perf_counter()

    if execution_mode == "1":
        print("Execution method: Multithreading")

        for i in range(number_of_threads):
            start = i * chunk_size
            end = min(start + chunk_size, N_SAMPLES)

            thread = threading.Thread(
                target=calculate_partial_sum_thread,
                args=(numbers, start, end, results, i)
            )
            workers.append(thread)

    else:
        print("Execution method: Multiprocessing")

        results_queue = multiprocessing.Queue()

        for i in range(number_of_threads):
            start = i * chunk_size
            end = min(start + chunk_size, N_SAMPLES)

            process = multiprocessing.Process(
                target=calculate_partial_sum_process,
                args=(numbers, start, end, results_queue)
            )
            workers.append(process)

    for worker in workers:
        worker.start()

    if execution_mode == "1":
        for worker in workers:
            worker.join()

    else:
        for i in range(number_of_threads):
            results[i] = results_queue.get()

        for worker in workers:
            worker.join()

        results_queue.close()

    total = sum(results)
    average = total/N_SAMPLES

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print("-------------------------------------")
    print(f"Average of our samples: {average:.2f}")
    print(f"Time took to take average: {elapsed_time:.6f}")
    print("-------------------------------------")


if __name__ == "__main__":
    random.seed(67)
    main()
