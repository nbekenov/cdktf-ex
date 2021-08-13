
# CDK-TF AWS Firewall Manager
> Example how to deploy AWS Firewall Manager with CDK for Terraform

## Firewall Manager prerequisites
* Your organization must be using AWS Organizations to manage your accounts, and All Features must be enabled.
* You must designate one of the AWS accounts in your organization as the Firewall Manager administrator for Firewall Manager. This gives the account permission to deploy security policies across the organization.
* You must enable AWS Config for all of the accounts in your organization so that Firewall Manager can detect newly created resources.

## Useful materials

* Great video overview and demo about Firewall Manager [link](https://www.youtube.com/watch?v=u27HLad-Wi8)
* Guidelines for Implementing AWS WAF [link](https://d1.awsstatic.com/whitepapers/guidelines-implementing-aws-waf.pdf)
* AWS Security blog article about Firewall Manager [link](https://aws.amazon.com/blogs/security/use-aws-firewall-manager-to-deploy-protection-at-scale-in-aws-organizations/?nc1=b_rp)
* The three most important WAF rate-based rules [link](https://aws.amazon.com/blogs/security/three-most-important-aws-waf-rate-based-rules/)
* Services that can integrate [link](https://docs.aws.amazon.com/organizations/latest/userguide/services-that-can-integrate-fms.html)
* Enable automatic logging of Web ACLs [link](https://aws.amazon.com/blogs/security/enable-automatic-logging-of-web-acls-by-using-aws-config/)
* Integrate Security Hub with Firewall Manager to detect resources that are not properly protected by WAF rules [link](https://aws.amazon.com/about-aws/whats-new/2019/12/aws-security-hub-integrates-with-aws-firewall-manager/)
* Centralized visibility into Shield Advanced DDoS events [link](https://aws.amazon.com/blogs/security/set-up-centralized-monitoring-for-ddos-events-and-auto-remediate-noncompliant-resources/)
* WAFv2 api ref [link](https://docs.aws.amazon.com/waf/latest/APIReference/Welcome.html)

---
## Dev Prerequisites
* Terraform v0.12+
* cdktf v0.3+
* Node.js v12.16+
* Python v3.7+ and pipenv
* AWS account and AWS Access Credentials

## Usage

Example can be found in def main()

Execute steps:
```bash
pipenv install
make build
make test
make deploy
```

## Cleanup
```bash
make clean
```