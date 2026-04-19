# 1. Functional Oriented Diagrams

This document contains the functional models for the SpendWise application, illustrating system data flows, modular hierarchy, and data definitions.

## 1.1 Data Flow Diagram (DFD) - Level 0 (Context Diagram)
The Context Diagram represents the entire SpendWise software system as a single process, showing its interactions with principal external entities (The User).

```mermaid
flowchart TD
    User([User])
    System((SpendWise\nSystem))
    
    User -- "User Credentials,\nTransaction Data,\nBudget Limits" --> System
    System -- "Dashboard Analytics,\nAlerts, Exported CSV" --> User
```

## 1.2 Data Flow Diagram (DFD) - Level 1
Level 1 breaks down the Context Diagram into the major sub-processes: Authentication, Transaction Processing, and Budget & Analytics.

```mermaid
flowchart TD
    User([User])
    
    P1((1. Auth\nProcess))
    P2((2. Transaction\nProcess))
    P3((3. Budget &\nAnalytics))
    
    DB_Users[(Users DB)]
    DB_Trans[(Transactions DB)]
    DB_Budgets[(Budgets DB)]
    
    User -- "Login/Register" --> P1
    P1 -- "Verify Auth" --> DB_Users
    DB_Users -- "Auth Token" --> P1
    P1 -- "Auth Token" --> User
    
    User -- "Income/Expense\nDetails" --> P2
    P2 -- "Store/Update" --> DB_Trans
    DB_Trans -- "Fetch Transactions" --> P2
    P2 -- "Transaction History" --> User
    
    User -- "Budget Targets" --> P3
    P3 -- "Save Target" --> DB_Budgets
    DB_Trans -- "Aggregate Data" --> P3
    DB_Budgets -- "Check Thresholds" --> P3
    P3 -- "Visual Charts & Alerts" --> User
```

## 1.3 Data Dictionary
A structured definition of the vital data elements traveling through the DFDs.

| Data Element | Description | Composition/Attributes |
| :--- | :--- | :--- |
| **UserCredentials** | Data required to authenticate a user. | `email` (String), `password` (String) |
| **UserProfile** | Data stored for an authenticated user. | `_id` (ObjectId), `name` (String), `email` (String), `hashed_password` (String) |
| **TransactionData** | Details of a financial log (income/expense). | `_id` (ObjectId), `user_id` (ObjectId), `amount` (Float), `type` (String: Income/Expense), `category` (String), `date` (DateTime), `description` (String) |
| **BudgetData** | Financial thresholds set by the user for a category. | `_id` (ObjectId), `user_id` (ObjectId), `category` (String), `limit_amount` (Float), `spent_amount` (Float), `month` (Integer), `year` (Integer) |
| **DashboardData** | Aggregated data returned to the user view. | `total_income` (Float), `total_expense` (Float), `net_balance` (Float), `pie_chart_data` (List), `line_chart_data` (List) |

## 1.4 Structured Chart
The Structured Chart focuses on the modular breakdown and control hierarchy of the application.

```mermaid
graph TD
    classDef main fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef module fill:#e1f5fe,stroke:#0288d1,stroke-width:1px;
    classDef leaf fill:#f1f8e9,stroke:#689f38,stroke-width:1px;
    
    Main((SpendWise\nMain System)):::main
    
    Auth[Authentication Module]:::module
    Trans[Transaction Module]:::module
    Budget[Budget & Analysis Module]:::module
    
    Main --- Auth
    Main --- Trans
    Main --- Budget
    
    Auth --- Login[Login Handler]:::leaf
    Auth --- Register[Register Handler]:::leaf
    Auth --- Token[Token Validator]:::leaf
    
    Trans --- AddTx[Add Transaction]:::leaf
    Trans --- EditTx[Edit Transaction]:::leaf
    Trans --- FetchTx[Get Transaction History]:::leaf
    
    Budget --- SetLimit[Set Budget Limit]:::leaf
    Budget --- CheckAlert[Check Alert Trigger]:::leaf
    Budget --- GenDash[Generate Dashboard Stats]:::leaf
```
