#include <stdio.h>
#include <windows.h>
#include <stdlib.h>
#include <time.h>

#define N_SAMPLES 1000000

typedef struct{ double value; double time_taken;} CalculationResult;
typedef long long ll;
typedef struct{ const int* data; int start; int end; ll partial_sum;} ThreadData;

DWORD WINAPI worker(LPVOID arg){
    ThreadData* args = (ThreadData*)arg;
    ll local_sum=0;
    for(ll i=args->start; i<args->end; i++){
        local_sum+=args->data[i];
    }
    args->partial_sum = local_sum;
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
    srand(67);
    for(int i = 0; i < number_of_samples; i++){
        data[i] = rand() % 100;
    }
    printf("Sampling %d samples done!", number_of_samples);
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
        threads[i] = CreateThread(NULL, 0, worker, &thread_data[i], 0, NULL);
    }
    WaitForMultipleObjects(number_of_threads, threads, TRUE, INFINITE);
    ll sum=0;
    for(int j = 0; j < number_of_threads; j++){
        sum+=thread_data[j].partial_sum;
        CloseHandle(threads[j]);
    }
    QueryPerformanceCounter(&end);
    double average = (double)sum / number_of_samples;
    double elapsed = (double)(end.QuadPart - start.QuadPart) / frequency.QuadPart;
    free(threads);
    free(thread_data);
    CalculationResult result = {average, elapsed};
    return result;
}

int main(void){

    int choice;
    while(1){
        sep();
        printf("What operation do you want to do?\n1. Average\n2. Variance\n");
        scanf("%d", &choice);
        if(choice==1){
            int threads_number = get_number_of_threads();
            int* data = sample(N_SAMPLES);
            if(data==NULL){
                printf("Failed to allocate memory!\n");
                continue;
            }
            CalculationResult result = calculate_average(data, N_SAMPLES, threads_number);
            free(data);
        }
        else if(choice==2){
            int threads_number = get_number_of_threads();
            int* data = sample(N_SAMPLES);
            if(data==NULL){
                printf("Failed to allocate memory!\n");
                continue;
            }
            // ops
            free(data);
        }
        else{
            printf("Wrong Input!\n");
            sep();
            continue;
        }
    }

    return 0;
}