import os
import anthropic
import requests
import time
import re

# Import Slack notifications
try:
    from slack_notifications import notify_pr_review_complete, notify_agent_error
    SLACK_ENABLED = True
except ImportError:
    print("⚠️  slack_notifications.py not found - Slack notifications disabled")
    SLACK_ENABLED = False

# Configuration
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
PR_NUMBER = os.environ.get('PR_NUMBER')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')
NOTION_METRICS_DB_ID = os.environ.get('NOTION_METRICS_DB_ID')

# Metrics tracking
start_time = time.time()
tokens_used = 0
files_reviewed = 0
issues_found = 0
suggestions_made = 0

# Validate PR_NUMBER
if not PR_NUMBER or PR_NUMBER == '':
    print("❌ PR_NUMBER not set. This workflow must be triggered by a pull request.")
    exit(0)

def get_pr_details():
    """Fetch PR details and metadata"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        return response.json()
    except Exception as e:
        if SLACK_ENABLED:
            notify_agent_error(
                agent_name="PR Review Agent",
                pr_number=int(PR_NUMBER),
                error_message=str(e),
                step="get_pr_details"
            )
        raise

def get_pr_files():
    """Fetch all changed files in the PR"""
    global files_reviewed
    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}/files"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if isinstance(data, dict):
            print(f"Warning: Unexpected response: {data}")
            return []
        
        files_reviewed = len(data)
        return data
    except Exception as e:
        if SLACK_ENABLED:
            notify_agent_error(
                agent_name="PR Review Agent",
                pr_number=int(PR_NUMBER),
                error_message=str(e),
                step="get_pr_files"
            )
        raise

def get_pr_diff():
    """Get the unified diff for the PR"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls/{PR_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3.diff"
    }
    
    try:
        response = requests.get(url, headers=headers)
        return response.text[:4000]
    except Exception as e:
        if SLACK_ENABLED:
            notify_agent_error(
                agent_name="PR Review Agent",
                pr_number=int(PR_NUMBER),
                error_message=str(e),
                step="get_pr_diff"
            )
        raise

def analyze_review_content(review_text):
    """Analyze review to extract metrics"""
    global issues_found, suggestions_made
    
    # Count issues mentioned
    issues_found = len(re.findall(r'(issue|problem|bug|error|concern)', review_text, re.IGNORECASE))
    
    # Count suggestions
    suggestions_made = len(re.findall(r'(suggest|recommend|consider|could|should)', review_text, re.IGNORECASE))
    
    # Cap at reasonable numbers
    issues_found = min(issues_found, 10)
    suggestions_made = min(suggestions_made, 15)

def review_code_with_claude(pr_details, files, diff):
    """Use Claude to review the code changes"""
    global tokens_used
    
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        file_summary = []
        for file in files[:5]:
            file_summary.append(f"- {file['filename']}: +{file['additions']} -{file['deletions']} lines")
        
        prompt = f"""You are a Senior Code Reviewer AI agent. Review this pull request and provide constructive feedback.

**PR Title:** {pr_details.get('title', 'Unknown')}
**Description:** {pr_details.get('body', 'No description provided')[:500]}

**Changed Files:**
{chr(10).join(file_summary)}

**Code Diff (sample):**
```
{diff}
```

**Your task:**
Provide a code review with:

1. **Overall Assessment** (Approve, Request Changes, or Comment)
2. **Code Quality** (readability, maintainability, best practices)
3. **Potential Issues** (bugs, edge cases, security concerns)
4. **Suggestions** (improvements, optimizations)
5. **Positive Feedback** (what's done well)

Be constructive and specific. Focus on:
- Logic errors or bugs
- Security vulnerabilities
- Performance issues
- Code style and readability
- Missing error handling
- Potential edge cases

Format your response as structured markdown with clear sections."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Track token usage
        tokens_used = message.usage.input_tokens + message.usage.output_tokens
        
        review_text = message.content[0].text
        
        # Analyze review for metrics
        analyze_review_content(review_text)
        
        return review_text
    
    except Exception as e:
        if SLACK_ENABLED:
            notify_agent_error(
                agent_name="PR Review Agent",
                pr_number=int(PR_NUMBER),
                error_message=str(e),
                step="review_code_with_claude"
            )
        raise

def post_review_comment(pr_details, review):
    """Post review as a comment on the PR"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{PR_NUMBER}/comments"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    comment_body = f"""## 👨‍💻 PR Review Agent Analysis

{review}

---
**Note:** This is an automated review. Human approval still required for merge.

*Generated by PR Review Agent*"""
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"body": comment_body}
        )
        
        if response.status_code == 201:
            print("✅ Review posted to GitHub")
        else:
            print(f"⚠️ Failed to post review: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to post GitHub comment: {e}")

def post_to_notion(pr_title, pr_number, review, pr_url):
    """Post review to Notion database"""
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("⚠️ Notion credentials not configured, skipping Notion post")
        return
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    truncated_review = review[:1800] if len(review) > 1800 else review
    
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": f"PR Review: {pr_title[:80]}"}}]
            },
            "Agent Type": {
                "select": {"name": "PR Review"}
            },
            "Issue/PR Number": {
                "number": int(pr_number)
            },
            "Status": {
                "select": {"name": "Complete"}
            }
        },
        "children": [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "Code Review Report"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {"type": "text", "text": {"content": "PR: "}},
                        {"type": "text", "text": {"content": pr_title, "link": {"url": pr_url}}}
                    ]
                }
            },
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": truncated_review}}]
                }
            }
        ]
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print("✅ Posted to Notion successfully!")
        else:
            print(f"⚠️ Notion post failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Notion post error: {e}")

def log_metrics(status="Success", error_message=None):
    """Log performance metrics to Notion"""
    if not NOTION_TOKEN or not NOTION_METRICS_DB_ID:
        print("⚠️ Metrics database not configured, skipping metrics logging")
        return
    
    execution_time = round(time.time() - start_time, 2)
    
    # Calculate cost
    input_cost = (tokens_used * 0.7) * (3.00 / 1_000_000)
    output_cost = (tokens_used * 0.3) * (15.00 / 1_000_000)
    cost = round(input_cost + output_cost, 4)
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    properties = {
        "Name": {
            "title": [{"text": {"content": f"PR Review - PR #{PR_NUMBER}"}}]
        },
        "Agent": {"select": {"name": "PR Review"}},
        "Execution Time": {"number": execution_time},
        "Tokens Used": {"number": tokens_used},
        "Cost": {"number": cost},
        "Status": {"select": {"name": status}},
        "Issue/PR Number": {"number": int(PR_NUMBER)}
    }
    
    if error_message:
        properties["Error Message"] = {
            "rich_text": [{"text": {"content": str(error_message)[:2000]}}]
        }
    
    data = {
        "parent": {"database_id": NOTION_METRICS_DB_ID},
        "properties": properties
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"📊 Metrics logged: {execution_time}s, {tokens_used} tokens, ${cost}")
        else:
            print(f"⚠️ Metrics logging failed: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Metrics error: {e}")

def send_slack_summary(pr_title, review_text):
    """Send completion summary to Slack"""
    if not SLACK_ENABLED:
        print("⚠️ Slack notifications not available")
        return
    
    execution_time = round(time.time() - start_time, 2)
    
    # Calculate cost
    input_cost = (tokens_used * 0.7) * (3.00 / 1_000_000)
    output_cost = (tokens_used * 0.3) * (15.00 / 1_000_000)
    cost = round(input_cost + output_cost, 4)
    
    # Extract summary (first paragraph or first 200 chars)
    review_lines = review_text.split('\n')
    review_summary = ""
    for line in review_lines:
        if line.strip() and not line.startswith('#'):
            review_summary = line.strip()
            break
    
    if not review_summary:
        review_summary = review_text[:200]
    
    try:
        notify_pr_review_complete(
            pr_number=int(PR_NUMBER),
            pr_title=pr_title,
            files_reviewed=files_reviewed,
            issues_found=issues_found,
            suggestions_made=suggestions_made,
            execution_time=execution_time,
            tokens_used=tokens_used,
            cost=cost,
            review_summary=review_summary
        )
    except Exception as e:
        print(f"⚠️ Failed to send Slack notification: {e}")

def main():
    print(f"🤖 PR Review Agent starting for PR #{PR_NUMBER}...")
    
    try:
        # Get PR details
        pr_details = get_pr_details()
        pr_title = pr_details.get('title', 'Unknown PR')
        pr_url = pr_details.get('html_url', '')
        print(f"🔍 Reviewing: {pr_title}")
        
        # Get changed files
        files = get_pr_files()
        if not files:
            print("⚠️ No files to review")
            log_metrics(status="Success")
            return
        
        print(f"📂 Found {len(files)} changed files")
        
        # Get diff
        diff = get_pr_diff()
        
        # Review with Claude
        print("🔍 Analyzing code with Claude...")
        review = review_code_with_claude(pr_details, files, diff)
        print(f"✅ Review complete ({len(review)} characters)")
        print(f"📊 Analysis: {issues_found} issues, {suggestions_made} suggestions")
        
        # Post to GitHub
        post_review_comment(pr_details, review)
        
        # Post to Notion
        print("📝 Posting to Notion...")
        post_to_notion(pr_title, PR_NUMBER, review, pr_url)
        
        # Log metrics
        log_metrics(status="Success")
        
        # Send Slack notification
        print("\n📱 Sending Slack notification...")
        send_slack_summary(pr_title, review)
        
        print("✅ PR Review Agent completed successfully!")
        
    except Exception as e:
        print(f"❌ PR Review Agent failed: {e}")
        log_metrics(status="Failed", error_message=str(e))
        
        # Try to send error notification
        if SLACK_ENABLED:
            try:
                notify_agent_error(
                    agent_name="PR Review Agent",
                    pr_number=int(PR_NUMBER) if PR_NUMBER else None,
                    error_message=str(e),
                    step="main"
                )
            except:
                pass
        
        raise

if __name__ == "__main__":
    main()
