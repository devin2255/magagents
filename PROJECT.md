# TRUMPTOPIA AI - Configuration

## Project Overview
A Trump-style US Government-inspired AI multi-agent system with:
- Three Branches: Legislative, Executive, Judicial
- DOGE (Department of Government Efficiency) oversight
- "You're Fired!" mechanism
- Truth Social messaging style

## Agent Structure

### Executive Branch (Cabinet)
- trump_president: POTUS, final decision maker
- state_dept: Foreign affairs, API interfaces
- treasury: Token budget, cost analysis
- defense: Security scanning, attack/defense
- commerce: Data analysis, market research
- energy: Compute scheduling, resource optimization
- justice: Compliance, legal review

### Legislative Branch (Congress)
- congress_senate: Upper chamber, bill review
- congress_house: Lower chamber, budget approval

### Judicial Branch (Courts)
- scotus: Supreme Court, final arbitration
- circuit_court: Circuit courts, initial review

### Oversight
- doge_musk: Efficiency audits, waste detection

## Permission Matrix
```
trump_president: [congress_senate, congress_house, state_dept, treasury, defense, commerce, energy, justice, doge_musk]
congress_senate: [trump_president, congress_house]
congress_house: [trump_president, congress_senate]
scotus: [trump_president, all_cabinet]
doge_musk: [trump_president, all_cabinet]
cabinet_members: [trump_president, doge_musk]
```

## State Machine
```
Pending -> Congress -> POTUS -> Cabinet -> Doing -> Review -> Done
            |           |         ^
            v           v         |
          SCOTUS <- DOGE Audit ---|
```

## Trump Style Keywords
- TREMENDOUS, HUGE, BEST, SAD, FAKE NEWS
- Believe me!, Many people are saying...
- Nobody has better X than us
- Make America Great Again #MAGA
- You're FIRED!

## Features
1. DOGE Daily Waste Report
2. "You're Fired" Termination System
3. Truth Social Notification Style
4. Tariff-based Resource Negotiation
5. C-SPAN Live Debate Channel
6. Loyalty Index Tracking
7. Border Wall Security Mode
