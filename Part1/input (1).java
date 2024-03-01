// Simple java program that finds the factorial

public class Factorial {
    public static void main(String[] args) {
        int number = 5; // Change this number to calculate factorial for a different number
        long factorial = calculateFactorial(number);
        System.out.println("Factorial of " + number + " is: " + factorial);
    }

    public static long calculateFactorial(int n) {
        long factorial = 1;
        for (int i = 1; i <= n; i++) {
            factorial *= i;
        }
        return factorial;
    }
}





