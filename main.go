package main

import (
	"fmt"
	"strings"
)

func main() {
	calculator()
}

func calculator() {
	var continueCalc string

	for {
		var num1, num2 float64
		var operator string

		fmt.Println("Enter first number:")
		if _, err := fmt.Scanln(&num1); err != nil {
			fmt.Println("Invalid number")
			// Clear input buffer
			var discard string
			fmt.Scanln(&discard)
			continue
		}

		fmt.Println("Enter operator (+, -, *, /):")
		if _, err := fmt.Scanln(&operator); err != nil {
			fmt.Println("Invalid operator")
			var discard string
			fmt.Scanln(&discard)
			continue
		}

		fmt.Println("Enter second number:")
		if _, err := fmt.Scanln(&num2); err != nil {
			fmt.Println("Invalid number")
			var discard string
			fmt.Scanln(&discard)
			continue
		}

		switch operator {
		case "+":
			fmt.Printf("Result: %v\n", num1+num2)
		case "-":
			fmt.Printf("Result: %v\n", num1-num2)
		case "*":
			fmt.Printf("Result: %v\n", num1*num2)
		case "/":
			if num2 == 0 {
				fmt.Println("Error: Division by zero")
				continue // Skip result display
			}
			fmt.Printf("Result: %v\n", num1/num2)
		default:
			fmt.Println("Invalid operator")
			continue
		}

		fmt.Println("Do you want to continue? (yes/no)")
		if _, err := fmt.Scanln(&continueCalc); err != nil {
			fmt.Println("Invalid input")
			var discard string
			fmt.Scanln(&discard)
			continue
		}

		if strings.ToLower(continueCalc) != "yes" {
			break
		}
	}
}
