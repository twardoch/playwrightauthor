# Authentication Workflows

PlaywrightAuthor's key feature is maintaining persistent authentication sessions. This section provides step-by-step guides for authenticating with popular services.

## 📋 Overview

When you first use PlaywrightAuthor with a service requiring authentication:

1. **Browser Opens**: Chrome launches with a clean profile
2. **Manual Login**: You log in manually (just once!)
3. **Session Saved**: Cookies and storage are persisted
4. **Future Runs**: Automatically authenticated

## 🔐 Service-Specific Guides

### Popular Services

- **[Gmail/Google](gmail.md)** - Handle 2FA, app passwords, and workspace accounts
- **[GitHub](github.md)** - Personal access tokens and OAuth apps
- **[LinkedIn](linkedin.md)** - Professional networking automation
- **[Microsoft/Office 365](microsoft.md)** - Enterprise authentication
- **[Facebook](facebook.md)** - Social media automation
- **[Twitter/X](twitter.md)** - API alternatives

### Enterprise Services

- **[Salesforce](salesforce.md)** - CRM automation
- **[Slack](slack.md)** - Workspace automation
- **[Jira/Confluence](atlassian.md)** - Project management

## 🎯 Best Practices

### Security

1. **Use Dedicated Accounts**: Create automation-specific accounts when possible
2. **App Passwords**: Use app-specific passwords instead of main credentials
3. **2FA Considerations**: Use backup codes or authentication apps
4. **Profile Isolation**: Use separate profiles for different accounts

### Reliability

1. **Test Authentication**: Use the `playwrightauthor health` command
2. **Monitor Sessions**: Check for expired sessions regularly
3. **Backup Profiles**: Export important profiles for team sharing
4. **Error Handling**: Implement retry logic for authentication failures

## 🔧 Common Authentication Patterns

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
    
    # Wait for successful login
    page.wait_for_selector(".dashboard", timeout=300000)  # 5 minutes
    print("Login successful!")
```

### Profile Management

```python
# Use different profiles for different accounts
with Browser(profile="work") as browser:
    # Work account
    page = browser.new_page()
    page.goto("https://workspace.google.com")

with Browser(profile="personal") as browser:
    # Personal account
    page = browser.new_page()
    page.goto("https://gmail.com")
```

## 🚨 Troubleshooting

See our comprehensive [Troubleshooting Guide](troubleshooting.md) for:

- Cookie and session issues
- JavaScript errors
- Popup blockers
- Network problems
- Platform-specific issues

## 💡 Tips

1. **First-Time Setup**: Run `playwrightauthor setup` for guided configuration
2. **Health Checks**: Use `playwrightauthor health` to validate setup
3. **Debug Mode**: Set `PLAYWRIGHTAUTHOR_VERBOSE=true` for detailed logs
4. **Manual Testing**: Use `playwrightauthor repl` for interactive debugging