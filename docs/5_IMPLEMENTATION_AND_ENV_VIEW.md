# 5. Implementation and Environment View Diagrams

This document illustrates the physical architecture of the application, including the source-code component wiring and the physical hardware/network deployment nodes.

## 5.1 Component Diagram
The Component Diagram details how the various modular parts of the software are wired together, specifically separating frontend UI modules from backend API modules.

```mermaid
classDiagram
    class Frontend {
        <<Component>>
        [Vite React Application]
    }
    class AuthContext {
        <<Component>>
        [JWT Storage & State]
    }
    class Pages {
        <<Component>>
        [Dashboard / Transactions / Budgets]
    }
    class API_Axios {
        <<Component>>
        [HTTP Interceptor]
    }
    
    class Backend_API {
        <<Component>>
        [FastAPI Uvicorn Server]
    }
    class Routers {
        <<Component>>
        [Endpoint Controllers]
    }
    class Services {
        <<Component>>
        [Business Logic]
    }
    class MotorDriver {
        <<Component>>
        [Async DB Connector]
    }

    Frontend *-- Pages
    Frontend *-- AuthContext
    Pages ..> API_Axios : uses
    AuthContext ..> API_Axios : injects token
    
    Backend_API *-- Routers
    Routers ..> Services : delegates logic
    Services ..> MotorDriver : calls
    
    API_Axios --> Backend_API : HTTPS/REST
```

## 5.2 Deployment Diagram
The Deployment Diagram represents the physical deployment layout, mapping software components to the hardware / cloud network environments they execute on.

```mermaid
flowchart TD
    subgraph Client [Client Device]
        direction TB
        Browser[Web Browser\nChrome/Safari/Edge]
    end

    subgraph CDN [Frontend Host : Vercel]
        direction TB
        StaticAssets[Compiled Static Files\nHTML/JS/CSS]
    end

    subgraph CloudApp [Backend Host : Render]
        direction TB
        API[FastAPI Server\nUvicorn / Python 3.11]
    end

    subgraph DBaaS [Database Host : MongoDB Atlas]
        direction TB
        Cluster[(MongoDB Cluster\nPrimary-Replica)]
    end

    Browser -- "HTTP GET (Port 443)\nLoads UI" --> StaticAssets
    Browser -- "HTTPS/REST (Port 443)\nAPI Requests" --> API
    API -- "MongoDB Wire Protocol\nTCP (Port 27017)" --> Cluster
```
