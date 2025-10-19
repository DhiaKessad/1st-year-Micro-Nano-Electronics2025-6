//Program to get the binary of a scaned decimal number 
#include<stdio.h>

int i = 0;
int binary( int n){
i = i * 10 + n%2; 
    if(n <2){
        return i;
    }else{
        return binary(n/2);
    }
}
int main(){
    int n;
    printf("enter a number\n");
    scanf("%d", &n);
    printf("the binary rep is %d", binary(n));
    return 0;
}
