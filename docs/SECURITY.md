# Security Audit & Hardening Guide

This document outlines the security posture of the **DC Shows** application, identifies potential vulnerabilities, and provides a roadmap for hardening the system against common web attacks.

## 🛡️ Security Overview

The application implements several baseline security features:
*   **Password Hashing:** Uses `bcryptjs` with a salt factor of 10.
*   **Stateless Auth:** Uses JWT (JSON Web Tokens).
*   **Secure Cookies:** JWTs are stored in `HttpOnly` cookies to prevent XSS-based token theft.
*   **Parameterized Queries:** Prevents SQL Injection by using `pg`'s built-in parameterization.

---

## 🛡️ Security Posture

The following security measures have been implemented and verified:

*   **CSRF Protection (Double Submit Cookie)**: All state-changing API routes require a valid `X-CSRF-Token` header that matches the `csrfToken` cookie.
*   **Rate Limiting**: Authentication endpoints (`/api/auth/login`, `/api/auth/register`) are limited to 10 requests per 15-minute window to prevent brute-force attacks.
*   **Hardened JWT & Cookies**:
    *   JWT expiration shortened to **1 hour**.
    *   `HttpOnly` and `SameSite=Lax` flags enabled for session tokens.
    *   `Secure` flag enabled for production environments.
*   **XSS Protection**:
    *   Strict use of `escHtml` for all dynamic data rendering.
    *   Removed inline event handlers (`onclick`) in favor of secure event delegation.
*   **Global Error Handler**: Centralized middleware to log errors internally while returning sanitized, generic responses to clients to prevent system leakage.
*   **SQL Injection Protection**: Parameterized queries used for all database interactions.
*   **Environment Security**: All sensitive secrets are externalized and excluded from source control via `.gitignore`.

---

## 🚨 Remaining Risks

### 1. Transport Security (MITM)
While the application is hardened internally, it currently serves over HTTP. In production, passwords and tokens are still vulnerable to interception.

**Recommendation:** Deploy behind a reverse proxy (Nginx/Caddy) with **HTTPS (TLS/SSL)** and enable HSTS.

---

## ⚠️ Medium-Risk Findings

### 1. Missing Security Headers
The application could benefit from standard security headers (e.g., `CSP`, `X-Frame-Options`).
*   **Recommendation:** Install and configure the `helmet` middleware.

---

## ⚙️ Hardened Roadmap (Status)

| Task | Status | Priority | Description |
| :--- | :--- | :--- | :--- |
| **CSRF Protection** | ✅ Done | High | Double Submit Cookie pattern implemented. |
| **Rate Limiting** | ✅ Done | High | 10 requests / 15 mins on auth routes. |
| **JWT Hardening** | ✅ Done | High | Short expiry + Secure/SameSite flags. |
| **XSS Hardening** | ✅ Done | High | Removed inline JS and added robust escaping. |
| **Install Helmet** | ⏳ Pending | Medium | Set security headers. |
| **Enable HTTPS** | ⏳ Pending | High | Required for production deployment. |

## 🧪 Security Testing
To verify these improvements, use tools like:
*   `npm audit`: Check for vulnerable dependencies.
*   `OWASP ZAP`: Automated vulnerability scanning.
*   `Burp Suite`: Manual interception and testing of API endpoints.
