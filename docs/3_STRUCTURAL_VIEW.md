# 3. Structural View Diagrams

This document illustrates the static architectures and static relationships defined within the SpendWise application.

## 3.1 Class Diagram
The Class Diagram isolates the Backend Models (Pydantic objects) and exactly how they associate with each other in memory and the DB.

```mermaid
classDiagram
    class User {
        +ObjectId id
        +String name
        +String email
        +String hashed_password
        +register_user()
        +login_user()
    }
    
    class Transaction {
        +ObjectId id
        +ObjectId user_id
        +Float amount
        +String type "Income|Expense"
        +String category
        +Date date
        +String description
        +add_transaction()
        +delete_transaction()
    }
    
    class Budget {
        +ObjectId id
        +ObjectId user_id
        +String category
        +Float limit_amount
        +Float spent_amount
        +Integer month
        +Integer year
        +check_threshold()
        +update_spent()
    }
    
    class Category {
        +String name
        +String type
        +String icon
        +String color
    }
    
    User "1" -- "*" Transaction : logs
    User "1" -- "*" Budget : establishes
    Transaction "*" -- "1" Category : classified_by
    Budget "1" -- "1" Category : tracks
```

## 3.2 Object Diagram
This diagram reveals a runtime snapshot showing instantiated instances of the classes above representing a single user session state.

```mermaid
classDiagram
    %% Object Diagram simulated via Class diagram schema defining actual instances
    class UserInstance {
        <<Object>>
        id = "U_0912A"
        name = "John Doe"
        email = "john@example.com"
    }
    
    class TransactionInstance1 {
        <<Object>>
        id = "T_991"
        amount = 15.00
        type = "Expense"
        category = "Food"
    }
    
    class TransactionInstance2 {
        <<Object>>
        id = "T_992"
        amount = 2000.00
        type = "Income"
        category = "Salary"
    }
    
    class BudgetInstance {
        <<Object>>
        id = "B_55"
        category = "Food"
        limit_amount = 300.00
        spent_amount = 15.00
    }
    
    UserInstance --> TransactionInstance1 : owns
    UserInstance --> TransactionInstance2 : owns
    UserInstance --> BudgetInstance : owns
```

## 3.3 Package Diagram
The Package diagram defines the file-directory level architecture dividing logically coupled components in the repository.

```mermaid
graph TD
    subgraph SpendWise System
        direction TB
        
        subgraph Frontend Package [React / Vite]
            FC[Components]
            FP[Pages]
            FCtx[Context]
            FS[Services / API]
            
            FP -.uses.-> FC
            FP -.uses.-> FCtx
            FCtx -.calls.-> FS
        end
        
        subgraph Backend Package [FastAPI]
            BR[Routers]
            BS[Services]
            BM[Models]
            BDB[Database Connector]
            
            BR -.uses.-> BS
            BS -.uses.-> BM
            BS -.uses.-> BDB
        end
        
        subgraph Database Package [MongoDB]
            Collections[(NoSQL Collections)]
        end
        
        FS == "HTTP JSON" ==> BR
        BDB == "Motor Async" ==> Collections
    end
```
