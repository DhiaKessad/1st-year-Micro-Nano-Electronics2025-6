//Fibonacci sequence
#include<stdio.h>

int a = 1;
int b = 1;
int c = 0;
int fibb (int n){
if(n > 1){
        c = a + b;
        a = b;
        b = c;
        fibb(n-1);
    }
    return c;
}

int main(){
    int n;
    printf("enetr the value of the index\n");
    scanf("%d", &n);
    if(n == 1 || n == 2){
        printf("the fibo sum of %d is : %d", n, 1);
    }else{
        printf("the fibo sum of %d is : %d", n, fibb(n));
    }
    
}