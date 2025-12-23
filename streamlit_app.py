"""
AWS Guardrails Platform - Enterprise Edition
=============================================
Policy as Code governance platform for AWS Organizations
Using Terraform, KICS, OPA, and GitHub-based workflows

Real-world enterprise architecture:
- Policies stored in GitHub
- KICS + OPA validation on every PR
- Terraform deploys SCPs, Config Rules, StackSets
- Security Hub aggregates findings
- This dashboard provides visibility and control
"""

import streamlit as st
from datetime import datetime, timedelta
import json
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random

# Simple inline authentication for Streamlit Cloud compatibility
# This avoids module import issues entirely

def authenticate(username: str, password: str):
    """Authenticate user credentials"""
    users = {
        "admin": {"password": "admin123", "role": "SUPER_ADMIN", "full_name": "Admin User"},
        "security_lead": {"password": "security123", "role": "SECURITY_ADMIN", "full_name": "Security Lead"},
        "compliance_mgr": {"password": "compliance123", "role": "COMPLIANCE_OFFICER", "full_name": "Compliance Manager"},
        "cloud_arch": {"password": "architect123", "role": "CLOUD_ARCHITECT", "full_name": "Cloud Architect"},
        "finops": {"password": "finops123", "role": "FINOPS_ANALYST", "full_name": "FinOps Analyst"},
        "devsecops": {"password": "devsec123", "role": "DEVSECOPS_ENGINEER", "full_name": "DevSecOps Engineer"},
        "auditor": {"password": "audit123", "role": "AUDITOR", "full_name": "Auditor"},
        "viewer": {"password": "viewer123", "role": "VIEWER", "full_name": "Viewer"},
    }
    if username in users and users[username]["password"] == password:
        return {"username": username, **{k: v for k, v in users[username].items() if k != "password"}}
    return None

def render_login_page():
    """Render login page"""
    st.markdown("""
    <style>
    .login-container { max-width: 400px; margin: 100px auto; padding: 2rem; 
        background: linear-gradient(145deg, #1a1f2e, #111827); border-radius: 16px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🛡️ AWS Guardrails")
        st.markdown("##### Policy as Code Platform")
        st.markdown("---")
        
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Sign In", use_container_width=True, type="primary"):
            user = authenticate(username, password)
            if user:
                st.session_state.current_user = user
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        with st.expander("Demo Credentials"):
            st.markdown("**admin** / admin123")
            st.markdown("**security_lead** / security123")
            st.markdown("**viewer** / viewer123")

def logout():
    """Logout user"""
    if 'current_user' in st.session_state:
        del st.session_state.current_user

def get_current_user():
    """Get current user from session"""
    return st.session_state.get('current_user')

# Page configuration
st.set_page_config(
    page_title="AWS Guardrails Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Authentication check
if 'current_user' not in st.session_state:
    render_login_page()
    st.stop()

current_user = st.session_state.current_user

# Custom CSS - Dark Enterprise Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #0a0f1a 0%, #0d1321 100%);
    }
    
    /* Header Styles */
    .main-header {
        background: linear-gradient(135deg, #1a1f2e 0%, #111827 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        border: 1px solid #374151;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .header-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
    }
    
    .header-subtitle {
        color: #9ca3af;
        font-size: 0.9rem;
        margin-top: 0.25rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, #1a1f2e, #111827);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        border-color: #6366f1;
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        line-height: 1.2;
    }
    
    .metric-label {
        color: #9ca3af;
        font-size: 0.85rem;
        margin-top: 0.5rem;
    }
    
    /* Status Colors */
    .status-healthy { color: #10b981; }
    .status-warning { color: #f59e0b; }
    .status-critical { color: #ef4444; }
    .status-info { color: #3b82f6; }
    
    /* GitHub Integration Card */
    .github-card {
        background: linear-gradient(145deg, #161b22, #0d1117);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Pipeline Status */
    .pipeline-stage {
        display: inline-flex;
        align-items: center;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        margin-right: 0.5rem;
        font-size: 0.85rem;
    }
    
    .stage-success { background: #10b98120; color: #10b981; border: 1px solid #10b98140; }
    .stage-running { background: #3b82f620; color: #3b82f6; border: 1px solid #3b82f640; }
    .stage-pending { background: #6b728020; color: #9ca3af; border: 1px solid #6b728040; }
    .stage-failed { background: #ef444420; color: #ef4444; border: 1px solid #ef444440; }
    
    /* Info Cards */
    .info-card {
        background: linear-gradient(145deg, #1a1f2e, #111827);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    
    /* Tool Badges */
    .tool-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-right: 6px;
    }
    
    .badge-terraform { background: #7c3aed20; color: #a78bfa; border: 1px solid #7c3aed40; }
    .badge-kics { background: #06b6d420; color: #22d3ee; border: 1px solid #06b6d440; }
    .badge-opa { background: #10b98120; color: #34d399; border: 1px solid #10b98140; }
    .badge-github { background: #6b728020; color: #e5e7eb; border: 1px solid #6b728040; }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HEADER
# ============================================================================

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown(f"""
    <div class="main-header">
        <div>
            <h1 class="header-title">🛡️ AWS Guardrails Platform</h1>
            <p class="header-subtitle">Policy as Code Governance • Terraform • KICS • OPA</p>
        </div>
        <div style="text-align: right;">
            <div style="color: #ffffff; font-weight: 500;">👤 {current_user.get('full_name', 'User')}</div>
            <div style="color: #9ca3af; font-size: 0.8rem;">{current_user.get('role', 'USER').replace('_', ' ')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🚪 Sign Out", use_container_width=True):
        logout()
        st.rerun()

# ============================================================================
# REAL-TIME STATUS BAR
# ============================================================================

st.markdown("### 📊 Platform Status")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value status-healthy">487</div>
        <div class="metric-label">AWS Accounts</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value status-info">156</div>
        <div class="metric-label">Policies in Git</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value status-healthy">94.2%</div>
        <div class="metric-label">Policy Compliance</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value status-warning">12</div>
        <div class="metric-label">Open PRs</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value status-critical">23</div>
        <div class="metric-label">KICS Findings</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value status-healthy">✓</div>
        <div class="metric-label">Pipeline Healthy</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================================
# MAIN CONTENT TABS
# ============================================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Overview",
    "📦 GitHub & CI/CD",
    "🔍 Policy Scans",
    "☁️ AWS Compliance",
    "📈 Trends"
])

# ============================================================================
# TAB 1: OVERVIEW
# ============================================================================

with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🏗️ Architecture Overview")
        
        st.markdown("""
        <div class="info-card">
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <span class="tool-badge badge-github">GitHub</span>
                <span style="color: #6b7280; margin: 0 0.5rem;">→</span>
                <span class="tool-badge badge-kics">KICS</span>
                <span class="tool-badge badge-opa">OPA</span>
                <span style="color: #6b7280; margin: 0 0.5rem;">→</span>
                <span class="tool-badge badge-terraform">Terraform</span>
                <span style="color: #6b7280; margin: 0 0.5rem;">→</span>
                <span style="color: #f59e0b; font-weight: 600;">AWS Organization</span>
            </div>
            <p style="color: #9ca3af; margin: 0; font-size: 0.9rem;">
                Policies defined as code in GitHub • Validated by KICS & OPA on every PR • 
                Deployed via Terraform to 487 AWS accounts across 8 portfolios
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Policy Types Chart
        st.markdown("#### Policy Distribution by Type")
        
        policy_types = ['SCPs', 'OPA/Rego', 'Config Rules', 'Sentinel', 'Custom']
        policy_counts = [24, 45, 52, 18, 17]
        
        fig_policies = go.Figure(data=[go.Bar(
            x=policy_types,
            y=policy_counts,
            marker=dict(
                color=['#8b5cf6', '#10b981', '#f59e0b', '#3b82f6', '#6b7280'],
                line=dict(color='rgba(255,255,255,0.2)', width=1)
            ),
            text=policy_counts,
            textposition='outside',
            textfont=dict(color='white', size=12)
        )])
        
        fig_policies.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='#e5e7eb'), showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#9ca3af'))
        )
        st.plotly_chart(fig_policies, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔗 Quick Links")
        
        st.markdown("""
        <div class="github-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.25rem; margin-right: 0.5rem;">📁</span>
                <span style="color: #e5e7eb; font-weight: 500;">Policy Repository</span>
            </div>
            <code style="color: #58a6ff; font-size: 0.8rem;">company/aws-governance-policies</code>
            <div style="margin-top: 0.5rem; color: #8b949e; font-size: 0.8rem;">
                Last commit: 2 hours ago
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="github-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.25rem; margin-right: 0.5rem;">🔄</span>
                <span style="color: #e5e7eb; font-weight: 500;">Latest Pipeline</span>
            </div>
            <div style="color: #10b981; font-weight: 500;">✓ All checks passed</div>
            <div style="margin-top: 0.5rem; color: #8b949e; font-size: 0.8rem;">
                Run #1247 • 15 minutes ago
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="github-card">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.25rem; margin-right: 0.5rem;">📋</span>
                <span style="color: #e5e7eb; font-weight: 500;">Terraform Cloud</span>
            </div>
            <div style="color: #a78bfa; font-weight: 500;">aws-guardrails workspace</div>
            <div style="margin-top: 0.5rem; color: #8b949e; font-size: 0.8rem;">
                State: Healthy • Drift: None
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### 📊 Compliance by Framework")
        
        frameworks_mini = ['CIS', 'SOC2', 'PCI', 'HIPAA']
        scores_mini = [96, 94, 88, 92]
        
        fig_mini = go.Figure(data=[go.Bar(
            y=frameworks_mini,
            x=scores_mini,
            orientation='h',
            marker=dict(color=['#10b981' if s >= 90 else '#f59e0b' for s in scores_mini]),
            text=[f'{s}%' for s in scores_mini],
            textposition='inside',
            textfont=dict(color='white', size=11)
        )])
        
        fig_mini.update_layout(
            height=180,
            margin=dict(l=0, r=10, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(range=[0, 100], showgrid=False, showticklabels=False),
            yaxis=dict(tickfont=dict(color='#e5e7eb', size=11))
        )
        st.plotly_chart(fig_mini, use_container_width=True)

# ============================================================================
# TAB 2: GITHUB & CI/CD
# ============================================================================

with tab2:
    st.markdown("#### 🔄 CI/CD Pipeline Status")
    
    # Pipeline visualization
    stages = [
        {"name": "Checkout", "status": "success", "time": "2s"},
        {"name": "KICS Scan", "status": "success", "time": "45s"},
        {"name": "OPA Validate", "status": "success", "time": "12s"},
        {"name": "Terraform Plan", "status": "success", "time": "1m 23s"},
        {"name": "Security Review", "status": "success", "time": "Manual"},
        {"name": "Terraform Apply", "status": "success", "time": "2m 45s"},
        {"name": "Verify", "status": "success", "time": "30s"},
    ]
    
    pipeline_html = '<div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1.5rem;">'
    for stage in stages:
        status_class = f"stage-{stage['status']}"
        icon = "✓" if stage['status'] == 'success' else "⏳" if stage['status'] == 'running' else "○"
        pipeline_html += f'<div class="pipeline-stage {status_class}">{icon} {stage["name"]} <span style="opacity: 0.7; margin-left: 0.5rem;">{stage["time"]}</span></div>'
    pipeline_html += '</div>'
    st.markdown(pipeline_html, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📥 Recent Pull Requests")
        
        prs = [
            {"number": "#156", "title": "Add IMDSv2 enforcement SCP for all OUs", "author": "security-team", "status": "🟢 Merged", "checks": "✓ All passed", "time": "2 hours ago"},
            {"number": "#155", "title": "Update OPA policy for RDS encryption", "author": "cloud-arch", "status": "🟡 Open", "checks": "✓ All passed", "time": "5 hours ago"},
            {"number": "#154", "title": "New Sentinel policy for cost tags", "author": "finops", "status": "🟡 Open", "checks": "⚠ 1 warning", "time": "1 day ago"},
            {"number": "#153", "title": "Fix KICS false positive in S3 module", "author": "devsecops", "status": "🔴 Failed", "checks": "✗ KICS failed", "time": "1 day ago"},
        ]
        
        for pr in prs:
            status_color = "#10b981" if "Merged" in pr['status'] else "#f59e0b" if "Open" in pr['status'] else "#ef4444"
            st.markdown(f"""
            <div class="github-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <span style="color: #58a6ff; font-weight: 600;">{pr['number']}</span>
                        <span style="color: #e5e7eb; margin-left: 0.5rem;">{pr['title']}</span>
                    </div>
                    <span style="color: {status_color};">{pr['status']}</span>
                </div>
                <div style="color: #8b949e; font-size: 0.8rem; margin-top: 0.5rem;">
                    👤 {pr['author']} • {pr['checks']} • ⏱️ {pr['time']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📊 Pipeline Metrics (7 Days)")
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        runs = [23, 31, 28, 35, 29, 12, 8]
        failures = [2, 1, 3, 2, 1, 0, 1]
        
        fig_pipeline = go.Figure()
        
        fig_pipeline.add_trace(go.Bar(
            x=days, y=runs, name='Total Runs',
            marker=dict(color='#3b82f6'),
            text=runs, textposition='outside', textfont=dict(color='white', size=10)
        ))
        
        fig_pipeline.add_trace(go.Bar(
            x=days, y=failures, name='Failures',
            marker=dict(color='#ef4444')
        ))
        
        fig_pipeline.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickfont=dict(color='#e5e7eb')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#9ca3af')),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(color='#e5e7eb')),
            barmode='group'
        )
        st.plotly_chart(fig_pipeline, use_container_width=True)
        
        # Repository structure
        st.markdown("#### 📁 Repository Structure")
        st.code("""
aws-governance-policies/
├── policies/
│   ├── scp/              # Service Control Policies
│   ├── opa/              # OPA Rego policies  
│   ├── sentinel/         # Terraform Sentinel
│   └── config-rules/     # AWS Config rules
├── terraform/
│   ├── scp-deployment/   # Deploy SCPs
│   ├── config-rules/     # Deploy Config
│   └── stacksets/        # StackSet modules
└── .github/workflows/    # CI/CD pipelines
        """, language=None)

# ============================================================================
# TAB 3: POLICY SCANS (KICS + OPA)
# ============================================================================

with tab3:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 KICS Scan Results")
        st.markdown("*Infrastructure as Code security scanning*")
        
        # KICS metrics
        kics_col1, kics_col2, kics_col3, kics_col4 = st.columns(4)
        with kics_col1:
            st.metric("High", "3", "-2")
        with kics_col2:
            st.metric("Medium", "12", "+1")
        with kics_col3:
            st.metric("Low", "8", "0")
        with kics_col4:
            st.metric("Files Scanned", "234")
        
        # KICS findings chart
        fig_kics = go.Figure(data=[go.Pie(
            values=[211, 8, 12, 3],
            labels=['Passed', 'Low', 'Medium', 'High'],
            hole=0.65,
            marker=dict(colors=['#10b981', '#6b7280', '#f59e0b', '#ef4444']),
            textinfo='label+value',
            textfont=dict(size=10, color='white')
        )])
        fig_kics.update_layout(
            height=220,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            showlegend=False,
            annotations=[dict(text='<b>234</b><br>Checks', x=0.5, y=0.5, font=dict(size=12, color='white'), showarrow=False)]
        )
        st.plotly_chart(fig_kics, use_container_width=True)
        
        # Top KICS findings
        st.markdown("**Top Findings:**")
        kics_findings = [
            {"severity": "HIGH", "query": "S3 Bucket Without Encryption", "file": "terraform/modules/s3/main.tf", "line": 23},
            {"severity": "HIGH", "query": "Security Group Open to Internet", "file": "terraform/modules/vpc/security.tf", "line": 45},
            {"severity": "MEDIUM", "query": "RDS Without Multi-AZ", "file": "terraform/modules/rds/main.tf", "line": 67},
        ]
        
        for finding in kics_findings:
            sev_color = "#ef4444" if finding['severity'] == "HIGH" else "#f59e0b"
            st.markdown(f"""
            <div style="background: #1a1f2e; border-left: 3px solid {sev_color}; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 0 8px 8px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #e5e7eb;">{finding['query']}</span>
                    <span style="color: {sev_color}; font-weight: 600;">{finding['severity']}</span>
                </div>
                <div style="color: #6b7280; font-size: 0.8rem; margin-top: 0.25rem;">
                    📁 {finding['file']}:{finding['line']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 📋 OPA Policy Evaluation")
        st.markdown("*Terraform plan validation against Rego policies*")
        
        # OPA metrics
        opa_col1, opa_col2, opa_col3, opa_col4 = st.columns(4)
        with opa_col1:
            st.metric("Policies", "45")
        with opa_col2:
            st.metric("Passed", "42", "+2")
        with opa_col3:
            st.metric("Violations", "3", "-1")
        with opa_col4:
            st.metric("Resources", "156")
        
        # OPA results
        opa_policies = [
            {"name": "require_encryption", "status": "PASS", "resources": 34},
            {"name": "restrict_regions", "status": "PASS", "resources": 28},
            {"name": "require_tags", "status": "FAIL", "resources": 12},
            {"name": "security_group_rules", "status": "PASS", "resources": 18},
            {"name": "iam_least_privilege", "status": "WARN", "resources": 8},
        ]
        
        for policy in opa_policies:
            status_color = "#10b981" if policy['status'] == "PASS" else "#ef4444" if policy['status'] == "FAIL" else "#f59e0b"
            st.markdown(f"""
            <div style="background: #1a1f2e; border: 1px solid #374151; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #e5e7eb; font-family: 'JetBrains Mono', monospace;">{policy['name']}.rego</span>
                    <span style="color: {status_color}; font-weight: 600;">{policy['status']}</span>
                </div>
                <div style="color: #6b7280; font-size: 0.8rem; margin-top: 0.25rem;">
                    Evaluated {policy['resources']} resources
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        st.markdown("**Sample OPA Policy:**")
        st.code("""
# policies/opa/require_encryption.rego
package terraform.aws

deny[msg] {
    resource := input.resource_changes[_]
    resource.type == "aws_s3_bucket"
    not has_encryption(resource)
    msg := sprintf("S3 bucket '%s' must have encryption", 
                   [resource.address])
}
        """, language="rego")

# ============================================================================
# TAB 4: AWS COMPLIANCE
# ============================================================================

with tab4:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### 🏢 Compliance by Organizational Unit")
        
        ous = ['Production', 'Development', 'Staging', 'Security', 'Data Analytics', 'Shared Services', 'Sandbox']
        compliance_scores = [98, 94, 96, 99, 92, 95, 78]
        accounts = [145, 98, 45, 32, 67, 65, 35]
        colors = ['#10b981' if s >= 90 else '#f59e0b' if s >= 80 else '#ef4444' for s in compliance_scores]
        
        fig_ou = go.Figure()
        
        fig_ou.add_trace(go.Bar(
            y=ous,
            x=compliance_scores,
            orientation='h',
            marker=dict(color=colors),
            text=[f'{s}% ({a} accounts)' for s, a in zip(compliance_scores, accounts)],
            textposition='inside',
            textfont=dict(color='white', size=11)
        ))
        
        fig_ou.update_layout(
            height=350,
            margin=dict(l=0, r=20, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(range=[0, 100], showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#9ca3af')),
            yaxis=dict(tickfont=dict(color='#e5e7eb', size=11))
        )
        st.plotly_chart(fig_ou, use_container_width=True)
    
    with col2:
        st.markdown("#### 🛡️ Active Guardrails")
        
        guardrails = [
            {"name": "Deny Public S3", "type": "SCP", "status": "Active", "accounts": 487},
            {"name": "Require IMDSv2", "type": "SCP", "status": "Active", "accounts": 487},
            {"name": "Restrict Regions", "type": "SCP", "status": "Active", "accounts": 452},
            {"name": "S3 Encryption", "type": "Config", "status": "Active", "accounts": 487},
            {"name": "EBS Encryption", "type": "Config", "status": "Active", "accounts": 487},
        ]
        
        for gr in guardrails:
            type_color = "#8b5cf6" if gr['type'] == "SCP" else "#f59e0b"
            st.markdown(f"""
            <div style="background: #1a1f2e; border: 1px solid #374151; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #e5e7eb;">{gr['name']}</span>
                    <span style="background: {type_color}20; color: {type_color}; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem;">{gr['type']}</span>
                </div>
                <div style="color: #6b7280; font-size: 0.8rem; margin-top: 0.25rem;">
                    🟢 {gr['status']} • {gr['accounts']} accounts
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Config Rules compliance
    st.markdown("#### 📊 AWS Config Rules Compliance")
    
    config_rules = pd.DataFrame({
        "Rule": ["s3-bucket-server-side-encryption-enabled", "ec2-imdsv2-check", "rds-storage-encrypted", "ebs-encrypted-volumes", "iam-password-policy"],
        "Compliant": [487, 485, 456, 478, 487],
        "Non-Compliant": [0, 2, 31, 9, 0],
        "Compliance %": ["100%", "99.6%", "93.6%", "98.2%", "100%"],
        "Last Evaluated": ["5 min ago", "5 min ago", "5 min ago", "5 min ago", "5 min ago"]
    })
    
    st.dataframe(config_rules, use_container_width=True, hide_index=True)

# ============================================================================
# TAB 5: TRENDS
# ============================================================================

with tab5:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Compliance Score Trend (90 Days)")
        
        dates = pd.date_range(end=datetime.now(), periods=90, freq='D')
        scores = [85 + i*0.1 + random.uniform(-1, 1) for i in range(90)]
        scores[-1] = 94.2
        
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=dates, y=scores,
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.2)',
            line=dict(color='#10b981', width=2),
            mode='lines',
            hovertemplate='%{x|%b %d}<br>Score: %{y:.1f}%<extra></extra>'
        ))
        
        fig_trend.add_hline(y=90, line_dash="dash", line_color="#f59e0b", annotation_text="Target: 90%")
        
        fig_trend.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickfont=dict(color='#9ca3af')),
            yaxis=dict(range=[80, 100], showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#9ca3af'))
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col2:
        st.markdown("#### 🔍 Security Findings Trend")
        
        weeks = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7', 'W8']
        critical = [5, 4, 6, 3, 4, 2, 3, 2]
        high = [23, 25, 22, 20, 18, 19, 16, 15]
        medium = [67, 65, 70, 62, 58, 55, 52, 48]
        
        fig_findings = go.Figure()
        
        fig_findings.add_trace(go.Scatter(x=weeks, y=critical, name='Critical', line=dict(color='#ef4444', width=2), mode='lines+markers'))
        fig_findings.add_trace(go.Scatter(x=weeks, y=high, name='High', line=dict(color='#f59e0b', width=2), mode='lines+markers'))
        fig_findings.add_trace(go.Scatter(x=weeks, y=medium, name='Medium', line=dict(color='#a855f7', width=2), mode='lines+markers'))
        
        fig_findings.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False, tickfont=dict(color='#9ca3af')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#9ca3af')),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(color='#e5e7eb'))
        )
        st.plotly_chart(fig_findings, use_container_width=True)
    
    # Deployment frequency
    st.markdown("#### 🚀 Policy Deployment Frequency")
    
    months = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    scp_deploys = [8, 12, 10, 15, 11, 14]
    config_deploys = [15, 18, 22, 19, 25, 21]
    opa_updates = [23, 28, 31, 35, 29, 33]
    
    fig_deploys = go.Figure()
    
    fig_deploys.add_trace(go.Bar(x=months, y=scp_deploys, name='SCP Deployments', marker_color='#8b5cf6'))
    fig_deploys.add_trace(go.Bar(x=months, y=config_deploys, name='Config Rules', marker_color='#f59e0b'))
    fig_deploys.add_trace(go.Bar(x=months, y=opa_updates, name='OPA Policy Updates', marker_color='#10b981'))
    
    fig_deploys.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickfont=dict(color='#e5e7eb')),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', tickfont=dict(color='#9ca3af')),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, font=dict(color='#e5e7eb')),
        barmode='group'
    )
    st.plotly_chart(fig_deploys, use_container_width=True)

# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.markdown("### 🛡️ AWS Guardrails")
    st.markdown("Policy as Code Platform")
    
    st.markdown("---")
    
    st.markdown("**Quick Actions**")
    
    if st.button("🔄 Sync from GitHub", use_container_width=True):
        st.toast("Syncing policies from GitHub...")
    
    if st.button("🔍 Run KICS Scan", use_container_width=True):
        st.toast("Starting KICS security scan...")
    
    if st.button("📋 Validate OPA", use_container_width=True):
        st.toast("Running OPA policy validation...")
    
    if st.button("🚀 Trigger Deploy", use_container_width=True):
        st.warning("Requires approval for production")
    
    st.markdown("---")
    
    st.markdown("**System Status**")
    st.markdown("🟢 GitHub Connected")
    st.markdown("🟢 Terraform Cloud")
    st.markdown("🟢 AWS Organization")
    st.markdown("🟢 KICS Scanner")
    st.markdown("🟢 OPA Engine")
    
    st.markdown("---")
    
    st.markdown("**Environment**")
    st.selectbox("Target", ["Production", "Staging", "Development"], key="env_select")
    
    st.markdown("---")
    
    st.markdown(f"""
    <div style="color: #6b7280; font-size: 0.8rem; text-align: center;">
        Version 2.0.0<br>
        Policy as Code Edition<br>
        {datetime.now().strftime("%Y-%m-%d %H:%M")}
    </div>
    """, unsafe_allow_html=True)
