package main

import "fmt"

func main() {
    calculator()
}

func calculator() {
    var num1, num2 float64
    var operator string
    var continueCalc string

    for {
        fmt.Println("Enter first number:")
        fmt.Scanln(&num1)

        fmt.Println("Enter operator (+, -, *, /):")
        fmt.Scanln(&operator)

        fmt.Println("Enter second number:")
        fmt.Scanln(&num2)

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
            } else {
                fmt.Printf("Result: %v\n", num1/num2)
            }
        default:
            fmt.Println("Invalid operator")
        }

        fmt.Println("Do you want to continue? (yes/no)")
        fmt.Scanln(&continueCalc)
        if continueCalc != "yes" {
            break
        }
    }
}