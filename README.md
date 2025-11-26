# 🎬 Movie Recommendation System  
# Machine Learning–Based Content Recommendation (2024–2025)

<img width="650" alt="banner" src="https://github.com/user-attachments/assets/placeholder-movie" />

## 📌 Overview

This project focuses on building a **machine learning–based movie recommendation engine** using data collected from multiple sources, including IMDb, Rotten Tomatoes, and TMDB.  
The system provides **personalized movie suggestions**, detailed movie information, and an **interactive UI** that enhances user experience.

The project consists of four main components:

1. **Web Scraping (IMDb & Rotten Tomatoes)**
2. **Data Collection via TMDB API**
3. **Content-Based Recommendation Engine**
4. **User Interface (Movie Browser + Chatbot Page)**

---

## 🛠️ Tech Stack

### **Languages & Libraries**
- **Python 3.10+**
- **Scrapy / Custom Spider** – used for scraping IMDb & Rotten Tomatoes  
- **TMDB API** – used for structured movie metadata  
- **pandas, numpy** – data processing  
- **scikit-learn** – machine learning & similarity modeling  
- **NLTK / spaCy** – text normalization & metadata cleaning  
- **Flask / FastAPI** (optional) – backend API for recommendations  

### **Frontend & UI**
- **HTML/CSS/JS**
- **Bootstrap / Tailwind**
- **Custom Movie Browser UI**
- **Dedicated Chatbot Interface**

---

## 📂 Project Highlights

### 🕸️ **1. Data Collection**
- Scraped and processed **50,000+ movie records** using:
  - **IMDb Spider**
  - **Rotten Tomatoes Spider**
- Collected structured metadata from **TMDB API**, including:
  - Genres  
  - Cast & Crew  
  - Overview  
  - Poster & images  
  - Release dates  
  - Ratings & popularity

### 🧹 **2. Data Cleaning & Preprocessing**
- Combined data from all sources into a unified format.
- Cleaned text fields, removed duplicates, normalized genres.
- Engineered features such as:
  - Genre embeddings  
  - Keyword vectors  
  - Cast & director similarity profiles  

### 🤖 **3. Recommendation System**
Developed a **content-based recommendation engine** using:
- TF-IDF vectorization  
- Cosine similarity  
- Metadata-weighted scoring  

Performance:
- **20% improvement** in recommendation relevance vs. baseline model.
- Evaluated using:
  - Precision@K  
  - NDCG  
  - Similarity relevance testing  

### 🖥️ **4. User Interface**
The project includes a clean and responsive UI with:

#### 🎞️ **Movie Browser Page**
- Movie selection panel  
- Movie information display  
- Poster, genres, descriptions  
- “Recommend Similar Movies” button  

#### 🤖 **Dedicated Chatbot Page**
- Chatbot built into its own UI screen  
- Handles:
  - Movie queries  
  - Genre-based suggestions  
  - Cast/actor-related recommendations  
  - Natural language interactions  

---

## 📁 Project Structure

