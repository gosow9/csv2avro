package main

import (
	"bufio"
	"bytes"
	"flag"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strings"
	"time"
)

// Regular expressions to match potential sensitive data
var patterns = map[string]*regexp.Regexp{
	"Token":    regexp.MustCompile(`(?i)(token|bearer|apikey|secret)[=:]\s*['"]?[\w-]{10,}`),
	"Password": regexp.MustCompile(`(?i)password[=:]\s*['"]?[\w-]{8,}`),
	"Cert":     regexp.MustCompile(`(?i)(-----BEGIN CERTIFICATE-----|-----BEGIN PRIVATE KEY-----)`),
}

// CID pattern (e.g., emails, names, phone numbers)
var cidPatterns = map[string]*regexp.Regexp{
	"Email": regexp.MustCompile(`[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`),
	"Name":  regexp.MustCompile(`(?i)(first name|last name|full name)[=:]\s*['"]?[a-zA-Z\s]+`),
	//"Phone": regexp.MustCompile(`\+?[0-9]{1,3}[-.\s]?[(]?[0-9]{1,4}[)]?[-.\s]?[0-9]{1,4}[-.\s]?[0-9]{1,9}`),
}

var GOGO_CHECK = `

 ██████╗  ██████╗  ██████╗  ██████╗        ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗
██╔════╝ ██╔═══██╗██╔════╝ ██╔═══██╗      ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝
██║  ███╗██║   ██║██║  ███╗██║   ██║█████╗██║     ███████║█████╗  ██║     █████╔╝ 
██║   ██║██║   ██║██║   ██║██║   ██║╚════╝██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ 
╚██████╔╝╚██████╔╝╚██████╔╝╚██████╔╝      ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗
 ╚═════╝  ╚═════╝  ╚═════╝  ╚═════╝        ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝
                                                                                 
`

func main() {
	start := time.Now()

	// Define the flag to check for CID
	checkCID := flag.Bool("cid", true, "Check for client identifying data (email, phone, names)")
	flag.Parse()

	// Show the cool GOCHECK message
	fmt.Println(GOGO_CHECK)
	fmt.Println("\033[1;34mGOCHECK: Scanning files for sensitive information...\033[0m")

	// Get the files added to the current commit
	files, err := getAddedFiles()
	if err != nil {
		fmt.Println("\033[1;31mError fetching git files: \033[0m", err)
		os.Exit(1)
	}

	// Scan each file for sensitive data
	found := false
	for _, file := range files {
		if scanFile(file, *checkCID) {
			found = true
		}
	}

	// If sensitive information is found, abort the commit
	if found {
		duration := time.Since(start)
		fmt.Printf("\033[1;31mCommit halted due to sensitive information found in %s.\033[0m\n", duration)

		fmt.Println("\033[1;31mTo ignore this, press [y] to commit, or press [n] to abort commit:\033[0m")

		// Using fmt.Scanln to read user input
		var input string
		_, err := fmt.Scanln(&input)
		if err != nil {
			fmt.Println("\033[1;31mError reading input. Commit aborted.\033[0m")
			os.Exit(1) // Exit with status 1 to abort commit
		}

		// Handle user input
		switch strings.ToLower(input) {
		case "y":
			fmt.Println("Committing changes...")
		case "n":
			fmt.Println("Commit aborted.")
			os.Exit(1) // Exit with status 1 to abort commit
		default:
			fmt.Println("Invalid input. Commit aborted.")
			os.Exit(1)
		}
	}

	// Print the time it took to run the check
	duration := time.Since(start)
	fmt.Printf("\033[1;32mGOCHECK: All files scanned successfully in %s.\033[0m\n", duration)
}

// getAddedFiles returns the list of files added for the current commit
func getAddedFiles() ([]string, error) {
	cmd := exec.Command("git", "diff", "--cached", "--name-only", "--diff-filter=ACM")
	var out bytes.Buffer
	cmd.Stdout = &out
	err := cmd.Run()
	if err != nil {
		return nil, err
	}

	files := strings.Split(strings.TrimSpace(out.String()), "\n")
	return files, nil
}

// scanFile scans a file for sensitive information and returns true if any found
func scanFile(file string, checkCID bool) bool {
	found := false

	f, err := os.Open(file)
	if err != nil {
		fmt.Printf("\033[1;31mError opening file %s: %v\033[0m\n", file, err)
		return false
	}
	defer f.Close()

	scanner := bufio.NewScanner(f)
	lineNum := 0
	for scanner.Scan() {
		lineNum++
		line := scanner.Text()

		// Check for general sensitive data (Tokens, Passwords, Certs)
		for key, pattern := range patterns {
			if pattern.MatchString(line) {
				fmt.Printf("\033[1;31m%s found in %s at line %d: %s\033[0m\n", key, file, lineNum, strings.TrimSpace(line))
				found = true
			}
		}

		// Optionally check for CID data
		if checkCID {
			for key, pattern := range cidPatterns {
				if pattern.MatchString(line) {
					fmt.Printf("\033[1;31m%s found in %s at line %d: %s\033[0m\n", key, file, lineNum, strings.TrimSpace(line))
					found = true
				}
			}
		}
	}

	if err := scanner.Err(); err != nil {
		fmt.Printf("\033[1;31mError reading file %s: %v\033[0m\n", file, err)
	}

	return found
}
