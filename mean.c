#include <stdio.h>
#include <windows.h>
#include <stdlib.h>
#include <time.h>

#define N_SAMPLES 1000000

DWORD WINAPI worker(LPVOID arg){
    int id = *(int*)arg;
    return 0;
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
    return data;
}

int main(void){

    



    return 0;
}