# 4. Revised Risk Formula

```
Current:  Risk = 0.45×Behavioral + 0.30×Device + 0.25×Context

Improved: Risk = 0.40×Behavioral + 0.25×Device + 0.20×Context + 0.15×FailedLoginBehavior
```
During enrollment phase (no ML):
```
Risk = 0.70×Device + 0.30×Context  (rule-based fallback)
```\n