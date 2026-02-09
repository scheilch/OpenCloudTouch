#!/usr/bin/env python3
"""
Pre-commit hook: Validate Git user configuration.

Blocks commits if:
- user.name contains corporate ID patterns
- user.email is corporate email domain

Run: pre-commit install
"""
import subprocess
import sys
import re

def get_git_config(key):
    """Get git config value."""
    try:
        return subprocess.check_output(
            ["git", "config", key],
            stderr=subprocess.DEVNULL
        ).decode().strip()
    except subprocess.CalledProcessError:
        return None

def main():
    """Validate git user configuration."""
    user_name = get_git_config("user.name")
    user_email = get_git_config("user.email")

    # Blocked patterns
    blocked_name_patterns = [
        r'^T\d{5}[A-Z]$',  # Corporate ID format (letter + 5 digits + letter)
        r'^\d+$',           # Pure numbers
        r'^user\d+$',       # user123
    ]

    blocked_email_domains = [
        'example.de',
        'company.local',
    ]

    errors = []

    # Check name
    if user_name:
        for pattern in blocked_name_patterns:
            if re.match(pattern, user_name):
                errors.append(
                    f"❌ Git user.name '{user_name}' looks like a corporate ID!\n"
                    f"   Fix: git config user.name 'scheilch'"
                )
                break
    else:
        errors.append(
            "❌ Git user.name not set!\n"
            "   Fix: git config user.name 'scheilch'"
        )

    # Check email
    if user_email:
        domain = user_email.split('@')[-1] if '@' in user_email else None
        if domain in blocked_email_domains:
            errors.append(
                f"❌ Git user.email '{user_email}' is corporate!\n"
                f"   Fix: git config user.email 'christian@scheils.de'"
            )
    else:
        errors.append(
            "❌ Git user.email not set!\n"
            "   Fix: git config user.email 'christian@scheils.de'"
        )

    if errors:
        print("\n" + "="*60)
        print("🚫 COMMIT BLOCKED: Git Configuration Invalid")
        print("="*60)
        for error in errors:
            print(f"\n{error}")
        print("\n" + "="*60)
        print("💡 Recommended configuration:")
        print("   git config --local user.name 'scheilch'")
        print("   git config --local user.email 'christian@scheils.de'")
        print("="*60 + "\n")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
