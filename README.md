# FarmConnect - Agricultural Marketplace System

## Project Overview

FarmConnect (Farmso) is a comprehensive full-stack web application designed to bridge the gap between farmers and customers. It provides three distinct modules:

* **Customer Portal** – Allows customers to browse fresh produce, view farmer shop profiles, add products to a real-time shopping cart, and place orders seamlessly.
* **Farmer Portal** – Empowers farmers to manage their own digital storefronts (shops), upload and manage inventory, track analytics through a dashboard, and process incoming orders.
* **Admin Portal** – Provides system administrators with a bird's-eye view of platform analytics, user demographics, and the ability to moderate the platform by activating/deactivating specific users, shops, and products.

The application is built for high performance using **React.js (Vite)** for the frontend and **Python FastAPI** for the backend, with a highly scalable **PostgreSQL (Neon)** relational database.

---

## Technology Stack

### Frontend (React/Vite)
* **Framework:** React.js initialized via Vite
* **Routing:** React Router v6
* **Styling:** Tailwind CSS (Utility-first CSS)
* **Icons & UI:** Lucide React
* **Data Visualization:** Recharts
* **State Management:** React Context API (AuthContext, CartContext)
* **HTTP Client:** Axios
* **Deployment Readiness:** Vercel configured (`vercel.json` included)

### Backend (FastAPI)
* **Framework:** Python FastAPI
* **Database ORM:** SQLAlchemy
* **Data Validation:** Pydantic
* **Migrations:** Alembic
* **Authentication:** JWT (JSON Web Tokens) with Passlib & bcrypt
* **Server:** Uvicorn
* **Deployment Readiness:** Vercel Serverless configured (`vercel.json` included)

### Database
* **Database Engine:** PostgreSQL (Managed via Neon / AWS)

---

## Project Structure

```text
farmso/
│
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database Migrations
│   ├── app/
│   │   ├── api/              # Route Handlers (auth, admin, customer, farmer)
│   │   ├── core/             # Security and Config settings
│   │   ├── models/           # SQLAlchemy Database Models
│   │   └── schemas/          # Pydantic Validation Schemas
│   ├── requirements.txt      # Python Dependencies
│   └── vercel.json           # Vercel Deployment Config
│
├── frontend/                 # Vite React Application
│   ├── src/
│   │   ├── api/              # Axios instance configuration
│   │   ├── components/       # Reusable UI (Layouts, Modals)
│   │   ├── context/          # Global State (Auth, Cart)
│   │   ├── pages/            # Page Views (Admin, Customer, Farmer, Auth)
│   │   └── routes/           # AppRoutes configuration
│   ├── package.json          # Node Dependencies
│   ├── tailwind.config.js    # Tailwind Config
│   └── vercel.json           # Vercel SPA Routing Config
│
└── README.md
```

---

# Backend Setup

## 1. Navigate to Backend

```bash
cd backend
```

## 2. Create a Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS
```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@hostname/dbname?sslmode=require

# Security
SECRET_KEY=your-secure-jwt-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 5. Run Database Migrations

Ensure your database is up-to-date with the latest schema by running Alembic:

```bash
alembic upgrade head
```

## 6. Running the Backend

From the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`.
FastAPI automatically provides interactive API documentation at `http://localhost:8000/docs`.

---

# Frontend Setup

## 1. Navigate to Frontend

Open a new terminal and navigate to the frontend:

```bash
cd frontend
```

## 2. Install Dependencies

```bash
npm install
```

## 3. Configure API Endpoint

Ensure `frontend/src/api/axios.js` points to your active backend (either localhost or your deployed Vercel URL).

## 4. Start Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite specifies).

---

# Application Modules

## Admin Portal (`/admin`)
* **Analytics Dashboard:** View Total Revenue, Orders, and User Demographics via Recharts.
* **User Management:** View all users and activate/deactivate accounts. Deactivating a farmer automatically hides their shop from customers.
* **Product Moderation:** View all products across the platform and deactivate specific rule-breaking items.

## Farmer Portal (`/farmer`)
* **Analytics Dashboard:** Track personal shop revenue and order volume.
* **Shop Management:** Manage shop profile details (Name, Address, Image).
* **Inventory Management:** Add, edit, and restock products.
* **Order Processing:** View incoming orders and fulfill them.

## Customer Portal (`/customer`)
* **Marketplace:** Browse shops and search for products by category or name.
* **Shopping Cart:** Add items to a real-time cart, tracked persistently.
* **Checkout & Orders:** Place orders and view historical order data.
* **Profile:** Manage delivery address and contact information.

---

# Deployment (Vercel)

Both the frontend and backend are pre-configured for deployment on **Vercel**.

1. **Frontend:** Point a Vercel project to the `frontend/` directory. Vercel will automatically detect Vite and use `frontend/vercel.json` for React Router SPA rewrites.
2. **Backend:** Point a separate Vercel project to the `backend/` directory. The `backend/vercel.json` maps serverless requests directly to the FastAPI instance (`app.main:app`). Don't forget to add your `.env` variables to the Vercel dashboard!

---

# Author
Developed as a comprehensive, modern, scalable Agricultural Marketplace.
