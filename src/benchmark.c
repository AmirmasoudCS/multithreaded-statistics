#include <stdio.h>
#include <windows.h>
#include <stdlib.h>

#define N_SAMPLES 100000000

typedef struct{ double value; double time_taken;} CalculationResult;
typedef long long ll;
typedef struct{ const int* data; int start; int end; ll partial_sum; double mean; double partial_variance;} ThreadData;

DWORD WINAPI average_worker(LPVOID arg){
    ThreadData* args = (ThreadData*)arg;
    ll local_sum=0;
    for(ll i=args->start; i<args->end; i++){
        local_sum+=args->data[i];
    }
    args->partial_sum = local_sum;
    return 0;
}

DWORD WINAPI variance_worker(LPVOID arg){
    ThreadData* args = (ThreadData*)arg;
    double deviation;
    double local_sum=0.0;
    for(ll i = args->start; i < args->end; i++){
        deviation = args->data[i] - args->mean;
        local_sum += deviation*deviation;
    }
    args->partial_variance=local_sum;
    return 0;
}

void sep(){
    printf("=========================\n");
}

int* sample(int number_of_samples){
    int* data = malloc(number_of_samples * sizeof(int));
    if(data==NULL){
        printf("Failed to allocate memory to data.\n");
        return NULL;
    }
    for(int i = 0; i < number_of_samples; i++){
        data[i] = rand() % 100;
    }
    printf("Sampling %d samples done!\n", number_of_samples);
    sep();
    return data;
}

int get_number_of_threads(){
    int threads_number;
    printf("Please enter the number of threads you would like to use: ");
    scanf("%d", &threads_number);
    if(threads_number > 0 && threads_number < 5) return threads_number;
    else printf("Invalid number of threads!\nUsing a single thread.");
    return 1;
}

CalculationResult calculate_average(const int* data, int number_of_samples, int number_of_threads){
    LARGE_INTEGER start, end, frequency;
    QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&start);
    HANDLE* threads = malloc(number_of_threads * sizeof(HANDLE));
    ThreadData* thread_data = malloc(number_of_threads * sizeof(ThreadData));
    int chunk = number_of_samples / number_of_threads;
    for(int i = 0; i < number_of_threads; i++){
        int start_index = i * chunk;
        int end_index = (i==number_of_threads-1)? number_of_samples: start_index + chunk;
        thread_data[i].data = data;
        thread_data[i].start = start_index;
        thread_data[i].end = end_index;
        thread_data[i].partial_sum=0;
        threads[i] = CreateThread(NULL, 0, average_worker, &thread_data[i], 0, NULL);
    }
    WaitForMultipleObjects(number_of_threads, threads, TRUE, INFINITE);
    ll sum=0;
    for(int j = 0; j < number_of_threads; j++){
        sum+=thread_data[j].partial_sum;
        CloseHandle(threads[j]);
    }
    free(threads);
    free(thread_data);
    QueryPerformanceCounter(&end);
    double average = (double)sum / number_of_samples;
    double elapsed = (double)(end.QuadPart - start.QuadPart) / frequency.QuadPart;
    CalculationResult result = {average, elapsed};
    return result;
}

CalculationResult calculate_variance(const int* data, int number_of_samples, int number_of_threads){
    LARGE_INTEGER start, end, frequency;
    QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&start);
    HANDLE* threads = malloc(number_of_threads * sizeof(HANDLE));
    ThreadData* thread_data = malloc(number_of_threads * sizeof(ThreadData));
    int chunk = number_of_samples / number_of_threads;
    for(int i = 0; i < number_of_threads; i++){
        int start_index = i * chunk;
        int end_index = (i==number_of_threads-1)? number_of_samples: start_index + chunk;
        thread_data[i].data = data;
        thread_data[i].start = start_index;
        thread_data[i].end = end_index;
        thread_data[i].partial_sum=0;
        threads[i] = CreateThread(NULL, 0, average_worker, &thread_data[i], 0, NULL);
    }
    WaitForMultipleObjects(number_of_threads, threads, TRUE, INFINITE);
    ll sum=0;
    for(int j = 0; j < number_of_threads; j++){
        sum+=thread_data[j].partial_sum;
        CloseHandle(threads[j]);
    }
    double average = (double)sum / number_of_samples;
    for(int i = 0; i < number_of_threads; i++){
        int start_index = i * chunk;
        int end_index = (i==number_of_threads-1)? number_of_samples: start_index + chunk;
        thread_data[i].data = data;
        thread_data[i].start = start_index;
        thread_data[i].end = end_index;
        thread_data[i].partial_sum=0;
        thread_data[i].mean = average;
        thread_data[i].partial_variance=0.0;
        threads[i] = CreateThread(NULL, 0, variance_worker, &thread_data[i], 0, NULL);
    }
    WaitForMultipleObjects(number_of_threads, threads, TRUE, INFINITE);
    double total=0;
    for(int i = 0; i < number_of_threads; i++){
        total+=thread_data[i].partial_variance;
        CloseHandle(threads[i]);
    }
    free(threads);
    free(thread_data);
    QueryPerformanceCounter(&end);
    double variance = total / number_of_samples;
    double elapsed = (double)(end.QuadPart - start.QuadPart) / frequency.QuadPart;
    CalculationResult result = {variance, elapsed};
    return result;
}


int main(int argc, char* argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: %s <average|variance> <threads>\n", argv[0]);
        return 1;
    }

    const char* operation = argv[1];

    char* endptr;
    long threads_number = strtol(argv[2], &endptr, 10);

    if (*argv[2] == '\0' || *endptr != '\0' ||
        threads_number < 1 || threads_number > 4) {
        fprintf(stderr, "Error: threads must be an integer from 1 to 4.\n");
        return 1;
    }

    if (strcmp(operation, "average") != 0 &&
        strcmp(operation, "variance") != 0) {
        fprintf(stderr, "Error: operation must be average or variance.\n");
        return 1;
    }

    srand(67);

    int* data = sample(N_SAMPLES);
    if (data == NULL) {
        fprintf(stderr, "Failed to allocate memory!\n");
        return 1;
    }

    CalculationResult result;

    if (strcmp(operation, "average") == 0) {
        result = calculate_average(data, N_SAMPLES, (int)threads_number);
    } else {
        result = calculate_variance(data, N_SAMPLES, (int)threads_number);
    }

    // CSV-compatible output for the benchmark script.
    printf("RESULT,%s,%ld,%.10f,%.9f\n",
           operation, threads_number, result.value, result.time_taken);

    free(data);
    return 0;
}
