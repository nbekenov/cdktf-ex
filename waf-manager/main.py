#!/usr/bin/env python
import os
import sys
import json
from constructs import Construct
from cdktf import App, TerraformStack
from imports.aws import (
    AwsProvider, FmsPolicy,
    FmsAdminAccount,
    FmsPolicySecurityServicePolicyData
)

class FirewallManager(TerraformStack):
    def __init__(self, scope: Construct, ns: str, profile_name, partition):
        super().__init__(scope, ns)

        self.profile_name = profile_name
        region = "us-gov-west-1" if "gov" in partition else "us-east-1" 
        AwsProvider(self, f"aws-{region}", region=region, profile=profile_name)

    def set_admin_account(self):
        """
        Associates an AWS Firewall Manager administrator account. 
        This operation must be performed in the us-east-1 region.
        aws_fms_admin_account
        """
        # FmsAdminAccount(self, "fms-admin")
        pass
    
    def create_global_policy(self, policy_name, rules_file):
        """
        Create AWS Firewall Manager policy
        global scope -> CloudFront
        """
        rules = self.__parse_rule(rules_file)

        global_policy = FmsPolicy(self,f"fms-globalpolicy-{policy_name}",
            name=policy_name,
            exclude_resource_tags=False,
            resource_type = "AWS::CloudFront::Distribution",
            security_service_policy_data = [
                FmsPolicySecurityServicePolicyData(
                    type="WAFV2",
                    managed_service_data = json.dumps(rules)
                )
            ],
            remediation_enabled=True, # Auto remediate any noncompliant resourcesß
        )
    
    def create_region_policy(self, policy_name, rules_file, region):
        """
        Create AWS Firewall Manager policy
        region scope -> ALB, ApiGateway
        """
        aws = AwsProvider(self, f"aws-fms-{region}",
            region=region,
            profile=self.profile_name,
            alias = f"aws-{region}"
        )
        rules = self.__parse_rule(rules_file)
        
        region_policy = FmsPolicy(self,f"fms-policy-{policy_name}",
            name=policy_name,
            exclude_resource_tags=False,
            resource_type_list = ["AWS::ElasticLoadBalancingV2::LoadBalancer", "AWS::ApiGateway::Stage"],
            security_service_policy_data = [
                FmsPolicySecurityServicePolicyData(
                    type="WAFV2",
                    managed_service_data = json.dumps(rules)
                )
            ],
            remediation_enabled=True, # Auto remediate any noncompliant resources
            provider = aws
        )

    def __parse_rule(self, file_name):
        """
        Parse and validate json file with rules definitions
        """
        project_dir = os.path.dirname(os.path.realpath(__file__))
        rule_data = {}
        try:
            with open(f"{project_dir}/{file_name}") as rules_rile:
                rule_data = json.load(rules_rile)
            rules_num = len(rule_data["preProcessRuleGroups"])
            print(f"LOG: number of preProcessRuleGroups {rules_num}")
        except FileNotFoundError as fnf_err:
            sys.exit(f"{fnf_err}: rule file not found")

        return rule_data


def main():
    app = App(stack_traces=False)
    waf_manager = FirewallManager(app, "waf-manager", profile_name="nurdev", partition="aws")
    # waf_manager.set_admin_account()
    waf_manager.create_global_policy(policy_name="FMS-Test-global",
        rules_file="AWSCommonRuleSet.json"
    )
    waf_manager.create_region_policy(policy_name="FMS-Test-regional",
        rules_file="AWSCommonRuleSet.json", region="us-east-1"
    )
    app.synth()


if __name__ == "__main__":
    main()