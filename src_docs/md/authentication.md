# Authentication

PlaywrightAuthor handles authentication through persistent browser profiles and guided workflows. No need to log in every time you run automation.

## How Authentication Works

PlaywrightAuthor stores login sessions in Chrome user profiles:

1. **Profile Persistence**: Login data saves to a Chrome user profile
2. **Session Reuse**: Later runs use the existing session
3. **Guided Setup**: Interactive help for first-time authentication
4. **Cross-Site Support**: Works with any site that uses persistent cookies

## Basic Authentication Setup

### First-Time Setup

```python
from playwrightauthor import Browser

# First run - will guide you through login
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com/login")
    
    # PlaywrightAuthor detects if you're logged in
    # and shows login guidance if needed
```

### Check Authentication Status

```python
from playwrightauthor import Browser
from playwrightauthor.auth import is_authenticated

with Browser() as browser:
    page = browser.new_page()
    page.goto("https://github.com")
    
    if is_authenticated(page, site="github"):
        print("Already logged in")
    else:
        print("Login required")
        # Start setup flow
```

## Onboarding Workflow

### Interactive Setup

When login is needed, PlaywrightAuthor walks you through it:

```python
from playwrightauthor import Browser
from playwrightauthor.onboarding import OnboardingManager

with Browser() as browser:
    onboarding = OnboardingManager(browser)
    
    # Start GitHub login guide
    success = onboarding.guide_authentication(
        site="github",
        target_url="https://github.com/settings/profile"
    )
    
    if success:
        print("Login saved")
```

### Onboarding Page Template

PlaywrightAuthor serves this local page for setup:

```html
<!-- http://localhost:8080/onboarding -->
<!DOCTYPE html>
<html>
<head>
    <title>PlaywrightAuthor - Authentication Setup</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .step { margin: 20px 0; padding: 15px; border-left: 4px solid #007acc; }
        .success { border-color: #28a745; background: #f8fff9; }
    </style>
</head>
<body>
    <h1>Authentication Setup</h1>
    <div class="step">
        <h3>Step 1: Login</h3>
        <p>A browser window opens. Log in normally.</p>
    </div>
    <div class="step">
        <h3>Step 2: Verify</h3>
        <p>Go to a protected page to confirm login.</p>
    </div>
    <div class="step success">
        <h3>Step 3: Done</h3>
        <p>Your session saves for future runs.</p>
    </div>
</body>
</html>
```

## Site-Specific Authentication

### GitHub

```python
from playwrightauthor import Browser
from playwrightauthor.auth.github import GitHubAuth

with Browser() as browser:
    github_auth = GitHubAuth(browser)
    
    if not github_auth.is_authenticated():
        github_auth.authenticate()
    
    page = browser.new_page()
    page.goto("https://github.com/settings/profile")
    
    name = page.input_value("#user_profile_name")
    print(f"GitHub user: {name}")
```

### Gmail

```python
from playwrightauthor import Browser
from playwrightauthor.auth.gmail import GmailAuth

with Browser() as browser:
    gmail_auth = GmailAuth(browser)
    
    if not gmail_auth.is_authenticated():
        gmail_auth.authenticate()
    
    page = browser.new_page()
    page.goto("https://mail.google.com")
    
    page.wait_for_selector("[data-tooltip='Compose']")
    page.click("[data-tooltip='Compose']")
```

### LinkedIn

```python
from playwrightauthor import Browser
from playwrightauthor.auth.linkedin import LinkedInAuth

with Browser() as browser:
    linkedin_auth = LinkedInAuth(browser)
    
    if not linkedin_auth.is_authenticated():
        linkedin_auth.authenticate()
    
    page = browser.new_page()
    page.goto("https://www.linkedin.com/feed/")
    
    page.wait_for_selector("[data-test-id='feed-tab']")
```

## Custom Authentication

### Custom Site Handler

```python
from playwrightauthor import Browser
from playwrightauthor.auth import BaseAuth

class CustomSiteAuth(BaseAuth):
    def __init__(self, browser, site_url: str):
        super().__init__(browser)
        self.site_url = site_url
    
    def is_authenticated(self) -> bool:
        page = self.browser.new_page()
        page.goto(self.site_url)
        
        login_button = page.query_selector("text=Login")
        user_menu = page.query_selector("[data-testid='user-menu']")
        
        page.close()
        return user_menu is not None and login_button is None
    
    def authenticate(self) -> bool:
        if self.is_authenticated():
            return True
        
        page = self.browser.new_page()
        page.goto(f"{self.site_url}/login")
        
        self._wait_for_authentication(page)
        return self.is_authenticated()
    
    def _wait_for_authentication(self, page):
        print("Complete login in browser...")
        
        try:
            page.wait_for_selector("[data-testid='user-menu']", timeout=300000)
            print("Login successful")
        except TimeoutError:
            print("Login timed out")

with Browser() as browser:
    auth = CustomSiteAuth(browser, "https://example.com")
    auth.authenticate()
```

### Multi-Factor Authentication

```python
from playwrightauthor import Browser
from playwrightauthor.auth import MFAHandler

class MFAAuth:
    def __init__(self, browser):
        self.browser = browser
        self.mfa_handler = MFAHandler()
    
    def handle_mfa_flow(self, page):
        if page.query_selector("text=Enter verification code"):
            return self._handle_code_verification(page)
        elif page.query_selector("text=Use your authenticator app"):
            return self._handle_app_verification(page)
        elif page.query_selector("text=Check your phone"):
            return self._handle_sms_verification(page)
        return True
    
    def _handle_code_verification(self, page):
        print("Enter verification code in browser")
        
        page.wait_for_function(
            "document.querySelector('[name=verification_code]').value.length >= 6"
        )
        
        page.click("button[type=submit]")
        return True
    
    def _handle_app_verification(self, page):
        print("Use authenticator app")
        page.wait_for_url("**/dashboard", timeout=120000)
        return True

with Browser() as browser:
    mfa_auth = MFAAuth(browser)
    
    page = browser.new_page()
    page.goto("https://secure-site.com/login")
    
    page.fill("#username", "your_username")
    page.fill("#password", "your_password")
    page.click("#login-button")
    
    mfa_auth.handle_mfa_flow(page)
```

## Profile Management

### Named Profiles

```python
from playwrightauthor import Browser, BrowserConfig
from pathlib import Path

def create_auth_profile(profile_name: str):
    profile_dir = Path.home() / ".playwrightauthor" / "profiles" / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)
    return BrowserConfig(user_data_dir=str(profile_dir))

github_config = create_auth_profile("github_work")
gmail_config = create_auth_profile("gmail_personal")

with Browser(config=github_config) as browser:
    page = browser.new_page()
    page.goto("https://github.com/settings")

with Browser(config=gmail_config) as browser:
    page = browser.new_page()
    page.goto("https://mail.google.com")
```

### Switch Profiles

```python
from playwrightauthor.auth import ProfileManager

profile_manager = ProfileManager()

profiles = {
    "work": "/path/to/work/profile",
    "personal": "/path/to/personal/profile"
}

for name, path in profiles.items():
    config = BrowserConfig(user_data_dir=path)
    
    with Browser(config=config) as browser:
        print(f"Using {name} profile")
        page = browser.new_page()
        page.goto("https://github.com")
        
        if page.query_selector("[data-testid='header-user-menu']"):
            user = page.text_content("[data-testid='header-user-menu'] img")
            print(f"Logged in as: {user}")
```

## Session Validation

### Check Session Health

```python
from playwrightauthor.auth import SessionValidator

class SessionValidator:
    def __init__(self, browser):
        self.browser = browser
    
    def validate_session(self, site: str) -> bool:
        validators = {
            "github": self._validate_github_session,
            "gmail": self._validate_gmail_session
        }
        
        validator = validators.get(site)
        return validator() if validator else False
    
    def _validate_github_session(self) -> bool:
        page = self.browser.new_page()
        page.goto("https://api.github.com/user")
        
        is_valid = "login" in page.text_content("body")
        page.close()
        return is_valid
    
    def refresh_session_if_needed(self, site: str):
        if not self.validate_session(site):
            print(f"Session expired for {site}, re-authenticating...")
            
            auth_handlers = {
                "github": GitHubAuth,
                "gmail": GmailAuth
            }
            
            auth_class = auth_handlers.get(site)
            if auth_class:
                auth = auth_class(self.browser)
                auth.authenticate()

with Browser() as browser:
    validator = SessionValidator(browser)
    validator.refresh_session_if_needed("github")
    
    page = browser.new_page()
    page.goto("https://github.com/settings")
```

## Security Practices

### Secure Profile Storage

```python
import os
from pathlib import Path
from playwrightauthor import BrowserConfig

def create_secure_profile(profile_name: str):
    profile_dir = Path.home() / ".playwrightauthor" / "profiles" / profile_name
    profile_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(profile_dir, 0o700)  # Owner read/write only
    return BrowserConfig(user_data_dir=str(profile_dir))
```

### Environment Configuration

```python
import os
from playwrightauthor import Browser, BrowserConfig

def get_auth_config():
    profile_path = os.getenv("PLAYWRIGHT_PROFILE_PATH")
    if not profile_path:
        raise ValueError("PLAYWRIGHT_PROFILE_PATH required")
    return BrowserConfig(user_data_dir=profile_path)

config = get_auth_config()
with Browser(config=config) as browser:
    pass
```

### Credential Management

```python
from playwrightauthor.auth import CredentialManager

class CredentialManager:
    def __init__(self):
        self.credentials = {}
    
    def store_credential(self, site: str, username: str, encrypted_token: str):
        self.credentials[site] = {
            "username": username,
            "token": encrypted_token,
            "expires_at": None
        }
    
    def get_credential(self, site: str):
        return self.credentials.get(site)
    
    def is_credential_valid(self, site: str) -> bool:
        cred = self.get_credential(site)
        if not cred:
            return False
        
        if cred.get("expires_at"):
            from datetime import datetime
            return datetime.now() < cred["expires_at"]
        
        return True
```

## Troubleshooting

### Common Issues

1. **Session Expired**:
```python
try:
    page.goto("https://secure-site.com/protected")
    if "login" in page.url:
        auth.authenticate()
        page.goto("https://secure-site.com/protected")
except Exception as e:
    print(f"Auth error: {e}")
```

2. **Profile Corrupted**:
```python
from playwrightauthor.auth import ProfileRepair

repair = ProfileRepair()
if repair.is_profile_corrupted(profile_path):
    repair.backup_profile(profile_path)
    repair.create_fresh_profile(profile_path)
```

3. **Cookie Problems**:
```python
# Clear cookies for specific site
page.context.clear_cookies(url="https://problematic-site.com")

# Or clear all cookies
page.context.clear_cookies()
```

## Next Steps

- See [Advanced Features](advanced-features.md) for complex auth cases
- Check [Troubleshooting](troubleshooting.md) for auth issues
- Review [API Reference](api-reference.md) for auth methods
- Learn [Browser Management](browser-management.md) for profile handling