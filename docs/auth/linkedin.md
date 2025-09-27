# LinkedIn Authentication Guide

This guide covers authenticating with LinkedIn using PlaywrightAuthor for professional networking automation, lead generation, and content management.

## Prerequisites

Before starting:

1. **LinkedIn Account**: Active account in good standing
2. **Security Verification**: Phone number or email for two-factor authentication
3. **Rate Limits**: Understand LinkedIn's automation restrictions

**Important**: LinkedIn actively blocks automation. Use carefully and consider official APIs for production applications.

## Authentication Process

### Basic Login

```python
from playwrightauthor import Browser

# First run - manual login
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://www.linkedin.com/login")
    
    print("Log in to LinkedIn manually")
    print("Complete security challenges if prompted")
    
    # Wait for successful login
    try:
        page.wait_for_selector('[data-test-id="feed"]', timeout=300000)
        print("Login successful")
    except:
        # Fallback check
        page.wait_for_selector('nav[aria-label="Primary"]', timeout=300000)
        print("Login successful")
```

### Automated Login with Security Handling

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://www.linkedin.com/login")
    
    # Enter credentials
    page.fill('#username', "your-email@example.com")
    page.fill('#password', "your-password")
    page.click('button[type="submit"]')
    
    # Handle verification code
    try:
        page.wait_for_selector('input[name="pin"]', timeout=5000)
        print("Verification required")
        
        code = input("Enter code from email/phone: ")
        page.fill('input[name="pin"]', code)
        page.click('button[type="submit"]')
        
    except:
        print("No verification required")
    
    # Confirm login
    page.wait_for_selector('[data-test-id="feed"]', timeout=30000)
    print("Authentication complete")
```

### Remember Device Setup

```python
# Reduce future security prompts
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://www.linkedin.com/login")
    
    # Complete login process first
    
    try:
        remember_checkbox = page.query_selector('input[type="checkbox"][name="rememberMe"]')
        if remember_checkbox:
            page.click('input[type="rememberMe"]')
            print("Device will be remembered")
    except:
        pass
```

## Advanced Authentication

### Multiple Account Management

```python
# Personal profile
with Browser(profile="linkedin-personal") as browser:
    page = browser.new_page()
    page.goto("https://www.linkedin.com/feed")

# Company page management
with Browser(profile="linkedin-company") as browser:
    page = browser.new_page()
    page.goto("https://www.linkedin.com/company/admin")
```

### Sales Navigator Access

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://www.linkedin.com/sales")
    
    try:
        page.wait_for_selector('[data-test="sales-nav-logo"]', timeout=10000)
        print("Sales Navigator access confirmed")
    except:
        print("Sales Navigator subscription required")
```

### LinkedIn Learning Access

```python
with Browser() as browser:
    page = browser.new_page()
    page.goto("https://www.linkedin.com/learning")
    
    if "learning" in page.url:
        print("LinkedIn Learning accessible")
    else:
        print("LinkedIn Learning subscription required")
```

## Common Problems

### Suspicious Activity Blocks

LinkedIn may block logins that appear automated:

```python
import time
import random

with Browser() as browser:
    page = browser.new_page()
    
    # Human-like delays
    time.sleep(random.uniform(2, 5))
    page.goto("https://www.linkedin.com/login")
    
    time.sleep(random.uniform(1, 3))
    page.fill('#username', "email@example.com")
    
    time.sleep(random.uniform(1, 2))
    page.fill('#password', "password")
    
    time.sleep(random.uniform(1, 2))
    page.click('button[type="submit"]')
```

### CAPTCHA Challenges

```python
def handle_captcha(page):
    try:
        page.wait_for_selector('iframe[src*="captcha"]', timeout=3000)
        print("CAPTCHA detected. Solve manually.")
        
        page.wait_for_selector('[data-test-id="feed"]', timeout=300000)
        print("CAPTCHA solved. Continuing.")
        
    except:
        pass  # No CAPTCHA
```

### Account Restrictions

When LinkedIn limits your access:
1. Reduce automation frequency
2. Increase delays between actions
3. Vary activity patterns
4. Use official LinkedIn APIs

## Status Monitoring

### Authentication Check

```python
def check_linkedin_auth():
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://www.linkedin.com/feed")
        
        if "login" in page.url:
            return False, "Not authenticated"
        
        try:
            page.click('[data-control-name="nav.settings_signout"]')
            name_element = page.query_selector('.t-16.t-black.t-bold')
            if name_element:
                name = name_element.inner_text()
                return True, f"Authenticated as: {name}"
        except:
            pass
        
        return True, "Authenticated"

status, message = check_linkedin_auth()
print(message)
```

### Activity Tracking

```python
from datetime import datetime

class LinkedInActivityTracker:
    def __init__(self):
        self.activities = []
        self.daily_limits = {
            'connection_requests': 100,
            'messages': 150,
            'profile_views': 1000
        }
    
    def log_activity(self, activity_type: str):
        self.activities.append({
            'type': activity_type,
            'timestamp': datetime.now()
        })
        
        today_count = len([a for a in self.activities 
                          if a['type'] == activity_type 
                          and a['timestamp'].date() == datetime.now().date()])
        
        limit = self.daily_limits.get(activity_type, float('inf'))
        if today_count >= limit:
            print(f"Daily limit reached for {activity_type}")
            return False
        
        print(f"{activity_type}: {today_count}/{limit}")
        return True
```

## Automation Examples

### Send Connection Request

```python
def send_connection_request(profile_url: str, message: str = None):
    with Browser() as browser:
        page = browser.new_page()
        page.goto(profile_url)
        
        connect_button = page.query_selector('button:has-text("Connect")')
        if not connect_button:
            print("Already connected or pending")
            return
        
        connect_button.click()
        
        if message:
            page.click('button:has-text("Add a note")')
            page.fill('textarea[name="message"]', message)
        
        page.click('button[aria-label="Send now"]')
        print("Connection request sent")
```

### Post Content

```python
def post_update(content: str):
    with Browser() as browser:
        page = browser.new_page()
        page.goto("https://www.linkedin.com/feed")
        
        page.click('button[data-control-name="share.share_box_open"]')
        page.wait_for_selector('.ql-editor', timeout=10000)
        page.fill('.ql-editor', content)
        
        # Add hashtags
        for tag in ["#automation", "#productivity"]:
            page.type('.ql-editor', f" {tag}")
        
        page.click('button[data-control-name="share.post"]')
        print("Update posted")
```

### Lead Generation Search

```python
def search_and_connect(search_query: str, max_connections: int = 10):
    with Browser() as browser:
        page = browser.new_page()
        page.goto(f"https://www.linkedin.com/search/results/people/?keywords={search_query}")
        page.wait_for_selector('.search-results-container')
        
        profiles = page.query_selector_all('.entity-result__title-text a')
        
        connected = 0
        for profile in profiles[:max_connections]:
            if connected >= max_connections:
                break
                
            profile_url = profile.get_attribute('href')
            page.goto(profile_url)
            time.sleep(random.uniform(3, 7))
            
            try:
                connect_btn = page.query_selector('button:has-text("Connect")')
                if connect_btn:
                    connect_btn.click()
                    time.sleep(1)
                    
                    send_btn = page.query_selector('button[aria-label="Send now"]')
                    if send_btn:
                        send_btn.click()
                        connected += 1
                        print(f"Connected: {connected}/{max_connections}")
                        time.sleep(random.uniform(30, 60))
            except:
                continue
```

## Best Practices

1. **Respect Rate Limits**:
   - Connection requests: ~100/day
   - Messages: ~150/day
   - Profile views: ~1000/day

2. **Human-like Behavior**:
   - Random delays between actions (2-10 seconds)
   - Vary activity patterns
   - No 24/7 automation

3. **Profile Warm-up**:
   - Start slowly with new accounts
   - Gradually increase activity
   - Mix automated and manual actions

4. **Content Quality**:
   - Personalize connection messages
   - Avoid spam-like content
   - Engage authentically

5. **Error Handling**:
   - Retry failed actions with backoff
   - Handle CAPTCHAs gracefully
   - Monitor for account restrictions

## Security

1. **Use Dedicated Profiles**: Never automate your primary account
2. **IP Rotation**: Consider residential proxies
3. **Session Management**: Keep browser fingerprints consistent
4. **Data Privacy**: Follow GDPR and local privacy laws
5. **API Alternative**: Use LinkedIn's official APIs when possible

## Legal & Ethical Notes

1. **Terms of Service**: LinkedIn prohibits most automation
2. **Data Scraping**: Likely violates LinkedIn's terms
3. **Spam Laws**: Comply with CAN-SPAM and similar regulations
4. **User Consent**: Respect privacy and preferences
5. **Professional Use**: Legitimate business purposes only

## Resources

- [LinkedIn User Agreement](https://www.linkedin.com/legal/user-agreement)
- [LinkedIn API Documentation](https://docs.microsoft.com/en-us/linkedin/)
- [LinkedIn Help Center](https://www.linkedin.com/help/linkedin)
- [PlaywrightAuthor Rate Limiting Guide](../performance/rate-limiting.md)
- [Ethical Automation Guidelines](../best-practices/ethics.md)