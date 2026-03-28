# Compliance Framework

This document describes how Jays-Graphic-Arts maintains full compliance with legal, data-privacy, intellectual-property, and financial regulations while operating an autonomous AI-driven business.

---

## Table of Contents

1. [Data Privacy and Protection](#1-data-privacy-and-protection)
2. [Intellectual Property and Copyright](#2-intellectual-property-and-copyright)
3. [Financial Regulations](#3-financial-regulations)
4. [Accessibility Standards](#4-accessibility-standards)
5. [AI Ethics and Responsible Use](#5-ai-ethics-and-responsible-use)
6. [Content Moderation](#6-content-moderation)
7. [Record Retention](#7-record-retention)
8. [Third-Party Vendor Compliance](#8-third-party-vendor-compliance)
9. [Compliance Review Schedule](#9-compliance-review-schedule)

---

## 1. Data Privacy and Protection

### Applicable Regulations

| Regulation | Jurisdiction | Status |
|---|---|---|
| GDPR (General Data Protection Regulation) | European Union | ✅ Compliant |
| CCPA (California Consumer Privacy Act) | California, USA | ✅ Compliant |
| POPIA (Protection of Personal Information Act) | South Africa | ✅ Compliant |
| PIPEDA (Personal Information Protection and Electronic Documents Act) | Canada | ✅ Compliant |
| UK GDPR | United Kingdom | ✅ Compliant |

### Data Handling Principles

1. **Lawful basis**: Personal data is only processed where a lawful basis exists (contract performance, legitimate interest, or explicit consent).
2. **Data minimisation**: Only data necessary for the specific task is collected and retained.
3. **Purpose limitation**: Data collected for one purpose is never repurposed without a new lawful basis.
4. **Storage limitation**: Personal data is automatically deleted or anonymised at the end of its retention period (see [Record Retention](#7-record-retention)).
5. **Accuracy**: Client records are validated at intake and updated whenever a change is received.
6. **Security**: All personal data is encrypted at rest (AES-256) and in transit (TLS 1.3).

### Client Rights

The AI handles data-subject requests automatically:

| Right | Supported | Typical Response Time |
|---|---|---|
| Right of access (subject access request) | ✅ Yes | Within 72 hours |
| Right to rectification | ✅ Yes | Immediate |
| Right to erasure ("right to be forgotten") | ✅ Yes | Within 30 days |
| Right to data portability | ✅ Yes | Within 72 hours (JSON/CSV export) |
| Right to object to processing | ✅ Yes | Immediate suspension of processing |
| Right not to be subject to automated decision-making | ✅ Yes | Human review option always available |

### Data Processing Agreements
A GDPR-compliant Data Processing Agreement (DPA) is automatically generated and offered to any client who requests one. Sub-processor lists are maintained and updated quarterly.

---

## 2. Intellectual Property and Copyright

### Ownership of AI-Generated Work

All creative work produced for a client is fully transferred to that client upon payment of the final invoice, as documented in the standard service agreement. The company retains no licence to reuse client-specific work.

### Third-Party Assets

Every design asset that incorporates licensed stock imagery, fonts, or other third-party materials is tracked in an asset registry. The AI:

- Verifies that the licence for every used asset permits the intended use (commercial, print, digital, etc.)
- Documents licence scope in the project delivery notes
- Automatically flags assets approaching usage limits or licence expiry

### Trademark Clearance

Before delivery of any logo or brand identity work:

1. The AI runs the design concepts against USPTO, EUIPO, and WIPO trademark databases
2. A keyword analysis flags visually or phonetically similar registered marks
3. Any potential conflict is escalated to a human reviewer before the work is delivered

### Copyright Notice

Where requested, the AI generates appropriate copyright notices and DMCA/EUCD takedown templates for client use.

---

## 3. Financial Regulations

### Tax Compliance

- Invoices include the correct tax (VAT, GST, or sales tax) based on the client's billing jurisdiction, determined automatically from address data
- Tax identification numbers are validated at client onboarding
- Quarterly tax summary exports are generated in a format suitable for submission to an accountant or tax authority
- No tax advice is provided; clients are directed to qualified tax professionals for jurisdiction-specific questions

### Anti-Money Laundering (AML)

- New client records are screened against OFAC, EU, and UN sanctions lists at onboarding and on a weekly rolling basis
- Transactions above $10,000 trigger a manual review and are flagged for Suspicious Activity Report (SAR) consideration
- Full transaction records are retained for 5 years in accordance with AML recordkeeping requirements

### Payment Card Industry (PCI DSS)

- No payment card data is stored by the system; all card processing is handled by PCI-DSS-certified payment processors (Stripe, PayPal)
- The system is SAQ-A compliant (fully outsourced card processing)

---

## 4. Accessibility Standards

All digital assets produced for clients are evaluated for accessibility compliance where applicable:

| Standard | Scope | Compliance Target |
|---|---|---|
| WCAG 2.1 Level AA | Web and digital assets | ✅ Checked on all digital deliverables |
| Section 508 | US federal contractor clients | ✅ Available on request |
| EN 301 549 | EU public-sector clients | ✅ Available on request |

Accessibility checks include:

- Color contrast ratios for all text/background combinations
- Alt-text suggestions for all images
- Readable font size recommendations
- Link text clarity audits for web-format deliverables

---

## 5. AI Ethics and Responsible Use

### Prohibited Content

The AI will refuse to generate content that:

- Depicts or promotes violence, hate speech, or discrimination based on protected characteristics
- Infringes on a known copyright or trademark without authorisation
- Is deliberately misleading, fraudulent, or defamatory
- Contains personally identifiable information of third parties without consent
- Violates the laws of the client's or company's jurisdiction

All refusals are logged with the reason, the original request hash, and a client notification.

### Bias Monitoring

- The AI's outputs are audited quarterly for systematic bias in design style recommendations, pricing, and communication tone
- Audit findings are reviewed by a human ethics officer and, where bias is identified, corrective prompt-engineering updates are applied

### Transparency

- Clients are informed that their work is produced by an AI system as part of the service agreement
- The AI never impersonates a human during client communication
- Confidence scores and quality-check results are available to clients on request for any delivered project

---

## 6. Content Moderation

Every piece of content produced or published by the AI passes through an automated moderation pipeline before delivery or publication:

1. **Profanity and offensive language filter**: Removes or flags inappropriate language in all written content
2. **Brand safety check**: Ensures content does not appear alongside or reference controversial topics without client approval
3. **Image safety scan**: Detects and blocks the generation or use of unsafe or illegal imagery
4. **Legal keyword scan**: Flags terms that may create legal liability (unsupported health claims, guarantees, etc.)

Any content that triggers a moderation flag is quarantined and escalated for human review before it can be released.

---

## 7. Record Retention

| Data Category | Retention Period | Basis |
|---|---|---|
| Client contracts and signed agreements | 7 years after contract end | Legal/regulatory |
| Invoices and payment records | 7 years | Tax and financial regulations |
| Project files and deliverables | 5 years after delivery | Client agreement |
| Client communications (email, chat) | 3 years | Business operations |
| Audit logs | 7 years | Legal/regulatory |
| Marketing data (newsletter, analytics) | 2 years or until opt-out | GDPR/CCPA |
| Applicant/HR records | 1 year (unsuccessful) / duration of engagement + 7 years (engaged) | Employment law |

At the end of each retention period, data is automatically anonymised or securely deleted. Deletion certificates are generated and retained.

---

## 8. Third-Party Vendor Compliance

All third-party vendors who process personal data on behalf of Jays-Graphic-Arts are required to:

- Execute a Data Processing Agreement
- Demonstrate compliance with applicable data-protection regulations (GDPR Article 28 requirements)
- Maintain ISO 27001 certification or equivalent
- Notify us within 24 hours of any security incident affecting our data

Current sub-processors are reviewed annually, and the list is available to clients on request.

---

## 9. Compliance Review Schedule

| Review | Frequency | Responsible |
|---|---|---|
| Data privacy policy review | Annual | Compliance officer |
| Sub-processor list update | Quarterly | Operations AI + human sign-off |
| OFAC/sanctions screening update | Weekly (automated) | AI system |
| IP/trademark database sync | Monthly | AI system |
| Accessibility audit (sample deliverables) | Quarterly | QA AI + human sign-off |
| Content moderation policy review | Bi-annual | Compliance officer |
| Full compliance audit (external) | Annual | Independent auditor |

---

*Last updated: March 2026*
