//calculate the sum of digits
#include<stdio.h>

int sum = 0;
int sumofdigits(int n){
    sum = sum + n%10;
    if(n < 10){
        return sum;
    }else{
        return(sumofdigits(n/10));
    }
}

int main(){
    int n;
    printf("Enter the number");
    scanf("%d", &n);
    if(n<10 ){
        printf(" the sum of digits is : %d\n", n);
    }else{
        printf(" the sum of digits is : %d\n", sumofdigits(n));
    }
}