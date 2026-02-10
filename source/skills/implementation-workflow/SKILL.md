---
name: implementation-workflow
description: Six-phase implementation method for complex work: requirements, architecture, strategy, QA, security, optimization. Use for multi-step features, refactors, or high-risk changes that need structured planning and verification.
---

# Implementation Workflow

This document outlines the systematic approach for implementing complex technical solutions.

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

For automated security review, invoke the **@code-security** agent with target files.

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

## Application of Workflow

- **Simple features**: May skip formal architecture planning
- **Complex features**: Full workflow recommended
- **Bug fixes**: Focus on quality assurance and testing
- **Refactoring**: Emphasize testing and incremental changes
- **Performance work**: Deep dive into optimization phase

## Best Practices

- **Document decisions**: Keep a record of why choices were made
- **Communicate early**: Share design proposals before implementation
- **Fail fast**: Identify issues in planning rather than implementation
- **Iterate**: Be prepared to revise plans based on new information
- **Measure**: Use metrics to validate improvements
