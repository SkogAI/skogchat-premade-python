# Quick Reference Guide

Choose your path based on your role and immediate needs:

## 🆕 New to Claude Code Framework?

**Start here**: [`README.md`](../README.md) → [`CLAUDE.md`](../CLAUDE.md) → [Customization Guide](../.claude/guides/customization-guide.md)

## 👨‍💻 Developer Quick Start

### By Technology Stack
| Technology | Best Practices Guide | Templates |
|------------|---------------------|-----------|
| **Node.js** | [nodejs-best-practices.md](../.claude/best_practices/nodejs-best-practices.md) | [PR Template](../.claude/templates/pull-request-template.md) |
| **Python** | [python-best-practices.md](../.claude/best_practices/python-best-practices.md) | [Code Review](../.claude/templates/code-review-checklist.md) |
| **Java** | [java-best-practices.md](../.claude/best_practices/java-best-practices.md) | [Task Spec](../.claude/templates/task-spec-template.md) |
| **Angular** | [angular-best-practices.md](../.claude/best_practices/angular-best-practices.md) | |
| **PHP** | [php-best-practices.md](../.claude/best_practices/php-best-practices.md) | |

### Common Commands
- **Start Session**: `<Health-Check>` - Monitor session health
- **JIRA Integration**: See [jira.md](../.claude/commands/jira.md)
- **Document Management**: See [document.md](../.claude/commands/document.md)

## 👥 Team Lead Quick Start

### Setup & Configuration
1. **Team Configuration**: [config/README.md](../.claude/config/README.md)
2. **Choose Template**: [Enterprise](../.claude/config/examples/enterprise-team.yaml) | [Startup](../.claude/config/examples/startup-team.yaml) | [Open Source](../.claude/config/examples/opensource-project.yaml)
3. **Run Setup**: `./scripts/customize-framework.sh`

### Management Tools
- **Session Management**: [session-management-guide.md](../.claude/guides/session-management-guide.md)
- **Handover Template**: [handover-template.md](../.claude/templates/handover-template.md)
- **Team Quick Reference**: [team-quick-reference.md](../.claude/templates/team-quick-reference.md)

## 🛠️ DevOps & Infrastructure

### Core Guides
- **Security**: [security-best-practices.md](../.claude/best_practices/security-best-practices.md) 
- **Docker**: [docker-best-practices.md](../.claude/best_practices/docker-best-practices.md)
- **Database**: [database-best-practices.md](../.claude/best_practices/database-best-practices.md)
- **API Design**: [api-design-best-practices.md](../.claude/best_practices/api-design-best-practices.md)
- **Logging**: [logging-monitoring-best-practices.md](../.claude/best_practices/logging-monitoring-best-practices.md)

## 🔧 Advanced Users

### MCP Integration
- **MCP Tools**: [mcp-best-practices.md](../.claude/best_practices/mcp-best-practices.md)
- **Custom Commands**: [commands/](../.claude/commands/) directory

### Customization
- **Custom Best Practices**: [custom-best-practice-template.md](../.claude/templates/custom-best-practice-template.md)
- **Best Practice Addendum**: [best-practice-addendum-template.md](../.claude/templates/best-practice-addendum-template.md)
- **Migration Guide**: [migration-guide-template.md](../.claude/templates/migration-guide-template.md)

## 🚨 Troubleshooting

### Common Issues
- **Session Problems**: [health-check.md](../.claude/commands/health-check.md)
- **GitHub Issues**: [fix-github-issues.md](../.claude/commands/fix-github-issues.md)
- **Configuration Problems**: [config/README.md](../.claude/config/README.md)

### Getting Help
1. Check the relevant best practices guide for your technology
2. Review templates for similar use cases
3. Use session health check: `<Health-Check>`
4. Create handover document: `<Handover01>`

---

📋 **Pro Tip**: Bookmark this page for quick access to all documentation!

*Last updated: 2025-06-30*