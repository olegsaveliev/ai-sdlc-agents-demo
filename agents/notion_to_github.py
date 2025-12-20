import os
import requests
import time
from datetime import datetime

# Configuration
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_TRIGGER_DB_ID = os.environ.get('NOTION_TRIGGER_DB_ID')  # New database for triggers
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY')

def get_new_notion_pages():
    """Find Notion pages with Status = 'New'"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Query for pages with Status = "New"
    data = {
        "filter": {
            "property": "Status",
            "select": {
                "equals": "New"
            }
        }
    }
    
    response = requests.post(
        f"https://api.notion.com/v1/databases/{NOTION_TRIGGER_DB_ID}/query",
        headers=headers,
        json=data
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to query Notion: {response.status_code}")
        return []
    
    return response.json().get('results', [])

def extract_page_info(page):
    """Extract title and description from Notion page"""
    properties = page['properties']
    
    # Get title
    title = ""
    if 'Name' in properties and properties['Name']['title']:
        title = properties['Name']['title'][0]['text']['content']
    
    # Get description
    description = ""
    if 'Description' in properties:
        desc_property = properties['Description']
        if desc_property['type'] == 'rich_text' and desc_property['rich_text']:
            description = desc_property['rich_text'][0]['text']['content']
    
    return title, description, page['id']

def create_github_issue(title, description):
    """Create a GitHub issue"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/issues"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    
    body = description if description else "Created from Notion - awaiting BA analysis"
    
    data = {
        "title": title,
        "body": body,
        "labels": ["from-notion", "needs-analysis"]
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        issue_number = response.json()['number']
        print(f"✅ Created GitHub issue #{issue_number}")
        return issue_number
    else:
        print(f"❌ Failed to create issue: {response.status_code}")
        return None

def update_notion_page(page_id, status, issue_number=None):
    """Update the Notion page status and issue number"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    properties = {
        "Status": {
            "select": {"name": status}
        }
    }
    
    if issue_number:
        properties["GitHub Issue Number"] = {"number": issue_number}
    
    data = {"properties": properties}
    
    response = requests.patch(
        f"https://api.notion.com/v1/pages/{page_id}",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print(f"✅ Updated Notion page status to '{status}'")
    else:
        print(f"❌ Failed to update Notion: {response.status_code}")

def add_analysis_to_notion(page_id, analysis):
    """Append BA analysis to the Notion page"""
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    # Truncate if needed
    truncated_analysis = analysis[:1900] if len(analysis) > 1900 else analysis
    
    # Add blocks to the page
    data = {
        "children": [
            {
                "object": "block",
                "type": "divider",
                "divider": {}
            },
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "📋 BA Agent Analysis"}}]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": truncated_analysis}}]
                }
            }
        ]
    }
    
    response = requests.patch(
        f"https://api.notion.com/v1/blocks/{page_id}/children",
        headers=headers,
        json=data
    )
    
    if response.status_code == 200:
        print(f"✅ Added analysis to Notion page")
    else:
        print(f"❌ Failed to add analysis: {response.status_code}")

def main():
    print("🔍 Checking for new Notion pages...")
    
    # Get new pages
    new_pages = get_new_notion_pages()
    
    if not new_pages:
        print("📭 No new pages found")
        return
    
    print(f"📄 Found {len(new_pages)} new page(s)")
    
    for page in new_pages:
        title, description, page_id = extract_page_info(page)
        print(f"\n📝 Processing: {title}")
        
        # Mark as processing
        update_notion_page(page_id, "Processing")
        
        # Create GitHub issue
        issue_number = create_github_issue(title, description)
        
        if issue_number:
            # Update Notion with issue number
            update_notion_page(page_id, "Analyzed", issue_number)
            print(f"✅ Page processed successfully!")
        else:
            update_notion_page(page_id, "Error")

if __name__ == "__main__":
    main()
