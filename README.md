# WiFi Retail MVP – Phase 1

## Overview

This is Phase 1 of a 3-phase full-stack project. The goal of this phase is to build a WiFi retail platform where customers can purchase internet access (hourly, weekly, monthly) and pay using M-Pesa. 

The platform will be web-based and built with Django. The backend is designed to support advanced admin features for managing access, payments, and customer control.

---

## 🔧 Tech Stack

- **Backend**: Python, Django, Django Rest Framework
- **Frontend**:
- **Database**: PostgreSQL
- **Async Tasks**: Celery + Redis
- **Payments**: M-Pesa

---

## 🧱 Core Components

### Customer Features:
- View and choose WiFi packages (hourly, weekly, monthly)
- Make payment via M-Pesa STK Push
- Access WiFi automatically after successful payment
- Use voucher codes for free or discounted access

### Admin Features:
- Track active users and their access duration
- Modify access duration (e.g. upgrade from weekly to fortnightly)
- Update payment details and package pricing
- Create and manage custom packages (e.g. 5 hours, 3 hours)
- Issue promotional voucher codes
- Control the number of devices per payment
- Throttle WiFi speed per user/session

---
## Developers
### 📜 Generate AUTHORS File

Run the following script to auto-populate or update the `AUTHORS` file

```bash
bash scripts/generate-authors.sh

📘 See [SETUP.md](./SETUP.md) for full environment configuration instructions.
