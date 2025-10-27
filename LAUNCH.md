# 🚀 HOW TO LAUNCH BANTA DASHBOARD

## **Quick Start (2 Steps)**

### **Step 1: Setup Environment**
Create a `.env` file in the root directory:
```env
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here  
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

### **Step 2: Launch**
```bash
cd src
python start_server.py
```

**That's it!** 🎉

---

## **📁 Clean File Structure**

```
src/
├── start_server.py    ← 🚀 RUN THIS FILE
├── main.py           ← FastAPI app (don't run directly)
├── config.py         ← Settings
├── requirements.txt  ← Dependencies
├── services/         ← S3 service
└── utils/           ← Validators
```

---

## **🌐 Access Your Dashboard**

Once running:
- **🎨 Frontend:** http://localhost:3000 (if frontend is running)
- **⚙️ Backend API:** http://localhost:8000
- **📚 API Docs:** http://localhost:8000/docs

---

## **🔧 Troubleshooting**

**Problem:** Dependencies missing
**Solution:** 
```bash
cd src
pip install -r requirements.txt
python start_server.py
```

**Problem:** Port already in use
**Solution:** The script will tell you and suggest alternatives

**Problem:** AWS credentials error
**Solution:** Check your `.env` file has correct AWS keys

---

**Always use `start_server.py` - it handles everything!** ✨
