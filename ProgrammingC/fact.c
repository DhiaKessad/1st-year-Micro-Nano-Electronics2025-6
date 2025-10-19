//Factorial of a number
#include<stdio.h>

int factorial(int n){
    if (n == 0){
        return 1;
    }else{
        return n * factorial(n-1);
    }
}

int main(){
    int n;
    printf("Please enter the number of the factorial index");
    scanf("%d\n", &n);
    printf("the factorial of %d is: %d", n, factorial(n));
}