#!/usr/bin/env python3
"""Monday.com agent self-registration via HATCHA + email verification.

Automates the full signup flow:
  1. Solve HATCHA (reverse CAPTCHA)
  2. Enter email address
  3. Set agent name and password
  4. Retrieve verification email (via gog or himalaya)
  5. Follow verification link
  6. Extract API token from the workspace

Requires:
  - Playwright (headless Chromium) — browser-full container variant
  - gog or himalaya — for reading the verification email

Usage:
  python3 register.py --email agent@example.com --agent-name "My Agent"
  python3 register.py --email agent@example.com --agent-name "My Agent" --password "SecureP4ss!"
  python3 register.py --email agent@example.com --agent-name "My Agent" --email-tool himalaya
"""

import argparse
import json
import os
import re
import secrets
import shutil
import string
import subprocess
import sys
import time
from typing import Optional

# Resolve hatcha module from the same directory.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import hatcha

SIGNUP_URL = "https://auth.monday.com/users/sign_up_new?custom_flow=agent_bot"
PAGE_LOAD_WAIT_MS = 10_000
POST_ACTION_WAIT_MS = 8_000


def generate_password(length: int = 16) -> str:
    """Generate a strong password meeting Monday.com requirements."""
    # Must have: 1 digit, 1 lowercase, 1 uppercase, 8+ chars,
    # no repeating (aaa) or consecutive (1234, abcd) characters.
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if (
            any(c.isdigit() for c in pw)
            and any(c.islower() for c in pw)
            and any(c.isupper() for c in pw)
            and not re.search(r"(.)\1\1", pw)  # no triple repeats
        ):
            return pw


def find_email_tool() -> str:
    """Detect which email CLI is available: gog or himalaya."""
    if shutil.which("gog"):
        return "gog"
    if shutil.which("himalaya"):
        return "himalaya"
    print("ERROR: Neither 'gog' nor 'himalaya' found on PATH.", file=sys.stderr)
    print("Install one to receive the verification email.", file=sys.stderr)
    sys.exit(1)


def fetch_verification_link(
    email_tool: str,
    email_address: str,
    max_attempts: int = 12,
    interval: int = 10,
) -> Optional[str]:
    """Poll inbox for the Monday.com verification email and extract the link."""
    print(f"\nWaiting for verification email (checking every {interval}s)...")

    for attempt in range(1, max_attempts + 1):
        print(f"  Attempt {attempt}/{max_attempts}...")
        try:
            if email_tool == "gog":
                result = subprocess.run(
                    [
                        "gog", "gmail", "messages", "search",
                        f"to:{email_address} from:monday.com newer_than:1d subject:verify",
                        "--max", "1", "--json",
                        "--account", email_address,
                    ],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0 and result.stdout.strip():
                    data = json.loads(result.stdout)
                    if data:
                        msg_id = data[0].get("id") or data[0].get("Id")
                        if msg_id:
                            body_result = subprocess.run(
                                [
                                    "gog", "gmail", "messages", "get", msg_id,
                                    "--account", email_address, "--json",
                                ],
                                capture_output=True, text=True, timeout=30,
                            )
                            if body_result.returncode == 0:
                                link = _extract_link(body_result.stdout)
                                if link:
                                    return link
            else:
                # himalaya
                result = subprocess.run(
                    [
                        "himalaya", "envelope", "list",
                        "--output", "json",
                        "--page-size", "5",
                    ],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0 and result.stdout.strip():
                    envelopes = json.loads(result.stdout)
                    for env in envelopes:
                        subj = env.get("subject", "")
                        if "monday" in subj.lower() or "verify" in subj.lower():
                            msg_id = str(env.get("id", ""))
                            if msg_id:
                                body_result = subprocess.run(
                                    ["himalaya", "message", "read", msg_id],
                                    capture_output=True, text=True, timeout=30,
                                )
                                if body_result.returncode == 0:
                                    link = _extract_link(body_result.stdout)
                                    if link:
                                        return link
        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError) as e:
            print(f"    Warning: {e}")

        if attempt < max_attempts:
            time.sleep(interval)

    return None


def _extract_link(text: str) -> Optional[str]:
    """Extract a Monday.com verification/confirmation URL from email body."""
    patterns = [
        r'(https://auth\.monday\.com/[^\s"<>]+(?:confirm|verify|accept)[^\s"<>]*)',
        r'(https://[^\s"<>]*monday\.com[^\s"<>]*(?:confirm|verify|token|accept)[^\s"<>]*)',
    ]
    for pat in patterns:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            return m.group(1)
    return None


def register(
    email: str,
    agent_name: str,
    password: Optional[str] = None,
    email_tool: Optional[str] = None,
) -> dict:
    """Run the full Monday.com agent registration flow.

    Returns a dict with keys: success, token (if obtained), url, message.
    """
    if not password:
        password = generate_password()
        print(f"Generated password: {password}")

    if not email_tool:
        email_tool = find_email_tool()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            "success": False,
            "message": "Playwright is not installed. Run: pip install playwright && playwright install chromium",
        }

    result = {"success": False, "token": None, "url": None, "message": ""}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # --- Step 1: HATCHA ---
        print("\n==> Step 1: Solving HATCHA challenge...")
        page.goto(SIGNUP_URL, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_timeout(PAGE_LOAD_WAIT_MS)

        body_text = page.inner_text("body")
        answer = hatcha.solve(body_text)
        if not answer:
            result["message"] = f"Could not solve HATCHA challenge:\n{body_text[:500]}"
            browser.close()
            return result

        print(f"    Challenge solved: {answer}")

        text_input = page.query_selector('input[type="text"]')
        if not text_input:
            result["message"] = "No answer input found on HATCHA page."
            browser.close()
            return result

        text_input.fill(answer)
        verify_btn = page.query_selector('button:has-text("Verify")')
        if not verify_btn:
            result["message"] = "No Verify button found."
            browser.close()
            return result

        verify_btn.click()
        page.wait_for_timeout(POST_ACTION_WAIT_MS)

        body_text = page.inner_text("body")
        if "welcome" not in body_text.lower() and "email" not in body_text.lower():
            result["message"] = f"HATCHA verification failed:\n{body_text[:500]}"
            browser.close()
            return result
        print("    HATCHA passed.")

        # --- Step 2: Email ---
        print(f"\n==> Step 2: Entering email: {email}")
        email_input = page.query_selector(
            'input[type="email"], input[placeholder*="email"], input[placeholder*="@"]'
        )
        if not email_input:
            for inp in page.query_selector_all("input"):
                if inp.is_visible():
                    itype = inp.get_attribute("type") or ""
                    if itype not in ("hidden", "submit", "button", "checkbox", "radio"):
                        email_input = inp
                        break

        if not email_input:
            result["message"] = "No email input found."
            browser.close()
            return result

        email_input.fill(email)

        signup_btn = page.query_selector('button:has-text("Sign up")')
        if not signup_btn:
            result["message"] = "No 'Sign up' button found."
            browser.close()
            return result

        signup_btn.click()
        page.wait_for_timeout(POST_ACTION_WAIT_MS)
        print("    Email submitted.")

        # --- Step 3: Agent name + password ---
        body_text = page.inner_text("body")
        print(f"\n==> Step 3: Setting agent name and password...")

        if "agent name" not in body_text.lower() and "password" not in body_text.lower():
            # Might have gone straight to email verification
            print(f"    Unexpected page state:\n{body_text[:500]}")
        else:
            # Fill agent name
            name_input = page.query_selector('input[type="text"]')
            if name_input and name_input.is_visible():
                name_input.fill(agent_name)
                print(f"    Agent name: {agent_name}")

            # Fill password
            pass_input = page.query_selector('input[type="password"]')
            if pass_input and pass_input.is_visible():
                pass_input.fill(password)
                print("    Password set.")

            complete_btn = page.query_selector('button:has-text("Complete")')
            if complete_btn:
                complete_btn.click()
                page.wait_for_timeout(POST_ACTION_WAIT_MS)
                print("    Signup submitted.")

        body_text = page.inner_text("body")
        result["url"] = page.url
        print(f"    Current URL: {page.url}")
        print(f"    Page says: {body_text[:300]}")

        # --- Step 4: Email verification ---
        if "verify" in body_text.lower() or "check" in body_text.lower() or "confirm" in body_text.lower():
            print(f"\n==> Step 4: Retrieving verification email via {email_tool}...")
            link = fetch_verification_link(email_tool, email)
            if link:
                print(f"    Verification link: {link}")
                page.goto(link, wait_until="domcontentloaded", timeout=30_000)
                page.wait_for_timeout(POST_ACTION_WAIT_MS)
                body_text = page.inner_text("body")
                result["url"] = page.url
                print(f"    After verification: {body_text[:300]}")
            else:
                result["message"] = (
                    "Could not find verification email. "
                    "Check inbox manually and follow the link."
                )
                browser.close()
                return result

        # --- Step 5: Extract API token ---
        print("\n==> Step 5: Attempting to extract API token...")

        # Try navigating to the developer/API section
        for token_url in [
            "https://auth.monday.com/admin/integrations/api",
            page.url,  # might already be on the right page
        ]:
            if "api" in token_url.lower() or "developer" in token_url.lower():
                page.goto(token_url, wait_until="domcontentloaded", timeout=30_000)
                page.wait_for_timeout(5_000)

        body_text = page.inner_text("body")
        # Look for a token pattern (long alphanumeric string)
        token_match = re.search(r"(eyJ[A-Za-z0-9_-]{50,})", body_text)
        if token_match:
            result["token"] = token_match.group(1)
            print(f"    Token found: {result['token'][:20]}...")
        else:
            print("    Token not found on page. Retrieve manually from:")
            print("    Monday.com > Avatar > Developers > My access tokens")

        result["success"] = True
        result["message"] = "Registration complete."
        result["url"] = page.url

        browser.close()

    # Print summary
    print("\n" + "=" * 50)
    print("REGISTRATION SUMMARY")
    print("=" * 50)
    print(f"  Email:      {email}")
    print(f"  Agent name: {agent_name}")
    print(f"  Password:   {password}")
    if result["token"]:
        print(f"  API Token:  {result['token'][:20]}...")
        print(f"\n  export MONDAY_API_TOKEN=\"{result['token']}\"")
    else:
        print("  API Token:  Not extracted — retrieve from Monday.com settings.")
    print(f"  URL:        {result['url']}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Register an AI agent on Monday.com via HATCHA."
    )
    parser.add_argument("--email", required=True, help="Email address for signup")
    parser.add_argument("--agent-name", required=True, help="Display name for the agent")
    parser.add_argument("--password", help="Account password (generated if omitted)")
    parser.add_argument(
        "--email-tool",
        choices=["gog", "himalaya"],
        help="Email CLI to use for verification (auto-detected if omitted)",
    )
    args = parser.parse_args()

    result = register(
        email=args.email,
        agent_name=args.agent_name,
        password=args.password,
        email_tool=args.email_tool,
    )

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

