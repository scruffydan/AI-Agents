---
name: implementation-workflow
description: Use when implementing complex features, substantial refactors, or high-risk changes requiring coordinated architecture, testing, and delivery decisions.
---

# Implementation Workflow

Use the following areas as a reference for complex changes. Choose the steps
relevant to the actual users, lifespan, and tolerance for downtime or data loss;
do not turn every checklist item into a requirement for a small personal tool.
Reuse established decisions and existing dependencies where adequate.

Use `brainstorming` for unresolved design choices and `mode-thorough-plan` for an
analysis-only request. Keep implementation focused, verify meaningful behavior
changes, and optimize when requirements or measurements show a problem.

## Implementation Methodology

### 1. Requirements Analysis
**Deep understanding of technical specifications and acceptance criteria**

- Review all requirements and user stories thoroughly
- Identify functional and non-functional requirements
- Clarify ambiguous requirements with stakeholders
- Define clear acceptance criteria
- Document assumptions and constraints
- Identify dependencies on other systems or components

### 2. Architecture Planning
**Component design, data flow, and integration patterns**

- Design system architecture and component interactions
- Define data models and schemas
- Plan API contracts and interfaces
- Identify integration points with existing systems
- Consider scalability and performance requirements
- Document architecture decisions and rationale
- Create sequence diagrams for complex flows

### 3. Implementation Strategy
**Phased development approach with incremental delivery**

- Break work into small, testable increments
- Prioritize critical path and high-risk items
- Plan for iterative development and feedback
- Define milestones and checkpoints
- Consider backward compatibility requirements
- Plan for feature flags and gradual rollout
- Identify opportunities for parallel development

### 4. Quality Assurance
**Testing, code review, and performance validation**

- Write unit tests for new functionality
- Create integration tests for system interactions
- Develop end-to-end tests for critical user flows
- Perform code reviews with peers
- Validate performance against requirements
- Test error handling and edge cases
- Verify accessibility and usability standards

### 5. Security Review
**Vulnerability assessment and security best practices implementation**

When a specialist review is warranted, use the `code-security` agent through the
environment's supported tools and permissions.

For manual review, verify:
- Review code for common vulnerabilities (OWASP Top 10)
- Validate authentication and authorization logic
- Ensure proper input validation and sanitization
- Check for secure data handling and encryption
- Review dependencies for known vulnerabilities
- Validate security headers and configurations
- Perform threat modeling for sensitive features



### 6. Optimization
**Performance tuning and resource efficiency improvements**

- Profile code to identify bottlenecks
- Optimize database queries and indexes
- Minimize network requests and payload sizes
- Implement caching strategies where appropriate
- Review memory usage and potential leaks
- Optimize bundle sizes and load times
- Consider lazy loading and code splitting

## Completion

Use `verification-before-completion` for observed checks and `update-readme` for
README and existing AGENTS.md accuracy. Document substantial decisions when
useful. Continue within existing authorization; commits, external messages,
pushing, and deployment remain subject to user and repository instructions.
