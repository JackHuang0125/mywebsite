+++
title = "Decision & Classification Tree Learning"
date = 2025-03-18T16:20:00+08:00
draft =  false
tags = ["Learninig Record", "Decision Tree"]
categories = ["Learning"]

[cover]
    image =  "decision.webp"
    alt = '20250318'
    caption = 'decision.webp by ChatGpt 4o'
+++

#### 這是給自己的一份學習紀錄，以免日子久了忘記這是甚麼理論XD

### 🤔 What is decision tree?
Decision tree is a system that relies on evaluating conditions as *True* or *False* to make decisions, such as in classification or regression.  
When the tree needs to classify something into class A or class B, or even into multiple classes (which is called multi-class classification), we call 
it a **classification tree**; On the other hand, when the tree performs regression to predict a numerical value, we call it a **regression tree**.

---

### 🧐 What are the components of a decision tree?
- Root node: It is the starting point for decision-making.
- Internal nodes: They are between the root and leaf nodes. Each node represents a decision based on a specific feature.
- Leaf Nodes: It is the final points of the tree that provide a output(class label in classification or number value in regression).
- Branches: Each time a splitting occurs, new branches are created.
- Splitting: The process of dividing a node into two or more sub-nodes based on a feature.
- Pruning: A technique used to remove unnecessary nodes to simplify the tree and prevent overfitting.
---

### 😮 How the tree do the split?

### 1️⃣  
**Check** all the features and choose the best feature to be the root node. Both numerical and categorical features follow the same process - calculating the Gini impurity to determine the optimal split. Gini impurity is defined as:
$$ Gini \space Index(Impurity) = 1- \sum^N_ip^2_i$$

where
- $p_i$ represents the proportion of instances belonging to class $i$.
- $N$ is the total number of classes in the node.

For each feature, possible split points are considered, and the feature with the minimum Gini impurity is chosen as the root node.
Howeve, when evaluating split nodes, we do not only consider the Gini impurity of the result groups, but also their size. This is done using the weighted Gini impurity, which accounted for the proportin of instances in each child node. The weighted Gini impurity is defined as:
$$
Gini_{split} = \frac{N_L}{N}Gini_{L}+\frac{N_R}{N}Gini_{R}
$$
where
- $N_L$ and $N_R$ are the number of instances in the left and right child nodes.
- $N$ is the total number of instances in the parent node.
- $Gini_{L}$ and $Gini_{R}$ are the Gini impurity values for the left and right nodes.  
Also, there are different ways to calculate Gini impurity for them . If you want to learn more. I recommend watching this video 👇   
***[🔥Decision and Classification Trees, Clearly Explained!!!, StatQuest with Josh Starmer🔥](https://www.youtube.com/watch?v=_L39rN6gz7Y&t=6s)***

### 2️⃣  
**After** making sure the root node, we repeat the process to select internal nodes from other features by recalculating Gini impurity until one of the internal nodes can no longer be split, meaning its Gini impurity equals 0.  
The splitting process continues until one of the following stopping conditions is met:
- Gini impurity = 0, meaning all instances in a node belong to the same class.
- A predefined maximum depth is reached, to prevent overfitting.
- The number of instances in a node falls below a minimum threshold, ensuring statistical reliability.
### 3️⃣
**Overfitting** also happens when using decision tree because the tree will split again and again until one of the following stopping conditions is met like I mentioned earlier. Therefore, to avoid overfitting, decision trees may undergo pruning after training. Pruning removes unnecessary branches that do not significantly improve classification accuracy.

---
### 🔑 Key Takeaways
❤️ 
Choose the root node by calculating Gini impurity for all features and selecting the split with the lowest weighted impurity.  
🧡
Continue splitting recursively until stopping conditions are met.  
💛 
Consider pruning to prevent overfitting and improve generalization.

---
### 📖 Reference
[1] [Scikit-learn](https://scikit-learn.org/stable/modules/tree.html)  
[2] [Decision and Classification Trees, StatQuest with Josh Starmer](https://www.youtube.com/watch?v=_L39rN6gz7Y&t=6s)  
[3] [[Day 12]決策樹 (Decision tree), 10程式中 ](https://ithelp.ithome.com.tw/articles/10271143?sc=hot)
[4] [Wikipedia-Decision tree learning](https://en.wikipedia.org/wiki/Decision_tree_learning)
[5] [L. Breiman, J. Friedman, R. Olshen, and C. Stone. Classification and Regression Trees. Wadsworth, Belmont, CA, 1984](https://rafalab.dfci.harvard.edu/pages/649/section-11.pdf)