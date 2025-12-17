"""
Slack Notifications for AI Agents
Sends detailed success and error notifications to Slack.

Usage in your agents:
    from slack_notifications import notify_qa_complete, notify_pr_review_complete
"""

import os
import requests
from datetime import datetime
from typing import Optional, Dict, Any


def notify_qa_complete(
    pr_number: int,
    pr_title: str,
    tests_generated: int,
    tests_passed: int,
    tests_failed: int,
    execution_time: float,
    tokens_used: int,
    cost: float,
    files_analyzed: int
):
    """
    Send QA Agent completion notification to Slack with test results
    """
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("⚠️  SLACK_WEBHOOK_URL not set - skipping Slack notification")
        return
    
    github_repo = os.environ.get('GITHUB_REPOSITORY', 'owner/repo')
    pr_url = f"https://github.com/{github_repo}/pull/{pr_number}"
    
    # Calculate success rate
    total_tests = tests_passed + tests_failed
    success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Choose emoji and status based on results
    if success_rate == 100 and tests_generated > 0:
        status_emoji = "✅"
        status_text = "All Tests Passing"
    elif success_rate >= 80:
        status_emoji = "⚠️"
        status_text = "Most Tests Passing"
    elif tests_generated == 0:
        status_emoji = "ℹ️"
        status_text = "No Tests Generated"
    else:
        status_emoji = "❌"
        status_text = "Some Tests Failing"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🧪 QA Agent Complete: PR #{pr_number}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{pr_url}|{pr_title}>*\n{status_emoji} {status_text}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Tests Generated:*\n🔢 {tests_generated} tests"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Success Rate:*\n📊 {success_rate:.1f}%"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Passed:*\n✅ {tests_passed}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed:*\n❌ {tests_failed}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Files Analyzed:*\n📁 {files_analyzed} files"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Execution Time:*\n⏱️ {execution_time:.1f}s"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"💰 Cost: ${cost:.4f} | 🔤 Tokens: {tokens_used:,} | 🤖 QA Agent"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Pull Request",
                            "emoji": True
                        },
                        "url": pr_url,
                        "style": "primary"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(slack_webhook, json=message, timeout=10)
        
        if response.status_code == 200:
            print("✅ Slack notification sent successfully!")
        else:
            print(f"⚠️  Slack notification failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"⚠️  Failed to send Slack notification: {e}")


def notify_pr_review_complete(
    pr_number: int,
    pr_title: str,
    files_reviewed: int,
    issues_found: int,
    suggestions_made: int,
    execution_time: float,
    tokens_used: int,
    cost: float,
    review_summary: str
):
    """
    Send PR Review Agent completion notification to Slack
    """
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("⚠️  SLACK_WEBHOOK_URL not set - skipping Slack notification")
        return
    
    github_repo = os.environ.get('GITHUB_REPOSITORY', 'owner/repo')
    pr_url = f"https://github.com/{github_repo}/pull/{pr_number}"
    
    # Determine review status
    if issues_found == 0:
        status_emoji = "✅"
        status_text = "Looks Good!"
        style = "primary"
    elif issues_found <= 3:
        status_emoji = "⚠️"
        status_text = "Minor Issues Found"
        style = "primary"
    else:
        status_emoji = "🔴"
        status_text = "Review Needed"
        style = "danger"
    
    # Truncate summary if too long
    if len(review_summary) > 200:
        review_summary = review_summary[:197] + "..."
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"👨‍💻 PR Review Complete: PR #{pr_number}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*<{pr_url}|{pr_title}>*\n{status_emoji} {status_text}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"_{review_summary}_"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Files Reviewed:*\n📂 {files_reviewed} files"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Issues Found:*\n🔍 {issues_found}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Suggestions:*\n💡 {suggestions_made}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Execution Time:*\n⏱️ {execution_time:.1f}s"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"💰 Cost: ${cost:.4f} | 🔤 Tokens: {tokens_used:,} | 🤖 PR Review Agent"
                    }
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Review on GitHub",
                            "emoji": True
                        },
                        "url": pr_url,
                        "style": style
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(slack_webhook, json=message, timeout=10)
        
        if response.status_code == 200:
            print("✅ Slack notification sent successfully!")
        else:
            print(f"⚠️  Slack notification failed: {response.status_code}")
            print(f"   Response: {response.text}")
    
    except Exception as e:
        print(f"⚠️  Failed to send Slack notification: {e}")


def notify_agent_error(
    agent_name: str,
    pr_number: Optional[int],
    error_message: str,
    step: str
):
    """
    Send error notification to Slack when agent fails
    """
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("⚠️  SLACK_WEBHOOK_URL not set - skipping Slack notification")
        return
    
    github_repo = os.environ.get('GITHUB_REPOSITORY', 'owner/repo')
    pr_link = f"<https://github.com/{github_repo}/pull/{pr_number}|PR #{pr_number}>" if pr_number else "N/A"
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {agent_name} Failed",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Pull Request:*\n{pr_link}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failed at:*\n{step}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:*\n```{error_message[:500]}```"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(slack_webhook, json=message, timeout=10)
        
        if response.status_code == 200:
            print("✅ Error notification sent to Slack")
        else:
            print(f"⚠️  Slack error notification failed: {response.status_code}")
    
    except Exception as e:
        print(f"⚠️  Failed to send error notification: {e}")


def test_slack_notifications():
    """Test Slack notifications - run this to verify setup"""
    print("\n🧪 Testing Slack Notifications\n")
    print("=" * 60)
    
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')
    
    if not slack_webhook:
        print("❌ SLACK_WEBHOOK_URL not set!")
        print("\nPlease set it:")
        print("  export SLACK_WEBHOOK_URL='https://hooks.slack.com/services/...'")
        return
    
    print("✅ SLACK_WEBHOOK_URL is set")
    print(f"   Webhook: {slack_webhook[:50]}...")
    
    # Test QA notification
    print("\n1️⃣  Testing QA Agent notification...")
    notify_qa_complete(
        pr_number=999,
        pr_title="Test PR: Add new feature",
        tests_generated=5,
        tests_passed=4,
        tests_failed=1,
        execution_time=3.2,
        tokens_used=1250,
        cost=0.0045,
        files_analyzed=3
    )
    
    # Test PR Review notification
    print("\n2️⃣  Testing PR Review Agent notification...")
    notify_pr_review_complete(
        pr_number=999,
        pr_title="Test PR: Add new feature",
        files_reviewed=3,
        issues_found=2,
        suggestions_made=4,
        execution_time=4.1,
        tokens_used=2340,
        cost=0.0089,
        review_summary="Code looks good overall. Found minor issues with error handling and suggested some performance improvements."
    )
    
    # Test error notification
    print("\n3️⃣  Testing error notification...")
    notify_agent_error(
        agent_name="Test Agent",
        pr_number=999,
        error_message="This is a test error - please ignore",
        step="test_step"
    )
    
    print("\n" + "=" * 60)
    print("\n✅ Test complete! Check your Slack channel for messages.")
    print("\nIf you didn't receive messages:")
    print("  1. Verify webhook URL is correct")
    print("  2. Check Slack app permissions")
    print("  3. Ensure webhook is active")


if __name__ == "__main__":
    # Run tests when executed directly
    test_slack_notifications()
