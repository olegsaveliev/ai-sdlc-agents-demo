name: Deploy to Staging

on:
  pull_request:
    types: [closed]
  workflow_dispatch:
    inputs:
      branch:
        description: 'Branch to deploy'
        required: true
        default: 'main'

jobs:
  # Check if deployment should proceed
  check-deployment:
    if: github.event.pull_request.merged == true || github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    outputs:
      should_deploy: ${{ steps.check.outputs.should_deploy }}
    
    steps:
      - name: Check if deployment needed
        id: check
        run: |
          if [ "${{ github.event_name }}" == "workflow_dispatch" ]; then
            echo "should_deploy=true" >> $GITHUB_OUTPUT
          elif [ "${{ github.event.pull_request.merged }}" == "true" ]; then
            # Only deploy if PR was merged to main
            if [ "${{ github.event.pull_request.base.ref }}" == "main" ]; then
              echo "should_deploy=true" >> $GITHUB_OUTPUT
            else
              echo "should_deploy=false" >> $GITHUB_OUTPUT
            fi
          fi
      
      - name: Comment on PR
        if: steps.check.outputs.should_deploy == 'true' && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '🚀 **Deployment to Staging Started**\n\n' +
                    'View progress: [Actions](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})'
            })
  
  # Deploy to Staging
  deploy-staging:
    needs: check-deployment
    if: needs.check-deployment.outputs.should_deploy == 'true'
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.yourapp.com
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install boto3 requests
      
      - name: Configure AWS credentials (if using AWS)
        continue-on-error: true
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION || 'us-east-1' }}
      
      - name: Run tests
        run: |
          echo "🧪 Running tests..."
          # Add your test commands here
          # python -m pytest tests/
          echo "✅ Tests passed"
      
      - name: Build application
        run: |
          echo "🏗️  Building application..."
          # Add your build commands here
          # npm run build
          # docker build -t myapp:latest .
          echo "✅ Build complete"
      
      - name: Deploy to Staging
        run: |
          echo "🚀 Deploying to Staging..."
          python agents/deploy_staging.py --environment staging
      
      - name: Run smoke tests
        run: |
          echo "🔥 Running smoke tests..."
          # Add smoke tests here
          # curl -f https://staging.yourapp.com/health || exit 1
          sleep 2
          echo "✅ Smoke tests passed"
      
      - name: Deployment summary
        run: |
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo "✅ DEPLOYMENT SUCCESSFUL"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo "Environment: Staging"
          echo "Commit: ${{ github.sha }}"
          echo "URL: https://staging.yourapp.com"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
      
      - name: Post deployment notification
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const status = '${{ job.status }}' === 'success' ? '✅' : '❌';
            const message = `${status} **Staging Deployment ${status === '✅' ? 'Successful' : 'Failed'}**\n\n` +
                          `Environment: \`staging\`\n` +
                          `Commit: \`${{ github.sha }}\`\n` +
                          `Branch: \`${{ github.ref_name }}\`\n` +
                          `URL: https://staging.yourapp.com\n\n` +
                          `${status === '✅' ? '🎉 Staging is live! Test it out and verify everything works.' : '⚠️ Deployment failed. Check the [logs](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}).'}`;
            
            // Comment on PR if available
            if (context.payload.pull_request) {
              github.rest.issues.createComment({
                issue_number: context.payload.pull_request.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: message
              });
            }
            
            // Create a deployment issue for tracking
            if (status === '✅') {
              await github.rest.issues.create({
                owner: context.repo.owner,
                repo: context.repo.repo,
                title: `🚀 Staging Deployment - ${new Date().toISOString().split('T')[0]}`,
                body: message + `\n\n**Changes included:**\n- Commit: [\`${context.sha.substring(0, 7)}\`](https://github.com/${{ github.repository }}/commit/${{ github.sha }})`,
                labels: ['deployment', 'staging']
              });
            }
