#include <stdio.h>   
#include <stdlib.h>  
#include <string.h> 
#include <math.h>  

int main() {
    printf("Hello from C!\n");

    for (int i = 1; i <= 5; i++) {
        for(int j = 2; j <= 10; j++){
            printf("%d\n", i);
            printf("%d\n", j);
        }
    }

    while(int x < 5){
        x = x + 1;
    }

}