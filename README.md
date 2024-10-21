Here's a `README.md` file that you can include with your Go program, detailing the purpose of the program, how to install it in a Git environment as a pre-commit hook, and how to use it.

```markdown
# GOCHECK - Pre-Commit Hook for Sensitive Information

GOCHECK is a Git pre-commit hook written in Go, designed to scan staged files for sensitive information such as tokens, passwords, certificates, and Client Identifying Data (CID) like emails or names. If sensitive data is found, the commit will be halted and the user will be given the option to either abort or force the commit.

## Features
- Scans staged files for sensitive data including:
  - API tokens, bearer tokens, and secrets.
  - Passwords.
  - Certificates (e.g., SSL certificates or private keys).
  - Client Identifying Data (CID) such as emails and names.
- Offers an interactive prompt to decide whether to proceed with the commit if sensitive data is detected.
- Optionally, force commit via command-line flag.

## Prerequisites

- **Go**: Make sure Go is installed. You can download it from [https://golang.org/dl/](https://golang.org/dl/).
- **Git**: This program is designed to be used as a pre-commit hook in a Git environment.

## Installation

1. **Build the Go Program**:

   First, clone or download the project to your local machine, then build the Go executable.

   ```bash
   git clone https://your-repo-url.git
   cd your-repo-directory

   # Build the Go executable
   go build -o precommit.exe
   ```

   This will generate the `precommit.exe` binary in the project directory.

2. **Set Up the Git Pre-Commit Hook**:

   To use this tool as a Git pre-commit hook, follow these steps:

   1. Navigate to your local Git repository:

      ```bash
      cd path/to/your/git/repository
      ```

   2. Create a `pre-commit` hook file inside the `.git/hooks/` directory (if it doesn't already exist):

      ```bash
      touch .git/hooks/pre-commit
      chmod +x .git/hooks/pre-commit
      ```

   3. Add the following script to the `.git/hooks/pre-commit` file:

      ```sh
      #!/bin/sh
      # Run the Go pre-commit tool
      echo "Running GOCHECK pre-commit hook..."

      # Ensure input is taken from terminal
      exec < /dev/tty 'C:/Users/Cedric/Documents/csv2avro/precommit.exe'
      ```

      Adjust the path to the `precommit.exe` to match the location where you've built the executable.

3. **Commit the Hook Script (Optional)**:
   
   If you'd like to share this pre-commit hook across the team, you can commit the hook as part of your repository by including it in a directory such as `scripts/` or `hooks/`. In this case, your teammates can set it up by copying it to their `.git/hooks/` directory.

4. **Ignore the Executable (Optional)**:

   It is a good idea to add the `precommit.exe` to your `.gitignore` file so that it doesn’t get committed to the repository.

   Add this line to your `.gitignore` file:

   ```bash
   precommit.exe
   ```

## Usage

Once the pre-commit hook is set up, it will automatically run every time you attempt to commit changes to the repository.

### Example

```bash
git add myfile.go
git commit -m "Add new feature"
```

If GOCHECK detects sensitive information, it will halt the commit and display a message like this:

```
Cert found in precommit.go at line 19: "Cert": SOME ERROR
Commit halted due to sensitive information found in 39.2703ms.
To ignore this, press [y] to commit, or press [n] to abort commit:
```

You can then decide whether to continue or abort the commit.

### Force Commit

If you know that the flagged data is not sensitive, you can force the commit by running the following:

```bash
git commit -m "My commit message" --no-verify
```

Alternatively, you can modify the `pre-commit` hook script to pass a `--force` flag to the Go program to force commit despite detected sensitive information:

```sh
'C:/Users/Cedric/Documents/csv2avro/precommit.exe' --force
```

## Development

If you wish to modify the program or contribute:

1. Clone the repository:

   ```bash
   git clone https://your-repo-url.git
   ```

2. Install dependencies (if needed):

   ```bash
   go mod tidy
   ```

3. Build the binary:

   ```bash
   go build -o precommit.exe
   ```

4. Test your changes by running the program directly:

   ```bash
   ./precommit.exe
   ```

## Contributing

Pull requests and issues are welcome! Please ensure that new code includes tests where appropriate and that the overall functionality of the pre-commit hook remains intact.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

### Key Points:
- It explains the purpose and functionality of the program.
- Provides clear instructions for building the Go binary and installing the pre-commit hook.
- Demonstrates how to use the program and manage interactive or forced commits.
