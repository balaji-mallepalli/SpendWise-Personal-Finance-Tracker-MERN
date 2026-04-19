# 🚀 SpendWise Deployment Guide

This guide provides step-by-step instructions for deploying SpendWise as a live web application using **Render** for the backend and **Vercel** for the frontend.

---

## 🏗️ Phase 1: Prepare Your Repository

1.  **Push your code to GitHub**: 
    - Ensure all changes (including the `Procfile` and `vercel.json`) are committed.
    - Create a new public or private repository on GitHub and push your local SpendWise folder.

---

## 🎨 Phase 2: Deploy Backend (Render)

1.  Log in to [Render](https://render.com/).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub repository and select the `backend` folder as the root (or leave root as `./` and set the build/start commands below).
4.  **Configuration**:
    - **Runtime**: `Python 3`
    - **Build Command**: `pip install -r requirements.txt`
    - **Start Command**: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app`
5.  **Environment Variables**:
    - `MONGODB_URL`: Your MongoDB Atlas connection string.
    - `SECRET_KEY`: A random long string for JWT security.
    - `ALLOWED_ORIGINS`: Set this to `*` initially, then change it to your Vercel URL once the frontend is live (e.g., `https://spend-wise-frontend.vercel.app`).

---

## ⚡ Phase 3: Deploy Frontend (Vercel)

1.  Log in to [Vercel](https://vercel.com/).
2.  Click **Add New...** -> **Project**.
3.  Connect your GitHub repository.
4.  **Configuration**:
    - **Framework Preset**: `Vite` (Should be auto-detected).
    - **Root Directory**: `frontend`
5.  **Environment Variables**:
    - `VITE_API_URL`: The URL of your **Render backend** (e.g., `https://spend-wise-api.onrender.com`).
6.  Click **Deploy**.

---

## 🔗 Phase 4: Final Connection

Once the Vercel deployment finishes and you have your live frontend URL:
1.  Go back to your **Render Web Service** dashboard.
2.  Update the `ALLOWED_ORIGINS` environment variable by replacing `*` with your actual Vercel URL (e.g., `https://your-app-name.vercel.app`).
3.  Wait for Render to redeploy the backend.

---

## 🆘 Troubleshooting: "Failed to Login" (CORS Errors)

If you see a "Failed to Login" error on your live Vercel site:
1.  **Check the Vercel URL**: Ensure your URL in Render's `ALLOWED_ORIGINS` **exactly** matches your Vercel URL (e.g., `https://your-app-name.vercel.app`) with **no trailing slash**.
2.  **Wildcard Conflict**: Avoid using `*` for `ALLOWED_ORIGINS` in production. FastAPI does not allow credentialed requests (logins) when the origin is a wildcard.
3.  **Variable Names**: Verify the key is `ALLOWED_ORIGINS` (plural) and matches the code.

**Congratulations! Your SpendWise app is now globally accessible!**
