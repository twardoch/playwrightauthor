# Authentication Workflows

PlaywrightAuthor's key feature is maintaining persistent authentication sessions. This section provides practical guides for authenticating with common services.

## Overview

When using PlaywrightAuthor with a service that requires authentication:

1. **Browser Opens**: Chrome starts with a fresh profile
2. **Manual Login**: You log in manually—just once
3. **Session Saved**: Cookies and storage are saved automatically
4. **Future Runs**: Authentication happens automatically

## Service-Specific Guides

### Popular Services

- **[Gmail/Google](gmail.md)** – Handle 2FA, app passwords, and workspace accounts  
- **[GitHub](github.md)** – Personal access tokens and OAuth apps  
- **[LinkedIn](linkedin.md)** – Professional networking automation  
- **[Microsoft/Office 365](microsoft.md)** – Enterprise authentication  
- **[Facebook](facebook.md)** – Social media automation  
- **[Twitter/X](twitter.md)** – API alternatives  

### Enterprise Services

- **[Salesforce](salesforce.md)** – CRM automation  
- **[Slack](slack.md)** – Workspace automation  
- **[Jira/Confluence](atlassian.md)** – Project management  

## Best Practices

### Security

1. **Use Dedicated Accounts**: Where possible, create accounts specifically for automation  
2. **App Passwords**: Prefer app-specific passwords over primary credentials  
3. **2FA Workarounds**: Use backup codes or an authenticator app  
4. **Profile Isolation**: Keep different accounts in separate profiles  

### Reliability

1. **Test Authentication**: Run `playwrightauthor health` to verify login status  
2. **Monitor Sessions**: Watch for expired sessions and re-authenticate as needed  
3. **Backup Profiles**: Export important profiles for team use or recovery  
4. **Error Handling**: Add retry logic for unexpected authentication failures  

## Common Authentication Patterns

### Basic Login Flow

```python
from playwrightauthor import Browser

# First run - manual login required
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://example.com/login")
    print("Please log in manually...")
    input("Press Enter when logged in...")
```

### Multi-Step Authentication

```python
# Handle 2FA or multi-step login
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://secure-site.com")
    
    # Wait for login page
    page.wait_for_selector("input[name='username']")
    print("Enter credentials and complete 2FA...")
    
    # Wait for successful login (up to 5 minutes)
    page.wait_for_selector(".dashboard", timeout=300000)
    print("Login successful!")
```

### Profile Management

```python
# Use different profiles for different accounts
with Browser(profile="work") as browser:
    page = browser.new_page()
    page.goto("https://workspace.google.com")

with Browser(profile="personal") as browser:
    page = browser.new_page()
    page.goto("https://gmail.com")
```

## Troubleshooting

See the [Troubleshooting Guide](troubleshooting.md) for help with:

- Cookie and session problems  
- JavaScript errors  
- Popup blockers  
- Network issues  
- Platform-specific quirks  

## Tips

1. **First-Time Setup**: Run `playwrightauthor setup` for guided configuration  
2. **Health Checks**: Use `playwrightauthor health` to validate your setup  
3. **Debug Mode**: Set `PLAYWRIGHTAUTHOR_VERBOSE=true` for detailed logs  
4. **Manual Testing**: Use `playwrightauthor repl` for interactive debugging