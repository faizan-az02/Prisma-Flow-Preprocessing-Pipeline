# PrismaFlow

Transforming raw data into ML-ready insights, effortlessly.

PrismaFlow is an **automated, modular preprocessing pipeline** designed to simplify data cleaning, normalization, and transformation. It’s built to handle multiple workflows and scales with your projects.

---

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