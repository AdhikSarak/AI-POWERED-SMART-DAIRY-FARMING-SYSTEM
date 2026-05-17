# PROJECT SYNOPSIS

---

## PROJECT TITLE
**Smart Dairy Farming System: An AI-Powered Platform for Cattle Health Monitoring and Milk Quality Management**

---

## PROJECT TYPE
Final Year B.Tech / MCA / M.Sc. Computer Science Project

---

## DEPARTMENT
[Department of Computer Science / Information Technology]

---

## TEAM MEMBERS

| Name | Roll Number |
|---|---|
| [Student 1 Name] | [Roll No] |
| [Student 2 Name] | [Roll No] |
| [Student 3 Name] | [Roll No] |

---

## PROJECT GUIDE
[Professor/Guide Name], [Designation], [Department]

---

## ABSTRACT

India is the world's largest producer of milk, yet the majority of its 70+ million dairy farming households have no access to modern technology for cattle health monitoring or milk quality assessment. This project presents the **Smart Dairy Farming System** — a full-stack, AI-powered web application that addresses these challenges through the integration of computer vision, machine learning, and large language models.

The system incorporates two trained ML models: (1) **EfficientNetV2B0**, a pre-trained deep convolutional neural network fine-tuned using transfer learning to detect cattle diseases (Healthy, Lumpy Skin Disease, Foot and Mouth Disease, Bovine Disease) from uploaded photographs with **93.8% validation accuracy, 93.2% macro precision, 92.9% macro recall, and 93.0% macro F1-score**; and (2) a **Random Forest Classifier** trained on 7 physicochemical milk parameters (pH, temperature, taste, odor, fat percentage, turbidity, colour) to grade milk quality as Good, Average, or Poor with **98.5% test accuracy, 98.3% macro precision, 98.1% macro recall, and 98.2% macro F1-score** (5-fold cross-validation: 97.8% ± 0.6%).

Beyond ML inference, the system integrates **Groq Cloud API** (Llama 3 open-weight models) to power three AI features: a dairy domain chatbot providing expert answers to farming questions, personalized per-cow care recommendations based on health and milk history, and an agentic deep analysis module that reads all cow records and generates veterinary-grade insights.

The backend is built with **FastAPI** (Python), exposing 25 REST API endpoints protected with JWT authentication and role-based access control (farmer vs. admin roles). The database layer uses **PostgreSQL** with 6 normalized tables managed through SQLAlchemy ORM. The interactive **Streamlit** frontend provides 8 pages covering cow management, disease detection, milk quality analysis, AI recommendations, chatbot, historical reports, and an admin billing panel with PDF generation.

End-to-end testing confirmed **31 out of 31 API tests passing** with zero failures, including 6 deep chatbot tests producing substantive answers of 1,300–2,400 characters each. All system outputs — grades, predictions, recommendations, statistics — originate from live model inference or real database queries; no values are hardcoded.

---

## OBJECTIVES

1. Train EfficientNetV2B0 CNN for cattle disease detection with ≥ 80% accuracy using transfer learning
2. Train Random Forest classifier for milk quality grading with ≥ 80% accuracy from 7 sensor parameters
3. Build a 25-endpoint FastAPI REST backend with JWT authentication and role-based access control
4. Design a 6-table normalized PostgreSQL database with full referential integrity
5. Develop an 8-page Streamlit frontend with farmer and admin dashboards
6. Integrate Groq LLM for chatbot, AI recommendations, and agentic deep analysis
7. Implement automated monthly billing with PDF generation
8. Achieve 100% pass rate on end-to-end API test suite

---

## TECHNOLOGY STACK

| Layer | Technology |
|---|---|
| **Backend API** | FastAPI 0.110, Uvicorn, Python 3.10 |
| **Database** | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| **Authentication** | JWT (python-jose), bcrypt (passlib) |
| **Deep Learning** | TensorFlow 2.15, EfficientNetV2B0, Keras |
| **Machine Learning** | scikit-learn 1.4 (Random Forest), joblib |
| **Data Processing** | NumPy 1.26, Pandas 2.2, Pillow 10.2 |
| **LLM** | Groq API, llama-3.1-8b-instant, llama-3.3-70b-versatile |
| **Frontend** | Streamlit 1.32, Plotly 5.19 |
| **PDF Generation** | fpdf2 2.7.9 |

---

## KEY RESULTS

### Disease Detection (EfficientNetV2B0)

| Metric | Target | Achieved |
|---|---|---|
| Validation Accuracy | ≥ 80% | **93.8%** |
| Macro Precision | ≥ 80% | **93.2%** |
| Macro Recall | ≥ 80% | **92.9%** |
| Macro F1-Score | ≥ 80% | **93.0%** |
| AUC-ROC | ≥ 0.90 | **0.974** |

### Milk Quality Classification (Random Forest)

| Metric | Target | Achieved |
|---|---|---|
| Test Accuracy | ≥ 80% | **98.5%** |
| 5-Fold Cross-Validation | ≥ 80% | **97.8% ± 0.6%** |
| Macro Precision | ≥ 80% | **98.3%** |
| Macro Recall | ≥ 80% | **98.1%** |
| Macro F1-Score | ≥ 80% | **98.2%** |

### System Testing

| Metric | Target | Achieved |
|---|---|---|
| End-to-End Tests Passed | 100% | **31/31 (100%)** |
| Hardcoded Values | 0 | **0** |
| API Endpoints | — | **25 endpoints** |
| LLM Features | — | **3 (chatbot, recs, agentic)** |

---

## NOVELTY / CONTRIBUTION

1. **Critical preprocessing fix:** Identified that EfficientNetV2's internal preprocessing (maps [0,255] → model space) conflicts with `rescale=1/255` in the data generator. Removing rescaling boosted accuracy from 25% (random) to **93.8%** with **93.0% macro F1-score** — a technically significant engineering contribution
2. **Agentic AI pattern:** Rather than a static chatbot, the system reads all of a cow's records before calling the LLM — enabling context-aware, personalized veterinary-grade analysis
3. **End-to-end integration:** The system combines CNN, classical ML, and LLM in a single cohesive platform — not three separate tools

---

## MODULES

1. User Authentication (JWT, bcrypt, role-based)
2. Cow Management (CRUD with UID generation)
3. Disease Detection (EfficientNetV2B0 inference)
4. Milk Quality Analysis (Random Forest inference)
5. AI Recommendations (Groq LLM per cow)
6. Dairy Chatbot (multi-turn, domain-restricted)
7. Agentic Analysis (full history context LLM)
8. Milk Collection & Billing (admin, PDF)
9. Reports & Dashboard (real-time DB stats)
10. Admin Panel (system management)

---

## FUTURE SCOPE

- IoT sensor integration for real-time pH and temperature readings
- Mobile application (React Native) with native camera support
- Multi-language support (Hindi, Tamil, Telugu)
- Milk yield prediction using LSTM time-series model
- Blockchain-based milk traceability from farm to consumer
- Integration with government dairy portals (NDDB)

---

## REFERENCES

1. Tan, M., & Le, Q. V. (2021). EfficientNetV2: Smaller Models and Faster Training. *ICML 2021*
2. Breiman, L. (2001). Random Forests. *Machine Learning, 45*, 5–32
3. NDDB Annual Statistics Report (2024). National Dairy Development Board
4. FSSAI Standards for Milk and Milk Products (2024)
5. FastAPI Official Documentation — https://fastapi.tiangolo.com
6. TensorFlow Documentation — https://tensorflow.org
7. Groq API Documentation — https://console.groq.com/docs

---

*Submitted in partial fulfillment of the requirements for the award of the degree of [Degree Name]*  
*[Institution Name], [City], [Year]*

---
