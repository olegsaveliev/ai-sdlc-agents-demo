import os
import anthropic
import requests
import json

# Configuration
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY')
ISSUE_NUMBER = os.environ.get('ISSUE_NUMBER')
NOTION_TOKEN_TRIGGER = os.environ.get('NOTION_TOKEN_TRIGGER')
NOTION_TRIGGER_DB_ID = os.environ.get('NOTION_TRIGGER_DB_ID')

def normalize_db_id(db_id):
    """Normalize database ID to UUID format"""
    if not db_id:
        return None
    clean_id = db_id.replace('-', '').strip()
    if len(clean_id) == 32:
        return f"{clean_id[0:8]}-{clean_id[8:12]}-{clean_id[12:16]}-{clean_id[16:20]}-{clean_id[20:32]}"
    return db_id

# Normalize the database ID
NOTION_TRIGGER_DB_ID = normalize_db_id(NOTION_TRIGGER_DB_ID)

def get_issue_details():
    """Fetch issue details from GitHub"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues/{ISSUE_NUMBER}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed to fetch issue: {response.status_code}")
        return None

def check_if_issue_exists_in_notion(issue_number):
    """Check if this issue already exists in Notion trigger database"""
    if not NOTION_TOKEN_TRIGGER or not NOTION_TRIGGER_DB_ID:
        return False
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN_TRIGGER}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    query_data = {
        "filter": {
            "property": "GitHub Issue Number",
            "number": {
                "equals": int(issue_number)
            }
        }
    }
    
    try:
        response = requests.post(
            f"https://api.notion.com/v1/databases/{NOTION_TRIGGER_DB_ID}/query",
            headers=headers,
            json=query_data,
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json().get('results', [])
            return len(results) > 0
        else:
            print(f"⚠️ Failed to check Notion: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Error checking Notion: {e}")
        return False

def create_notion_page(issue):
    """Create a page in Notion trigger database for this issue"""
    if not NOTION_TOKEN_TRIGGER or not NOTION_TRIGGER_DB_ID:
        print("⚠️ Notion trigger credentials not configured")
        return False
    
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN_TRIGGER}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Get issue details
    title = issue['title']
    description = issue.get('body', '') or 'No description provided'
    issue_number = issue['number']
    
    # Truncate description if too long
    if len(description) > 2000:
        description = description[:1997] + "..."
    
    # Check if issue has the "from-notion" label
    labels = [label['name'] for label in issue.get('labels', [])]
    if 'from-notion' in labels:
        print("ℹ️ Issue was created from Notion, skipping reverse sync")
        return False
    
    # Create page in Notion
    data = {
        "parent": {"database_id": NOTION_TRIGGER_DB_ID},
        "properties": {
            "Name": {
                "title": [{"text": {"content": title[:100]}}]  # Notion title limit
            },
            "Status": {
                "select": {"name": "Analyzed"}  # Mark as already analyzed
            },
            "GitHub Issue Number": {
                "number": issue_number
            },
            "Description": {
                "rich_text": [{"text": {"content": description}}]
            }
        }
    }
    
    try:
        response = requests.post(
            "https://api.notion.com/v1/pages",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            page_id = response.json()['id']
            print(f"✅ Created Notion page for issue #{issue_number}")
            print(f"   Page ID: {page_id}")
            return True
        else:
            print(f"❌ Failed to create Notion page: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Error creating Notion page: {e}")
        return False

def main():
    print(f"🔄 Syncing issue #{ISSUE_NUMBER} to Notion...")
    
    # Check if credentials are configured
    if not NOTION_TOKEN_TRIGGER or not NOTION_TRIGGER_DB_ID:
        print("ℹ️ Notion trigger database not configured, skipping sync")
        return
    
    # Get issue details
    issue = get_issue_details()
    if not issue:
        print("❌ Could not fetch issue details")
        return
    
    print(f"📝 Issue: {issue['title']}")
    
    # Check if issue already exists in Notion
    if check_if_issue_exists_in_notion(ISSUE_NUMBER):
        print(f"ℹ️ Issue #{ISSUE_NUMBER} already exists in Notion")
        return
    
    # Create Notion page
    success = create_notion_page(issue)
    
    if success:
        print(f"✅ Successfully synced issue #{ISSUE_NUMBER} to Notion!")
    else:
        print(f"⚠️ Failed to sync issue to Notion")

if __name__ == "__main__":
    main()
