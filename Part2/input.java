import java.util.Scanner; // Import Scanner class for user input
import java.util.Random; // Import Random class for generating random numbers

public class RandomNumberGuessingGame {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in); // Create a Scanner object for user input
        Random random = new Random(); // Create a Random object for generating random numbers

        int randomNumber = random.nextInt(100); // Generate a random number between 0 and 99

        System.out.println("Welcome to the Random Number Guessing Game!");
        System.out.println("Try to guess the number between 0 and 99.");

        int guess;
        boolean correct = false;

        while (!correct) {
            System.out.print("Enter your guess: ");
            guess = scanner.nextInt(); // Get user's guess

            if (guess == randomNumber) {
                System.out.println("Congratulations! You guessed the correct number.");
                correct = true;
            } else if (guess < randomNumber) {
                System.out.println("Too low! Try again.");
            } else {
                System.out.println("Too high! Try again.");
            }
        }

        scanner.close(); // Close the Scanner object
    }
}
