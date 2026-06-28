#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys


REQUIRED_PACKAGES = {
    "PIL": "Pillow",
    "numpy": "numpy",
    "scipy": "scipy",
    "wordcloud": "wordcloud",
}


def find_missing_packages() -> list[str]:
    missing: list[str] = []
    for module_name, package_name in REQUIRED_PACKAGES.items():
        if importlib.util.find_spec(module_name) is None:
            missing.append(package_name)
    return missing


def build_install_command(missing: list[str], args: argparse.Namespace) -> list[str]:
    command = [sys.executable, "-m", "pip", "install"]
    if args.user:
        command.append("--user")
    if args.upgrade:
        command.append("--upgrade")
    command.extend(missing)
    return command


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check and optionally install Portrait Wordcloud dependencies.")
    parser.add_argument(
        "--install",
        action="store_true",
        help="Install missing packages after detecting them.",
    )
    parser.add_argument(
        "--user",
        action="store_true",
        help="Install packages into the current user's site-packages directory.",
    )
    parser.add_argument(
        "--upgrade",
        action="store_true",
        help="Pass --upgrade to pip when installing missing packages.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the install command without running it.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = find_missing_packages()

    if missing:
        print("Missing Python packages:")
        for package in missing:
            print(f"- {package}")

        install_command = build_install_command(missing, args)
        print("\nInstall command:")
        print(" ".join(install_command))

        if not args.install:
            print("\nRun this script again with --install after user approval.")
            return 1

        if args.dry_run:
            print("\nDry run only; no packages were installed.")
            return 1

        print("\nInstalling missing packages...")
        try:
            subprocess.check_call(install_command)
        except subprocess.CalledProcessError as exc:
            print(f"\nInstall failed with exit code {exc.returncode}.")
            return exc.returncode

        still_missing = find_missing_packages()
        if still_missing:
            print("\nInstall finished, but these packages are still unavailable:")
            for package in still_missing:
                print(f"- {package}")
            return 1

        print("\nEnvironment OK: missing packages were installed successfully.")
        return 0

    print("Environment OK: required Python packages are available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
