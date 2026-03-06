# AI Employee — Quick Start Commands

## Vault Path
```
VAULT = F:/AI_Employee_Vault/AI_Employee_Vault - Copy
TOKEN = F:/AI_Employee_Vault/AI_Employee_Private/tokens/token.json
```

---

## Gmail Setup — Pehli baar token banao
```bash
# Step 1: is folder mein jao
cd watchers_gmail

# Step 2: auth script chalao (browser khulega)
python gmail_auth.py

# Step 3: token.json ban jayega — ek baar hi karna hai
```
> Zaruri: pehle `client_secret.json` Google Cloud Console se download kar ke
> `watchers_gmail/` folder mein rakh do

---

## Gmail Watcher — Start karo
```bash
# Normal start (continuous, har 60 sec check)
python watchers_gmail/gmail_watcher.py "F:/AI_Employee_Vault/AI_Employee_Vault - Copy" "F:/AI_Employee_Vault/AI_Employee_Vault - Copy/watchers_gmail/token.json"
```

---

## Filesystem Watcher — Start karo
```bash
# File drop monitor karta hai vault root mein
python watchers/filesystem_watcher.py "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
```

---

## WhatsApp Watcher — Start karo
```bash
python watchers_whatsapp/whatsapp_watcher.py "F:/AI_Employee_Vault/AI_Employee_Vault - Copy"
```

---

## Orchestrator — Start karo
```bash
# Needs_Action process karta hai, approvals check karta hai
python System/orchestrator.py
```

---

## PM2 — Sab ek saath start karo (Recommended)
```bash
# Pehli baar
pm2 start Setup/ecosystem.config.js

# Status dekho
pm2 status

# Logs dekho
pm2 logs

# Restart karo
pm2 restart all

# Band karo
pm2 stop all

# Reboot ke baad bhi auto-start
pm2 save
pm2 startup
```

---

## VaultOS Dashboard — Start karo
```bash
cd vaultos
npm run dev
# Open: http://localhost:3000
```

---

## Folder Flow (Yaad rakhne ke liye)
```
Email aaya     → /Needs_Action/Email/
File drop ki   → /Needs_Action/Files/
WhatsApp msg   → /Needs_Action/WhatsApp/

Approval chahiye → /Pending_Approval/
Approve kiya     → /Approved/
Reject kiya      → /Rejected/
Kaam ho gaya     → /Done/
```
