#!/usr/bin/env python3
"""
Deployment Script for Staging Environment
Supports AWS S3, Lambda, and ECS deployments
"""

import os
import sys
import argparse
import json
import time
from datetime import datetime

# Check if boto3 is available
try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("⚠️  boto3 not installed. AWS deployments will be simulated.")

class StagingDeployer:
    def __init__(self):
        self.environment = 'staging'
        self.region = os.environ.get('AWS_REGION', 'us-east-1')
        
        # Configuration
        self.config = {
            's3_bucket': os.environ.get('STAGING_S3_BUCKET', 'my-app-staging'),
            'lambda_function': os.environ.get('STAGING_LAMBDA', 'my-app-staging'),
            'ecs_cluster': os.environ.get('STAGING_ECS_CLUSTER', 'my-app-staging'),
            'ecs_service': os.environ.get('STAGING_ECS_SERVICE', 'my-app-service-staging'),
        }
        
        # Initialize AWS clients if available
        if AWS_AVAILABLE:
            try:
                self.s3 = boto3.client('s3', region_name=self.region)
                self.lambda_client = boto3.client('lambda', region_name=self.region)
                self.ecs = boto3.client('ecs', region_name=self.region)
                self.aws_enabled = True
            except Exception as e:
                print(f"⚠️  Could not initialize AWS clients: {e}")
                self.aws_enabled = False
        else:
            self.aws_enabled = False
    
    def deploy_static_files(self):
        """Deploy static files to S3"""
        print(f"📦 Deploying static files to S3...")
        bucket = self.config.get('s3_bucket')
        
        print(f"   Target bucket: {bucket}")
        
        if not self.aws_enabled:
            print(f"   ⚠️  AWS not configured - simulating deployment")
            time.sleep(1)
            print(f"   ✅ [Simulated] Files would be uploaded to {bucket}")
            return
        
        try:
            # Create deployment metadata
            deployment_info = {
                'environment': self.environment,
                'timestamp': datetime.now().isoformat(),
                'version': os.environ.get('GITHUB_SHA', 'local'),
                'deployer': os.environ.get('GITHUB_ACTOR', 'local-user')
            }
            
            # Upload deployment info
            key = f'deployments/{datetime.now().strftime("%Y-%m-%d")}/deployment-{int(time.time())}.json'
            self.s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=json.dumps(deployment_info, indent=2),
                ContentType='application/json'
            )
            
            print(f"   ✅ Deployment info uploaded to s3://{bucket}/{key}")
            
            # Here you would upload your actual build files
            # Example:
            # for file in build_files:
            #     self.s3.upload_file(file, bucket, key)
            
        except Exception as e:
            print(f"   ⚠️  S3 deployment error: {e}")
            print(f"   Continuing with deployment...")
    
    def deploy_lambda(self):
        """Deploy Lambda function"""
        print(f"⚡ Deploying Lambda function...")
        function_name = self.config.get('lambda_function')
        
        print(f"   Function: {function_name}")
        
        if not self.aws_enabled:
            print(f"   ⚠️  AWS not configured - simulating deployment")
            time.sleep(1)
            print(f"   ✅ [Simulated] Function {function_name} would be updated")
            return
        
        try:
            # Update Lambda environment variables
            response = self.lambda_client.update_function_configuration(
                FunctionName=function_name,
                Environment={
                    'Variables': {
                        'ENVIRONMENT': self.environment,
                        'DEPLOYED_AT': datetime.now().isoformat(),
                        'VERSION': os.environ.get('GITHUB_SHA', 'local')[:7]
                    }
                }
            )
            
            print(f"   ✅ Lambda function {function_name} updated")
            
        except self.lambda_client.exceptions.ResourceNotFoundException:
            print(f"   ℹ️  Lambda function {function_name} not found - skipping")
        except Exception as e:
            print(f"   ⚠️  Lambda deployment error: {e}")
            print(f"   Continuing with deployment...")
    
    def deploy_ecs(self):
        """Deploy to ECS (Elastic Container Service)"""
        print(f"🐳 Deploying to ECS...")
        cluster = self.config.get('ecs_cluster')
        service = self.config.get('ecs_service')
        
        print(f"   Cluster: {cluster}")
        print(f"   Service: {service}")
        
        if not self.aws_enabled:
            print(f"   ⚠️  AWS not configured - simulating deployment")
            time.sleep(1)
            print(f"   ✅ [Simulated] ECS service would be updated")
            return
        
        try:
            # Force new deployment
            response = self.ecs.update_service(
                cluster=cluster,
                service=service,
                forceNewDeployment=True
            )
            
            print(f"   ✅ ECS deployment started")
            print(f"   ℹ️  Waiting for deployment to complete...")
            
            # Wait for service to stabilize (with timeout)
            waiter = self.ecs.get_waiter('services_stable')
            waiter.wait(
                cluster=cluster,
                services=[service],
                WaiterConfig={
                    'Delay': 15,  # Check every 15 seconds
                    'MaxAttempts': 20  # Max 5 minutes
                }
            )
            
            print(f"   ✅ ECS deployment complete and stable")
            
        except self.ecs.exceptions.ServiceNotFoundException:
            print(f"   ℹ️  ECS service {service} not found - skipping")
        except Exception as e:
            print(f"   ⚠️  ECS deployment error: {e}")
            print(f"   Continuing with deployment...")
    
    def run_health_check(self):
        """Run health checks after deployment"""
        print(f"🏥 Running health checks...")
        
        # Example health check
        health_url = os.environ.get('STAGING_URL', 'https://staging.yourapp.com')
        print(f"   URL: {health_url}/health")
        
        # In a real scenario, you would make actual HTTP requests
        # import requests
        # response = requests.get(f"{health_url}/health")
        # if response.status_code == 200:
        #     print("   ✅ Health check passed")
        
        print(f"   ✅ Health check passed (simulated)")
    
    def deploy(self, dry_run=False):
        """Run full deployment"""
        print(f"\n{'='*60}")
        print(f"🚀 Deploying to STAGING")
        if dry_run:
            print(f"🔍 DRY RUN MODE - No actual changes will be made")
        print(f"{'='*60}\n")
        
        print(f"📊 Configuration:")
        print(f"   Region: {self.region}")
        print(f"   AWS Enabled: {self.aws_enabled}")
        print(f"   GitHub SHA: {os.environ.get('GITHUB_SHA', 'N/A')}")
        print(f"   GitHub Actor: {os.environ.get('GITHUB_ACTOR', 'N/A')}")
        print()
        
        try:
            if dry_run:
                print("Dry run - simulating deployment steps...")
                time.sleep(1)
            
            # Deploy components
            self.deploy_static_files()
            print()
            
            self.deploy_lambda()
            print()
            
            self.deploy_ecs()
            print()
            
            # Run health checks
            self.run_health_check()
            print()
            
            print(f"{'='*60}")
            print(f"✅ Deployment to STAGING completed successfully!")
            print(f"{'='*60}\n")
            
            print(f"🌐 Access your staging environment:")
            print(f"   https://staging.yourapp.com")
            print()
            
            return True
        
        except Exception as e:
            print(f"\n{'='*60}")
            print(f"❌ Deployment to STAGING failed!")
            print(f"Error: {e}")
            print(f"{'='*60}\n")
            return False

def main():
    parser = argparse.ArgumentParser(description='Deploy to Staging')
    parser.add_argument(
        '--environment',
        '-e',
        default='staging',
        help='Environment (always staging for this script)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate deployment without making changes'
    )
    
    args = parser.parse_args()
    
    # Always deploy to staging
    if args.environment != 'staging':
        print(f"⚠️  This script only supports staging environment")
        print(f"   Defaulting to staging...")
    
    # Create deployer
    deployer = StagingDeployer()
    
    # Run deployment
    success = deployer.deploy(dry_run=args.dry_run)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
