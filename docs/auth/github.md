# GitHub Authentication Guide

This guide covers authenticating with GitHub using PlaywrightAuthor for repository automation, API access, and CI/CD workflows.

## 📋 Prerequisites

Before starting:

1. **GitHub Account**: Ensure you have an active GitHub account
2. **2FA Setup**: Have your authenticator app or SMS ready if 2FA is enabled
3. **Personal Access Tokens**: Consider using PATs for enhanced security

## 🚀 Step-by-Step Authentication

### Step 1: Basic Authentication

```python
from playwrightauthor import Browser

# First run - manual login
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com/login")
    
    print("Please log in to GitHub...")
    print("Complete any 2FA requirements if prompted.")
    
    # Wait for successful login (dashboard or profile page)
    try:
        page.wait_for_selector('[aria-label="Dashboard"]', timeout=300000)
        print("✅ GitHub login successful!")
    except:
        # Alternative: wait for avatar menu
        page.wait_for_selector('summary[aria-label*="profile"]', timeout=300000)
        print("✅ GitHub login successful!")
```

### Step 2: Handling 2FA

```python
# Automated login with 2FA handling
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com/login")
    
    # Enter credentials
    page.fill('input[name="login"]', "your-username")
    page.fill('input[name="password"]', "your-password")
    page.click('input[type="submit"]')
    
    # Check if 2FA is required
    try:
        page.wait_for_selector('input[name="otp"]', timeout=5000)
        print("2FA required. Enter your code:")
        
        # Option 1: Manual entry
        code = input("Enter 2FA code: ")
        page.fill('input[name="otp"]', code)
        page.press('input[name="otp"]', "Enter")
        
        # Option 2: Wait for manual completion
        # print("Complete 2FA in the browser...")
        # page.wait_for_url("https://github.com/", timeout=120000)
        
    except:
        print("No 2FA required or already completed")
    
    print("✅ Authentication complete!")
```

### Step 3: Personal Access Token Setup

For automation, PATs are recommended:

```python
# Navigate to token creation
with Browser() as browser:
    page = browser.new_page()
    
    # Ensure we're logged in
    page.goto("https://github.com")
    
    # Go to token settings
    page.goto("https://github.com/settings/tokens/new")
    
    print("Create a Personal Access Token:")
    print("1. Give it a descriptive name")
    print("2. Set expiration (90 days recommended)")
    print("3. Select required scopes:")
    print("   - repo (for repository access)")
    print("   - workflow (for Actions)")
    print("   - read:org (for organization access)")
    
    # Wait for token generation
    page.wait_for_selector('input[id*="new_token"]', timeout=300000)
    
    # Get the token value
    token_input = page.query_selector('input[id*="new_token"]')
    if token_input:
        token = token_input.get_attribute("value")
        print(f"✅ Token generated: {token[:8]}...")
        print("⚠️  Save this token securely - you won't see it again!")
```

## 🔧 Advanced Scenarios

### Multiple GitHub Accounts

```python
# Personal account
with Browser(profile="github-personal") as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    # Already logged in as personal account

# Work account
with Browser(profile="github-work") as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    # Already logged in as work account
```

### GitHub Enterprise

```python
# For GitHub Enterprise Server
GITHUB_ENTERPRISE_URL = "https://github.company.com"

with Browser(profile="github-enterprise") as browser:
    page = browser.new_page()
    page.goto(f"{GITHUB_ENTERPRISE_URL}/login")
    
    # Handle SSO if required
    if "sso" in page.url:
        print("Complete SSO authentication...")
        page.wait_for_url(f"{GITHUB_ENTERPRISE_URL}/**", timeout=300000)
    
    print("✅ GitHub Enterprise authentication complete!")
```

### OAuth App Authorization

```python
# Authorize OAuth apps
def authorize_oauth_app(app_name: str, client_id: str):
    with Browser() as browser:
        page = browser.new_page()
        
        # Navigate to OAuth authorization
        auth_url = f"https://github.com/login/oauth/authorize?client_id={client_id}"
        page.goto(auth_url)
        
        # Check if already authorized
        if "callback" in page.url:
            print(f"✅ {app_name} already authorized")
            return
        
        # Click authorize button
        try:
            page.click('button[name="authorize"]')
            print(f"✅ {app_name} authorized successfully")
        except:
            print(f"❌ Could not authorize {app_name}")
```

## 🚨 Common Issues & Solutions

### Issue 1: "Device Verification" Required

**Symptoms**: GitHub requires device verification

**Solutions**:
```python
# Handle device verification
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com/login")
    
    # ... login steps ...
    
    # Check for device verification
    if "sessions/verified-device" in page.url:
        print("Device verification required!")
        print("Check your email for the verification code")
        
        code = input("Enter verification code: ")
        page.fill('input[name="otp"]', code)
        page.click('button[type="submit"]')
```

### Issue 2: Rate Limiting

**Symptoms**: "Too many requests" errors

**Solutions**:
```python
import time

# Add delays between requests
def github_action_with_delay(page, action):
    action()
    time.sleep(2)  # 2-second delay between actions

# Use authenticated requests
headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}
```

### Issue 3: Session Timeout

**Symptoms**: Frequent re-authentication required

**Solutions**:
```python
# Keep session alive
def keep_github_session_alive():
    with Browser() as browser:
        page = browser.new_page()
        
        while True:
            # Visit GitHub every 30 minutes
            page.goto("https://github.com/notifications")
            print("✅ Session refreshed")
            time.sleep(1800)  # 30 minutes
```

## 📊 Monitoring & Maintenance

### Check Authentication Status

```python
def check_github_auth():
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://github.com")
        
        # Check if logged in
        try:
            # Look for user avatar/menu
            avatar = page.query_selector('summary[aria-label*="profile"]')
            if avatar:
                username = avatar.get_attribute("aria-label")
                return True, f"Authenticated as: {username}"
            else:
                return False, "Not authenticated"
        except:
            return False, "Authentication check failed"

status, message = check_github_auth()
print(f"{'✅' if status else '❌'} {message}")
```

### Monitor API Rate Limits

```python
def check_rate_limits():
    with Browser() as browser:
        page = browser.new_page()
        
        # Check API rate limit
        response = page.goto("https://api.github.com/rate_limit")
        data = response.json()
        
        core_limit = data["resources"]["core"]
        print(f"API Rate Limit: {core_limit['remaining']}/{core_limit['limit']}")
        print(f"Resets at: {core_limit['reset']}")
```

## 🤖 Automation Examples

### Repository Management

```python
def create_repository(repo_name: str, private: bool = False):
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://github.com/new")
        
        # Fill repository details
        page.fill('input[name="repository[name]"]', repo_name)
        page.fill('input[name="repository[description]"]', 
                  "Created with PlaywrightAuthor")
        
        # Set visibility
        if private:
            page.click('input[value="private"]')
        
        # Create repository
        page.click('button[type="submit"]')
        
        # Wait for repository page
        page.wait_for_url(f"**/{repo_name}")
        print(f"✅ Repository '{repo_name}' created!")
```

### Pull Request Automation

```python
def review_pull_request(repo: str, pr_number: int, approve: bool = True):
    with Browser() as browser:
        page = browser.new_page()
        page.goto(f"https://github.com/{repo}/pull/{pr_number}")
        
        # Click review button
        page.click('button[name="review_button"]')
        
        # Add review comment
        page.fill('textarea[name="body"]', 
                  "Automated review via PlaywrightAuthor")
        
        # Approve or request changes
        if approve:
            page.click('input[value="approve"]')
        else:
            page.click('input[value="reject"]')
        
        # Submit review
        page.click('button[type="submit"]')
        print(f"✅ PR #{pr_number} reviewed!")
```

## 💡 Best Practices

1. **Use Personal Access Tokens** for automation instead of passwords
2. **Implement retry logic** for API calls and page interactions
3. **Respect rate limits** - add delays between operations
4. **Use dedicated bot accounts** for automation workflows
5. **Enable 2FA** but use backup codes for automation
6. **Monitor authentication status** regularly
7. **Rotate tokens** periodically for security

## 🔐 Security Considerations

1. **Never commit tokens** to repositories
2. **Use environment variables** for sensitive data:
   ```python
   import os
   GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
   ```
3. **Limit token scopes** to minimum required permissions
4. **Set token expiration** dates (90 days recommended)
5. **Use GitHub Secrets** for Actions workflows
6. **Monitor token usage** in GitHub settings

## 📚 Additional Resources

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [GitHub Actions](https://docs.github.com/en/actions)
- [PlaywrightAuthor Examples](https://github.com/twardoch/playwrightauthor/tree/main/examples)