#include <stdio.h>
#include <windows.h>
#include <stdlib.h>
#include <time.h>

#define N_SAMPLES 1000000

typedef struct{ double value; double time_taken;} CalculationResult;
typedef long long ll;
typedef struct{ const int* data; int start; int end; ll partial_sum;} ThreadData;

DWORD WINAPI worker(LPVOID arg){
    int id = *(int*)arg;
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
            // ops
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