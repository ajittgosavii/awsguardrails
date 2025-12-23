# 🛡️ AWS Guardrails Platform

**Enterprise Policy as Code Governance for AWS Organizations**

A comprehensive governance platform that manages 500+ AWS accounts using Policy as Code principles with Terraform, KICS, OPA, and GitHub-based workflows.

![Platform](https://img.shields.io/badge/Platform-Streamlit-red)
![IaC](https://img.shields.io/badge/IaC-Terraform-purple)
![Scanner](https://img.shields.io/badge/Scanner-KICS-blue)
![Policy](https://img.shields.io/badge/Policy-OPA%2FRego-green)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              GitHub Repository                               │
│   aws-governance-policies/                                                   │
│   ├── policies/scp/          # Service Control Policies (JSON)              │
│   ├── policies/opa/          # OPA Rego validation policies                 │
│   ├── policies/sentinel/     # Terraform Sentinel policies                  │
│   ├── terraform/             # Terraform deployment modules                 │
│   └── .github/workflows/     # CI/CD pipelines                              │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                          PR / Push to main
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GitHub Actions CI/CD                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    KICS      │  │     OPA      │  │  Terraform   │  │  Terraform   │    │
│  │    Scan      │──│   Conftest   │──│    Plan      │──│    Apply     │    │
│  │  (IaC Sec)   │  │ (Policy Val) │  │              │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
                              Deploy to AWS
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AWS Organization                                   │
│  ├── Service Control Policies (SCPs)                                        │
│  ├── AWS Config Rules (via StackSets)                                       │
│  ├── Security Hub Standards                                                 │
│  └── 487 Member Accounts across 8 Portfolios                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Tool Integration

| Tool | Purpose | When Used |
|------|---------|-----------|
| **KICS** | IaC security scanning | Every PR - scans Terraform for vulnerabilities |
| **OPA/Conftest** | Policy validation | Every PR - validates Terraform plans against Rego policies |
| **Terraform** | Infrastructure deployment | On merge - deploys SCPs, Config Rules, StackSets |
| **Sentinel** | TFC/TFE policy enforcement | Optional - for Terraform Cloud/Enterprise |
| **GitHub Actions** | CI/CD orchestration | Automates the entire pipeline |

---

## 📦 Policy Repository Structure

```
aws-governance-policies/
├── .github/workflows/
│   ├── kics-scan.yml           # KICS security scanning
│   ├── opa-validate.yml        # OPA policy validation
│   └── terraform-deploy.yml    # Terraform deployment
├── policies/
│   ├── scp/                    # Service Control Policies (JSON)
│   ├── opa/                    # OPA Rego policies
│   ├── sentinel/               # Terraform Sentinel
│   └── config-rules/           # AWS Config Rules
├── terraform/
│   ├── modules/scp/            # SCP deployment module
│   ├── modules/config-rules/   # Config Rules module
│   └── environments/           # Environment-specific configs
└── docs/
```

---

## 🚀 Streamlit Cloud Deployment

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repository, set main file: `streamlit_app.py`
4. Configure secrets (optional for live AWS data)

---

## 👥 Demo Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Super Admin |
| security_lead | security123 | Security Admin |
| compliance_mgr | compliance123 | Compliance Officer |
| cloud_arch | architect123 | Cloud Architect |
| finops | finops123 | FinOps Analyst |
| devsecops | devsec123 | DevSecOps Engineer |
| auditor | audit123 | Auditor |
| viewer | viewer123 | Viewer |

---

## 📄 Pages

| Page | Description |
|------|-------------|
| 🏠 Dashboard | GitHub/CI status, policy compliance, scan results |
| 🏢 Account Management | 500+ AWS accounts management |
| 🛡️ Guardrails | SCPs, Config Rules, StackSets |
| ✅ Compliance Center | Multi-framework tracking |
| 🔐 DevSecOps Hub | Pipeline security |
| 🔍 Security Findings | Security Hub aggregation |
| 💰 Cost & FinOps | Cloud cost management |
| 🎛️ Control Center | Direct AWS operations |
| ✅ Approval Workflow | Change management |
| ⚙️ Admin Settings | System configuration |
| 📜 Policy as Code | GitHub, KICS, OPA, Terraform |

---

## 📋 Sample OPA Policy

```rego
package terraform.aws

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_encryption(resource)
    msg := sprintf("S3 bucket '%s' must have encryption", [resource.address])
}
```

---

## 🔒 Security Features

- RBAC with 8 predefined roles
- KICS IaC security scanning
- OPA policy validation
- Git-based policy versioning
- Approval workflows
- Full audit trail

---

## 🛠️ Local Development

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

MIT License
