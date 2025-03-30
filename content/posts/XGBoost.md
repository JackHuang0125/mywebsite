+++
title = "XGBoost Learning"
date = 2025-03-30T08:00:00+08:00
draft =  false
tags = ["Learninig Record", "Boosting"]
categories = ["Learning"]

[cover]
    image =  "XGBoost.webp"
    alt = '20250330'
    caption = 'XGBoost.webp by ChatGpt 4o'
+++

#### 這是給自己的一份學習紀錄，以免日子久了忘記這是甚麼理論XD

# 🦹 XGBoost Boost
### What is XGBoost?
Think of XGBoost as a team of smart tutors, each correcting the mistakes made by the previous one, gradually improving your answers step by step.

---
### 🗝 Key Concepts in XGBoost Tree Building
1. Start with an initial guess (e.g., average score).
2. Measure how far off the prediction is from the real answer (this is called the **residual**).
3. The next tree learns how to **fix these errors**.
4. Every new tree improves on the mistakes of the previous trees.

---
### 🥢 How to Divide the Data (Not Randomly)
1. XGBoost doesn’t split data based on traditional methods like information gain.
2. It uses a formula called **Gain**, which measures how much a split improves prediction.
3. A split only happens if:  
  **(Left + Right Score) > (Parent Score + Penalty)**

---
### ❓ How do we know if a split is good?
1. Use a value called **Similarity Score**
2. The higher the score, the more consistent (similar) the residuals are in that group

---
### 🐢 Two Ways to Find Splits: Accurate- Exact Greedy Algorithm
- Try **all** possible features and split points
- Very accurate but **very slow**

---
### 🐇 Two Ways to Find Splits: Fast- Approximate Algorithm
- Uses **feature quantiles** (e.g., median) to propose a few split points
- Group the data based on these splits and evaluate the best one
- Two options:
  - **Global Proposal**: use global info to suggest splits
  - **Local Proposal**: use local (node-specific) info

---
### 🏋 Weighted Quantile Sketch
- Some data points are more important (like how teachers focus more on students who struggle)
- Each data point has a **weight** based on how wrong it was (second-order gradient)
- Use these weights to suggest better and more meaningful split points

---
### 🕳 Handling Missing Values
- What if some feature values are **missing**?
- XGBoost learns a **default path** for missing data
- This makes the model more robust even when the data isn’t complete

---
### 🧚‍♀️ Controlling Model Complexity: Regularization

- Gamma (γ)
    - Penalizes overly complex trees
    - A split only happens if **Gain > Gamma**
    - Helps stop the model from splitting when it's not really helpful

- Lambda (λ)
    - Shrinks leaf node prediction values
    - Prevents overconfident and overfit models

---
### ✂ Pruning
- After building the tree, XGBoost may **prune** parts that don't help
- If a split's gain is **less than Gamma**, that branch is **cut off**
- This leads to **simpler trees** that generalize better

---
### 🧞‍♂️ Extra Tricks: Learn Smoothly and Fast

- Shrinkage (Learning Rate)
    - Only take a small step with each new tree
    - Makes learning **slower but more stable**

- Column Subsampling
    - Only use **a subset of features** for each tree
    - This speeds up training and reduces overfitting