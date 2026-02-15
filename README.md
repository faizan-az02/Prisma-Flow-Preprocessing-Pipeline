# PrismaFlow

Transforming raw data into ML-ready insights, effortlessly.

PrismaFlow is an **automated, modular preprocessing pipeline** designed to simplify data cleaning, normalization, and transformation. It’s built to handle multiple workflows and scales with your projects.

---

Feature Encoding (Categorical → Numeric)

ML models usually need numbers.

    Common Approaches:

    Label Encoding → ordinal categories

    One-Hot Encoding → nominal categories

    Target Encoding → high cardinality

Feature Scaling / Normalization

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

Feature Selection

Remove useless or harmful features.

    Techniques:

    Variance threshold

    Correlation filtering

    Mutual information

    Tree-based feature importance

Feature Engineering

Now you create better signals.

    Examples:

    Date → Year / Month / Day / DayOfWeek

    Ratios → Currency per minute, etc

    Interaction features → A * B

Class Imbalance Handling (If Classification)

Check target distribution.

    If Imbalanced:

    SMOTE

    Undersampling

    Class weights

Train / Test Preparation

Split BEFORE final fitting transforms (important).

    Do:

    Train/Test split

    Possibly Validation split

Pipeline Object Creation (Very Important)

    Bundle preprocessing steps.

    Why:
    Prevents data leakage.
    Ensures inference uses same transforms.

Data Leakage Checks

Make sure you didn’t accidentally use future info.

    Example:

    Don’t scale using full dataset before split

    Don’t encode using target leakage