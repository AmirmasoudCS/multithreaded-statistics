
import random
import threading
import time

N_SAMPLES = 10000000
NUMBER_OF_THREADS = 4

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
    number_of_threads = NUMBER_OF_THREADS
    print(f"Number of samples: {N_SAMPLES}")
    print(f"Number of threads: {number_of_threads}")

    numbers = sample(N_SAMPLES)
    threads = []
    results = [0] * number_of_threads

    chunk_size = (N_SAMPLES + number_of_threads - 1) // number_of_threads

    start_time = time.perf_counter()

    for i in range(number_of_threads):
        start = i * chunk_size
        end = min(start + chunk_size, N_SAMPLES)

        thread = threading.Thread(
            target=calculate_partial_sum,
            args=(numbers, start, end, results, i)
        )
        threads.append(thread)

    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
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
