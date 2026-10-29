#include <stdio.h>
#include <windows.h>

DWORD WINAPI worker(LPVOID arg){
    int id = *(int*)arg;
    return 0;
}