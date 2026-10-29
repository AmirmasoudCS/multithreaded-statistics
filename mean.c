#include <stdio.h>
#include <windows.h>
#include <stdlib.h>
#include <time.h>

#define N_SAMPLES 1000000

DWORD WINAPI worker(LPVOID arg){
    int id = *(int*)arg;
    return 0;
}

void sep(){
    print("=========================\n");
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

int get_number_of_threads(){
    int threads_number = 1;
    printf("Please enter the number of threads you would like to use: ");
    scanf("%d", &threads_number);
    if(threads_number > 0 && threads_number < 5) return threads_number;
    else printf("Invalid number of threads!\nUsing a single thread.");
    return threads_number;

}

int main(void){

    int choice;
    while(1){
        sep();
        printf("What operation do you want to do?\n1. Average\n2. Variance\n");
        scanf("%d", &choice);
        if(choice==1){

        }
        else if(choice==2){

        }
        else{
            printf("Wrong Input!\n");
            sep();
            continue;
        }
    }

    return 0;
}