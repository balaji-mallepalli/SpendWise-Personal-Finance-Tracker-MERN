# 4. Behavioral View Diagrams

This document highlights the dynamic behavior of the SpendWise system—showing how messages are passed chronologically, how statuses shift, and the logical flow of actions.

## 4.1 Sequence Diagram
Maps out the exact chronological series of requests and responses when a user logs a new expense.

```mermaid
sequenceDiagram
    actor User
    participant React_UI
    participant AuthContext
    participant FastAPI_Router
    participant Database

    User->>React_UI: Fills "New Expense" Form
    React_UI->>AuthContext: Request Current Token
    AuthContext-->>React_UI: Returns JWT
    React_UI->>+FastAPI_Router: POST /transactions (Payload + JWT)
    FastAPI_Router->>FastAPI_Router: Validate JWT
    FastAPI_Router->>+Database: Insert Transaction Document
    Database-->>-FastAPI_Router: Acknowledge (InsertComplete)
    FastAPI_Router-->>-React_UI: 201 Created (Transaction Object)
    React_UI->>React_UI: Update Dashboard State
    React_UI-->>User: Visual Success Alert / Renders new chart
```

## 4.2 Collaboration Diagram (Communication Diagram)
Displays object interactions arranged around the objects and their links to each other rather than a strict chronological timeline.

```mermaid
flowchart TD
    UI[Frontend Client : ReactApp]
    BS[Backend Service : TransactionRouter]
    Auth[Security : AuthService]
    DB[Storage : MongoCluster]
    
    UI -- "1. Send Transaction Payload" --> BS
    BS -- "2. Check Token Validity" --> Auth
    Auth -- "3. Token Valid" --> BS
    BS -- "4. Save Payload" --> DB
    DB -- "5. Return ID" --> BS
    BS -- "6. Return 200 OK" --> UI
```

## 4.3 State-chart Diagram
Maps the complete lifecycle of a `Budget` entity within a user's account over a single month.

```mermaid
stateDiagram-v2
    [*] --> Active : Budget Created
    
    state Active {
        [*] --> Secure
        Secure --> NearingLimit : Total Spent > 80%
        NearingLimit --> Secure : Transaction Deleted
    }
    
    Active --> Exceeded : Total Spent > 100%
    Exceeded --> NearingLimit : Transaction Deleted
    Exceeded --> Exceeded : Add More Expenses
    
    Active --> Reset : End of Month
    Exceeded --> Reset : End of Month
    Reset --> [*]
```

## 4.4 Activity Diagram
Shows the procedural workflow a user goes through when attempting to access secure data.

```mermaid
flowchart TD
    Start((Start)) --> AttemptLogin[User Enters Credentials]
    AttemptLogin --> API[Send to Auth Endpoint]
    API --> Check{Credentials Valid?}
    
    Check -->|No| Fail[Return 401 Error]
    Fail --> RenderError[Render Error Message on UI]
    RenderError --> End((End))
    
    Check -->|Yes| Success[Generate JWT Token]
    Success --> ReturnToken[Send Token via Response]
    ReturnToken --> Context[Save Token to LocalStorage/State]
    Context --> Route[Navigate to Protected Dashboard]
    Route --> Fetch[Fetch Dashboard Data]
    Fetch --> End((End))
```
