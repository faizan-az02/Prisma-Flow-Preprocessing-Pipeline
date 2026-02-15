# PrismaFlow

Transforming raw data into ML-ready insights, effortlessly.

PrismaFlow is an **automated, modular preprocessing pipeline** designed to simplify data cleaning, normalization, and transformation. It’s built to handle multiple workflows and scales with your projects.

---

Work In Progress

1️⃣ Data Type & Schema Finalization

Make sure everything is the correct type.

Do:

    Convert dates → datetime objects

    Ensure numeric columns are numeric

    Ensure categorical columns are string/category


2️⃣ Outlier Detection & Handling

Basic cleaning doesn’t usually handle extreme values.

    Options:

    IQR filtering

    Z-score filtering

    Winsorization (cap extremes)


3️⃣ Feature Encoding (Categorical → Numeric)

ML models usually need numbers.

    Common Approaches:

    Label Encoding → ordinal categories

    One-Hot Encoding → nominal categories

    Target Encoding → high cardinality

4️⃣ Feature Scaling / Normalization

Very important for many models.

    Options:

    Standard Scaling (mean=0, std=1)

    Min-Max Scaling (0 → 1)

    Robust Scaling (good if outliers exist)

    Critical For:

    Neural Networks

    SVM

    KNN

    Gradient methods

5️⃣ Feature Selection

Remove useless or harmful features.

    Techniques:

    Variance threshold

    Correlation filtering

    Mutual information

    Tree-based feature importance

6️⃣ Feature Engineering

Now you create better signals.

    Examples:

    Date → Year / Month / Day / DayOfWeek

    Ratios → Currency per minute, etc

    Interaction features → A * B

7️⃣ Class Imbalance Handling (If Classification)

Check target distribution.

    If Imbalanced:

    SMOTE

    Undersampling

    Class weights

8️⃣ Train / Test Preparation

Split BEFORE final fitting transforms (important).

    Do:

    Train/Test split

    Possibly Validation split

9️⃣ Pipeline Object Creation (Very Important)

    Bundle preprocessing steps.

    Why:
    Prevents data leakage.
    Ensures inference uses same transforms.

🔟 Data Leakage Checks

Make sure you didn’t accidentally use future info.

    Example:

    Don’t scale using full dataset before split

    Don’t encode using target leakage