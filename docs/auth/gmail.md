# Gmail/Google Authentication Guide

This guide shows how to authenticate with Gmail and Google services using PlaywrightAuthor.

## Prerequisites

Before starting:

1. **Disable "Less Secure Apps"**: Not needed - we use full browser automation
2. **2FA Considerations**: Have your phone or authenticator app ready
3. **Browser Permissions**: Ensure Chrome has necessary permissions (especially on macOS)

## Authentication Steps

### Step 1: Initial Setup

```python
from playwrightauthor import Browser

# First run - launches Chrome for manual login
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    
    print("Please complete the login process...")
    print("The browser will stay open until you're logged in.")
    
    # Wait for successful login (inbox appears)
    try:
        page.wait_for_selector('div[role="main"]', timeout=300000)  # 5 minutes
        print("Login successful!")
    except:
        print("Login timeout - please try again")
```

### Step 2: Handling 2FA

If you have 2FA enabled:

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://accounts.google.com")
    
    # Enter email
    page.fill('input[type="email"]', "your.email@gmail.com")
    page.click("#identifierNext")
    
    # Enter password
    page.wait_for_selector('input[type="password"]', timeout=10000)
    page.fill('input[type="password"]', "your_password")
    page.click("#passwordNext")
    
    print("Complete 2FA verification in the browser...")
    
    # Wait for successful authentication
    page.wait_for_url("**/myaccount.google.com/**", timeout=120000)
    print("2FA completed successfully!")
```

### Step 3: Verify Persistent Login

```python
# Run this after initial login to verify persistence
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    
    # Should load directly to inbox without login
    if page.url.startswith("https://mail.google.com/mail/"):
        print("Authentication persisted successfully!")
    else:
        print("Authentication not persisted - please login again")
```

## Advanced Scenarios

### Multiple Google Accounts

```python
# Work account
with Browser(profile="work") as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    # Login with work@company.com

# Personal account  
with Browser(profile="personal") as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
    # Login with personal@gmail.com
```

### Google Workspace (G Suite)

```python
# For custom domain emails
with Browser() as browser:
    page = browser.new_page()
    
    # Go directly to your domain's login
    page.goto("https://accounts.google.com/AccountChooser"
              "?Email=user@yourdomain.com"
              "&continue=https://mail.google.com")
    
    # Complete SSO if required
    print("Complete your organization's login process...")
```

### App Passwords

For automation, consider using App Passwords:

1. Enable 2FA on your Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app-specific password
4. Use it in your automation scripts

## Common Issues

### Issue 1: "Couldn't sign you in" Error

**Symptoms**: Google blocks the login attempt

**Solutions**:
1. Run `playwrightauthor setup` for guided configuration
2. Try logging in manually first
3. Check if your IP is trusted by Google
4. Use the same network as your regular browser

### Issue 2: Captcha Challenges

**Symptoms**: Repeated captcha requests

**Solutions**:
```python
# Add delays to appear more human-like
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://accounts.google.com")
    
    # Add realistic delays
    page.wait_for_timeout(2000)  # 2 seconds
    page.fill('input[type="email"]', "email@gmail.com")
    page.wait_for_timeout(1000)
    page.click("#identifierNext")
```

### Issue 3: Session Expires Frequently

**Symptoms**: Need to re-login often

**Solutions**:
1. Check Chrome flags: `chrome://flags`
2. Ensure cookies aren't being cleared
3. Verify profile persistence:

```python
# Check profile location
import os
from playwrightauthor.utils.paths import data_dir

profile_path = data_dir() / "profiles" / "default"
print(f"Profile stored at: {profile_path}")
print(f"Profile exists: {profile_path.exists()}")
```

### Issue 4: 2FA Problems

**Symptoms**: Can't complete 2FA

**Solutions**:
1. Use backup codes for automation
2. Set up a dedicated automation account
3. Use Google's Advanced Protection for better security

## Monitoring

### Check Authentication Status

```python
from playwrightauthor import Browser

def check_gmail_auth():
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://mail.google.com", wait_until="domcontentloaded")
        
        # Check if redirected to login
        if "accounts.google.com" in page.url:
            return False, "Not authenticated"
        elif "mail.google.com/mail/" in page.url:
            # Get account email
            try:
                email_element = page.query_selector('[aria-label*="Google Account"]')
                email = email_element.get_attribute("aria-label")
                return True, f"Authenticated as: {email}"
            except:
                return True, "Authenticated (email unknown)"
        else:
            return False, f"Unknown state: {page.url}"

status, message = check_gmail_auth()
print(f"{'✓' if status else '✗'} {message}")
```

### Export/Import Profile

```bash
# Export profile for backup or sharing
playwrightauthor profile export work --output work-profile.zip

# Import on another machine
playwrightauthor profile import work --input work-profile.zip
```

## Best Practices

1. **Dedicated Accounts**: Use separate Google accounts for automation
2. **Regular Checks**: Monitor authentication status weekly
3. **Backup Profiles**: Export working profiles regularly
4. **Error Handling**: Always implement retry logic
5. **Rate Limiting**: Add delays between actions to avoid detection

## Security

1. **Never hardcode passwords** in your scripts
2. **Use environment variables** for sensitive data
3. **Encrypt profile exports** when sharing
4. **Regularly rotate** app passwords
5. **Monitor account activity** for unauthorized access

## Resources

- [Google Account Security](https://myaccount.google.com/security)
- [App Passwords Guide](https://support.google.com/accounts/answer/185833)
- [Google Workspace Admin](https://admin.google.com)
- [PlaywrightAuthor Troubleshooting](troubleshooting.md)