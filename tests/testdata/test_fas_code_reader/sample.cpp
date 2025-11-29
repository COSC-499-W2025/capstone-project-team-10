#include <iostream> 
#include <string>    
#include "my_utility.h" 

class Animal {
public:
    void speak() {
        std::cout << "Animal sound" << std::endl;
    }
};

int helper() {
    std::cout << "I'm a helper" << std::endl;
}

int main() {
    for (int i = 1; i <= 5; i++) {
        for(int j = 2; j <= 10; j++){
            printf("%d\n", i);
            printf("%d\n", j);
        }
    }

    while(int x < 5){
        x = x + 1;
    }

    return 0;
}