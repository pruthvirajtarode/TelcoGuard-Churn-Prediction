# 📊 TelcoGuard Diagrams — Ready for Word/PowerPoint

## ✅ All Diagrams Generated Successfully

All diagrams are available in **two formats** in the `diagrams/` folder:

### **1. PNG Files** (for copy/paste into Word/PowerPoint)
- `diagrams/system_architecture.png` (20.5 KB)
- `diagrams/class_diagram.png` (25.9 KB)
- `diagrams/use_case_diagram.png` (25.8 KB) ✨ **with stick actors**
- `diagrams/sequence_diagram.png` (17.2 KB)
- `diagrams/dataflow_diagram.png` (15.5 KB)
- `diagrams/deployment_diagram.png` (11 KB)

### **2. JPG Files** (for better compression in Word)
- `diagrams/system_architecture.jpg` (64.2 KB)
- `diagrams/class_diagram.jpg` (72.2 KB)
- `diagrams/use_case_diagram.jpg` (50.5 KB) ✨ **with stick actors**
- `diagrams/sequence_diagram.jpg` (60.3 KB)
- `diagrams/dataflow_diagram.jpg` (53.3 KB)
- `diagrams/deployment_diagram.jpg` (43.7 KB)

---

## 📋 Diagram Descriptions

### **1. System Architecture**
Shows the complete TelcoGuard system with:
- Streamlit UI (Frontend)
- FastAPI Model API + GenAI Service
- PostgreSQL OLTP DB, Analytics Warehouse, Blob Storage
- Azure ML Workspace, Model Registry, CI/CD pipeline

### **2. Class Diagram**
Shows core classes and relationships:
- `StreamlitApp` (UI layer)
- `FeatureEngineering` (preprocessing)
- `Trainer` (ML training)
- `GenAIService` (AI/LLM integration)
- `AzureMLOps` (cloud deployment)

### **3. Use Case Diagram** ✨
Shows user interactions with **stick-figure actors**:
- **Client**: View Dashboard, Run Prediction, Batch Predictions
- **Data Engineer**: Train Model, Manage Deployments
- **Data Scientist**: View Model Metrics, Train Model

### **4. Sequence Diagram**
Shows prediction flow step-by-step:
1. User submits customer data in Streamlit UI
2. UI calls FastAPI /predict endpoint
3. API loads model from registry
4. Model makes prediction
5. GenAI Service generates explanation
6. Results returned with confidence score

### **5. Data Flow Diagram**
Shows data pipeline:
- Source Systems → Raw Storage
- Raw Storage → Processed Storage (ETL)
- Processed Storage → Analytics Warehouse
- Warehouse → Model Training
- Training → Model Registry
- Registry → Serving → Dashboard

### **6. Deployment Diagram**
Shows production deployment:
- Client Browser → Streamlit Host (HTTP)
- Streamlit → API Host (AKS/ACI, HTTPS)
- API → Azure ML (model inference)
- API → PostgreSQL (read/write)
- API → Blob Storage (knowledge base)

---

## 🎯 How to Use

### **Copy to Word:**
1. Open `diagrams/` folder in Windows Explorer
2. Right-click any PNG or JPG
3. Select "Copy"
4. Paste into Word document (Ctrl+V)

### **Recommended:**
- Use **PNG** for sharp diagrams (lossless)
- Use **JPG** for smaller file sizes (lossy, good for email)

---

## ✅ Quality Verified

- ✅ All PNG files: Valid (1200×800 pixels, RGB color)
- ✅ All JPG files: Valid (1200×800 pixels, RGB color)
- ✅ Use case diagram: **Includes stick-figure actors** (Client, Data Engineer, Data Scientist)
- ✅ All diagrams: Properly styled, readable, professional
- ✅ Ready for client delivery

---

## 🛠️ Source Files

If you need to edit the diagrams:
- `.puml` files: PlantUML source (edit here to modify)
- `.svg` files: SVG vector format (can edit with Inkscape or import to Word)

To regenerate PNGs/JPGs after editing `.puml` files, run:
```bash
python scripts/render_diagrams.py
```

---

**All diagrams are ready for your Word document! 🎉**
