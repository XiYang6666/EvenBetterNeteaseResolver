#!/usr/bin/env python3
import subprocess


def main():
    subprocess.run(["pdm", "export", "--no-hashes", "-o", "requirements.txt"])
    subprocess.run(["git", "add", "requirements.txt"])


if __name__ == "__main__":
    main()
