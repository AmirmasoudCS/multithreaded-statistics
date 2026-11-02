import random
import threading

N_SAMPLES = 1000000

def sample(number_of_samples: int) -> list[int]:
    numbers = []
    for i in range(number_of_samples):
        randomly_generated_number = int(random.random() * 100)
        numbers.append(randomly_generated_number)
    return numbers
