# multithreaded-statistics

A simple C project that calculates statistical values from a large dataset of randomly generated integers using multithreading on Windows.

## Features

- **Mean:** Calculates the average of the generated values using multiple threads.
- **Variance:** Planned feature to measure how much the values differ from the mean.
- **Execution Time:** Measures the calculation time to compare performance with different numbers of threads.

## How It Works

1. Generate 100,000,000 random integers between 0 and 99.
2. Divide the dataset into smaller chunks based on the selected number of threads.
3. Let each thread process its assigned chunk.
4. Combine the partial results to calculate the final statistic.

## Compilation

Compile the program using GCC:

```bash
gcc main.c -o main.exe
```

## Usage

Run the executable:

```bash
main.exe
```

Choose an operation from the menu:

1. Calculate the mean.
2. Calculate the variance.

Then choose the number of threads to use, from 1 to 4.

## License

See [Here](./LICENSE).
