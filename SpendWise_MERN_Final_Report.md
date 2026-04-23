# SpendWise: Personal Finance Tracker
### A Full-Stack MERN Application with JWT Authentication
**Final Project Report**

---

## 1. Abstract
SpendWise is a comprehensive personal finance management tool designed to empower users with real-time insights into their spending habits. The application has been migrated from a Python/FastAPI backend to a robust **MERN Stack** (MongoDB, Express.js, React, Node.js). This report details the architecture, design decisions, and implementation of the system, highlighting the use of Mongoose for data modeling and JWT for secure session management.

## 2. Introduction
In an era of digital transactions, tracking personal expenses is crucial for financial health. SpendWise provides a centralized "Command Center" for users to manage multiple accounts, track categories, and set budgets. The migration to MERN ensures a unified JavaScript environment, improving development efficiency and application performance.

## 3. Project Objectives
- **Secure Authentication**: Implement robust user registration and login using JWT and Bcrypt.
- **Financial Tracking**: Enable CRUD operations for transactions across multiple accounts.
- **Budgeting**: Provide real-time monitoring of category-specific spending limits.
- **Data Visualization**: Offer interactive charts (Pie, Line) for spending analysis.
- **MVC Architecture**: Ensure a clean separation of concerns for maintainability.

## 4. System Requirements
### 4.1 Hardware Requirements
- Processor: Dual Core 2.0GHz or higher
- RAM: 8GB minimum
- Storage: 100MB for application files

### 4.2 Software Requirements
- Operating System: Windows/Linux/macOS
- Runtime: Node.js v18+
- Database: MongoDB Atlas (Cloud)
- Frontend: React 19 (Vite)
- IDE: Visual Studio Code

## 5. Technology Stack (MERN)
### 5.1 Frontend (React)
- **Framework**: Vite/React for fast development and HMR.
- **Styling**: Tailwind CSS v4 for a modern monochrome design.
- **Charts**: Recharts for dynamic data visualization.

### 5.2 Backend (Node.js & Express)
- **Server**: Express.js for RESTful API routing.
- **ODM**: Mongoose for structured MongoDB interaction.
- **Auth**: `jsonwebtoken` for stateless authentication.
- **Security**: `bcryptjs` for industry-standard password hashing.

### 5.3 Database (MongoDB)
- **Type**: NoSQL Document Store.
- **Cloud**: MongoDB Atlas for global scalability and high availability.

## 6. System Architecture
The application follows a standard **Tiered Architecture**:
1. **Client Tier**: React SPA handling UI and State.
2. **Application Tier**: Node.js/Express handling business logic and API routes.
3. **Data Tier**: MongoDB Atlas storing JSON-like documents.

### 6.1 MVC Pattern (Backend)
- **Model**: Mongoose schemas in `models/` directory.
- **View**: JSON responses returned to the React frontend.
- **Controller**: Business logic in `controllers/` directory.

## 7. Database Design (ER-Diagram)
The system manages 6 primary collections:
1. **Users**: Credentials and profile info.
2. **Accounts**: Name, type, and balance tracking.
3. **Categories**: Icons and colors for transaction grouping.
4. **Transactions**: Linked to User, Account, and Category.
5. **Budgets**: Monthly limits for specific categories.
6. **Alerts**: Notifications when budgets are 90%+ exceeded.

## 8. Implementation Details
### 8.1 Authentication Flow
1. User submits credentials.
2. Backend verifies hash using `bcrypt.compare()`.
3. A JWT is signed and returned to the client.
4. Client stores JWT and includes it in the `Authorization` header for subsequent requests.

### 8.2 Transaction Lifecycle
- **Create**: Updates the associated account balance and checks for budget alerts.
- **Update**: Recalculates balance differences and updates the ledger.
- **Delete**: Reverses the balance change before removing the record.

## 9. Features & UI/UX
- **Monochrome Glassmorphism**: A sleek, premium design aesthetic.
- **Theme Support**: Dark and Light modes with persistent state.
- **Responsive Layout**: Mobile-first design for all devices.
- **CSV Export**: Ability to download financial data for offline analysis.

## 10. Verification & Testing
- **API Testing**: Verified using Postman.
- **Frontend Testing**: Component testing using Vitest.
- **E2E Testing**: Manual walkthrough of all user flows (Register -> Account -> Transaction -> Dashboard).

## 11. Challenges & Solutions
- **Migration**: Maintaining hash compatibility was achieved by using standard Bcrypt parameters.
- **Real-time Aggregation**: Solved using Mongoose Aggregation Pipelines for dashboard totals.

## 12. Conclusion
SpendWise demonstrates the power of the MERN stack in building production-ready financial tools. The migration from Python to Node.js has resulted in a more cohesive codebase and a more professional architecture.

## 13. Future Enhancements
- Role-based access control (RBAC).
- Direct bank API integration.
- AI-powered spending predictions.

---
**Prepared By:** [Your Name]
**Project ID:** SpendWise-MERN-2026
