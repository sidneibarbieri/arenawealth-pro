# Compliance and Regulatory Framing

## Current Position

ArenaWealth Pro is a **portfolio analysis and decision-support workbench**.
It provides tools for:

- Organizing and visualizing portfolio data.
- Scoring holdings against configurable quantitative criteria.
- Surfacing data-source health and provenance.
- Logging and replaying recommendation runs.

It does **not** provide:

- Personalized investment advice.
- Trade execution.
- Custody of funds or securities.
- Suitability assessments.

---

## Applicable Regulatory Frameworks

### United States
- **Relevant law**: Investment Advisers Act of 1940 (SEC).
- **Threshold**: Providing investment advice for compensation requires RIA
  registration with the SEC or state authority.
- **Our position**: Analysis tools without personalized advice and without
  compensation for advice are generally excluded from the definition of
  "investment adviser." We provide tools, not advice.
- **Risk boundary**: If the product is marketed as "recommending" specific
  securities to specific users for compensation, SEC review is required.

### Brazil
- **Relevant authority**: CVM (Comissão de Valores Mobiliários).
- **CVM Instruction 592**: Sets requirements for investment advisors.
- **Our position**: Portfolio organization and scoring tools for self-directed
  investors do not constitute advisory services under CVM 592 provided no
  personalized guidance is given for compensation.

### European Union
- **Relevant law**: MiFID II.
- **Our position**: Not currently targeting EU distribution. MiFID II review
  required before EU launch.

---

## Product Guardrails That Support This Framing

1. The recommendation engine generates ranked orders based on deterministic
   policy, not personalized suitability assessment.
2. No user profile, risk tolerance questionnaire, or investment goal is
   stored or used in scoring.
3. All output is labeled as analysis output, not advice.
4. The system does not execute trades.
5. The system does not hold or manage user funds.

---

## Path to Licensed Operation

If the product expands to personalized recommendations with suitability
assessment and charging users for advice:

- US: Apply for RIA registration (SEC or state, depending on AUM threshold).
- Brazil: Register as Assessor de Investimentos with ANCORD/CVM.
- Consider white-labeling to a licensed advisor as the initial route.

---

## For Pitch Purposes

When asked about compliance:

> "The current product is a decision-support tool, not an investment adviser.
> It organizes your portfolio, shows data provenance, and surfaces quantitative
> scores — you make the decision. We know the regulated advice path and have
> scoped the product to stay clearly outside it until we pursue licensing."
