#include <iostream>
#include <cstdlib>
#include <ctime>

int main() {
    // Seed the random number generator with the current time
    std::srand(static_cast<unsigned int>(std::time(0)));
    
    // Generate a random number between 1 and 100
    int secretNumber = std::rand() % 100 + 1;
    int playerGuess = 0;
    int attempts = 0;

    std::cout << "=================================\n";
    std::cout << "  Welcome to the Guessing Game!  \n";
    std::cout << "=================================\n";
    std::cout << "I have chosen a number between 1 and 100.\n";
    std::cout << "Can you guess what it is?\n\n";

    // Loop until the player guesses the correct number
    while (playerGuess != secretNumber) {
        std::cout << "Enter your guess: ";
        std::cin >> playerGuess;
        attempts++;

        if (playerGuess > secretNumber) {
            std::cout << "Too high! Try again.\n\n";
        } else if (playerGuess < secretNumber) {
            std::cout << "Too low! Try again.\n\n";
        } else {
            std::cout << "\n🎉 Congratulations! You got it!\n";
            std::cout << "The secret number was " << secretNumber << ".\n";
            std::cout << "It took you " << attempts << " attempts.\n";
        }
    }

    std::cout << "=================================\n";
    std::cout << "Thanks for playing! Game Over.\n";
    
    return 0;
}