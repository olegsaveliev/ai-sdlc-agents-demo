import os
import anthropic
import requests
from datetime import datetime, timedelta

# Configuration
ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
GITHUB_REPO = os.environ['GITHUB_REPOSITORY']
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

def get_team_activity():
    """Fetch recent team activity from GitHub"""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    since = (datetime.now() - timedelta(days=1)).isoformat()
    
    activity = {
        'issues': [],
        'pull_requests': []
    }
    
    # Get recent issues
    issues_url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    params = {'since': since, 'state': 'all', 'per_page': 50}
    response = requests.get(issues_url, headers=headers, params=params)
    activity['issues'] = response.json()
    
    # Get recent PRs
    prs_url = f"https://api.github.com/repos/{GITHUB_REPO}/pulls"
    params = {'state': 'all', 'per_page': 50}
    response = requests.get(prs_url, headers=headers, params=params)
    activity['pull_requests'] = response.json()
    
    return activity

def get_project_metrics(activity):
    """Calculate project metrics"""
    metrics = {
        'open_issues': 0,
        'closed_issues': 0,
        'open_prs': 0,
        'merged_prs': 0,
        'in_progress': 0,
        'blocked': 0
    }
    
    for issue in activity['issues']:
        if 'pull_request' not in issue:
            if issue['state'] == 'open':
                metrics['open_issues'] += 1
                if any(label['name'] == 'in-progress' for label in issue.get('labels', [])):
                    metrics['in_progress'] += 1
                if any(label['name'] == 'blocked' for label in issue.get('labels', [])):
                    metrics['blocked'] += 1
            else:
                metrics['closed_issues'] += 1
    
    for pr in activity['pull_requests']:
        if pr['state'] == 'open':
            metrics['open_prs'] += 1
        elif pr.get('merged_at'):
            metrics['merged_prs'] += 1
    
    return metrics

def generate_standup_report(activity, metrics):
    """Use Claude to generate a PM standup report"""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    recent_issues = [
        f"- {issue['title']} (#{issue['number']}) - {issue['state']}"
        for issue in activity['issues'][:10]
    ]
    
    recent_prs = [
        f"- {pr['title']} (#{pr['number']}) - {pr['state']}"
        for pr in activity['pull_requests'][:10]
    ]
    
    prompt = f"""You are a Program Manager AI agent. Generate a professional daily standup report.

**Project Metrics (Last 24 hours):**
- Open Issues: {metrics['open_issues']}
- Closed Issues: {metrics['closed_issues']}
- In Progress: {metrics['in_progress']}
- Blocked: {metrics['blocked']}
- Open PRs: {metrics['open_prs']}
- Merged PRs: {metrics['merged_prs']}

**Recent Issues:**
{chr(10).join(recent_issues) if recent_issues else 'No recent issues'}

**Recent Pull Requests:**
{chr(10).join(recent_prs) if recent_prs else 'No recent PRs'}

**Your task:**
Create a comprehensive standup report with:
1. Executive Summary (2-3 sentences on overall progress)
2. Key Highlights (wins and achievements)
3. Active Work Items (what's in progress)
4. Blockers & Risks (if any)
5. Velocity & Health Metrics
6. Next Steps & Priorities

Use markdown formatting. Be concise but insightful. Focus on actionable information."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return message.content[0].text

def post_to_notion(report, metrics):
    """Post PM report to Notion"""
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("⚠️ Notion credentials not configured, skipping Notion post")
        return
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    today = datetime.now().strftime('%Y-%m-%d')
    truncated_report = report[:1800] if len(report) > 1800 else report
    
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": f"PM Standup - {today}"}}]
            },
            "Agent Type": {
                "select": {"name": "PM"}
            },
            "Issue/PR Number": {
                "number": 0
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
                    "rich_text": [{"type": "text", "text": {"content": f"Daily Standup - {today}"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "Metrics"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"Open Issues: {metrics['open_issues']}"}}]
                }
            },
            {
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": f"Merged PRs: {metrics['merged_prs']}"}}]
                }
            },
            {
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "Report"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": truncated_report}}]
                }
            }
        ]
    }
    
    response = requests.post(
        "https://api.notion.com/v1/pages",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print(f"✅ Posted to Notion successfully!")
    else:
        print(f"⚠️ Notion post failed: {response.status_code}")
        print(response.text)

def save_report(report):
    """Save standup report to file"""
    with open('standup_report.md', 'w') as f:
        f.write(f"# Daily Standup Report\n")
        f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}\n\n")
        f.write(report)
        f.write(f"\n\n---\n*Generated by PM Agent*")
    
    print("✅ Report saved to standup_report.md")

def main():
    print("🤖 PM Agent starting daily standup report...")
    
    # Gather team activity
    print("📊 Collecting team activity...")
    activity = get_team_activity()
    
    # Calculate metrics
    metrics = get_project_metrics(activity)
    print(f"📈 Metrics: {metrics['open_issues']} open issues, {metrics['merged_prs']} PRs merged")
    
    # Generate report with Claude
    print("✍️ Generating standup report...")
    report = generate_standup_report(activity, metrics)
    
    # Save report
    save_report(report)
    
    # Post to Notion
    print("📝 Posting to Notion...")
    post_to_notion(report, metrics)
    
    print("✅ PM Agent completed successfully!")

if __name__ == "__main__":
    main()
