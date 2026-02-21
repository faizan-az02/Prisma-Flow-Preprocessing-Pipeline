# 🌊 PrismaFlow

> **Clean, Transform, And Explore Your CSV Data—In One Flow.**

PrismaFlow is a powerful, automated preprocessing pipeline that transforms raw data into ML-ready datasets. With an intuitive web interface and flexible CLI, it handles everything from null value imputation to feature engineering—all while giving you complete control over every transformation step.

---

## ✨ Features

### 🎯 **Comprehensive Data Preprocessing**
- **Smart Column Management**: Remove empty columns (≥95% null), manual column selection, and protected columns
- **Null Value Handling**: Configurable threshold-based imputation (mean/mode) or row dropping
- **Outlier Detection & Treatment**: IQR, Z-Score, or Modified Z-Score methods with remove/cap options
- **Feature Encoding**: Label encoding or one-hot encoding for categorical variables
- **Scaling**: Standard scaling or Min-Max normalization
- **Feature Selection**: Variance threshold and correlation-based feature elimination
- **Temporal Feature Extraction**: Automatic extraction from datetime columns (year, month, day, hour, etc.)
- **Data Type Inference**: Automatic conversion with smart datetime detection

### 🖥️ **Dual Interface**
- **Web UI**: Beautiful, modern interface with real-time previews, data reports, and step-by-step configuration
- **CLI**: Fast, scriptable command-line interface for batch processing and automation

### 📊 **Advanced Capabilities**
- **Per-Column Control**: Skip outlier handling or scaling for specific columns
- **Selective Pipeline Execution**: Enable/disable individual preprocessing steps
- **Comprehensive Logging**: Detailed logs for every transformation
- **Data Reports**: Column-level statistics (null percentage, unique values, data types)
- **Metrics Tracking**: Time elapsed, rows/columns removed, outliers handled

---

## 📖 Usage

### Web Interface

1. **Upload Data**: Click your intended source and select your dataset
2. **Choose Preprocessing Mode**:
   - **Cleaning Data**: Quick data cleaning with essential steps only
     - Configure null threshold percentage (default: 5%)
     - Select columns to remove (optional)
     - Runs: Column removal → Drop empty columns → Handle nulls → Finalize types → Handle outliers (IQR)
   - **Advanced**: Full-featured preprocessing with complete control
     - Select pipeline steps to execute
     - Set null threshold percentage
     - Choose encoding method (Label/One-Hot)
     - Configure outlier handling (Skip/Remove/Cap) and detection method
     - Select scaling method (Standard/MinMax)
     - Specify columns to remove, keep, or skip for specific operations
3. **Run Pipeline**: Click "Run Data Cleaning" or "Run Advanced Preprocessing"
4. **Download Results**: Get your processed CSV and detailed logs
5. **View Data Report**: Click "Data Report" button to see column statistics (null %, unique values, data types)


## 🔧 Pipeline Steps

PrismaFlow offers two modes with different step configurations:

### 🧹 Cleaning Data Mode
Ideal for visualization
Runs essential cleaning steps only:
1. **Manual Columns Removal** (`manual_columns`): Removes user-specified columns
2. **Drop Empty Columns** (`drop_empty_columns`): Removes columns with ≥95% null/empty values
3. **Handle Null Values** (`handle_nulls`): Imputes or drops rows based on null threshold
4. **Finalize Data Types** (`finalize_dtypes`): Converts data types and detects datetime columns
5. **Handle Outliers** (`handle_outliers`): Removes outliers using IQR method

### ⚙️ Advanced Preprocessing Mode
Get your data ready for models 
Full pipeline with all available steps:
1. **Target Column Removal** (`remove_target`): Temporarily removes the target column for processing
2. **Manual Columns Removal** (`manual_columns`): Removes user-specified columns
3. **Drop Empty Columns** (`drop_empty_columns`): Removes columns with ≥95% null/empty values
4. **Handle Null Values** (`handle_nulls`): Imputes or drops rows based on null threshold
5. **Finalize Data Types** (`finalize_dtypes`): Converts data types and detects datetime columns
6. **Handle Outliers** (`handle_outliers`): Removes or caps outliers using selected method
7. **Encode Features** (`encoding`): Encodes categorical variables (Label/One-Hot)
8. **Feature Selection** (`feature_selection`): Removes low-variance and highly correlated features
9. **Extract Temporal Features** (`temporal_features`): Extracts date/time components from datetime columns
10. **Scaling** (`scaling`): Normalizes numerical features (Standard/MinMax)
11. **Add Target Column** (`add_target`): Restores the target column to the final dataset

---

## ⚙️ Configuration Options

### Outlier Handling

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| `outlier_method` | `iqr`, `zscore`, `modified_zscore` | `iqr` | Detection method |
| `outlier_action` | `skip`, `remove`, `cap` | `remove` | Treatment strategy |
| `outlier_param` | Float | `1.5` (IQR), `3.0` (Z-Score), `3.5` (Modified) | Threshold/multiplier |

### Null Value Handling

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `null_threshold` | Float (0-1) | `0.05` | Drop rows if null % > threshold; otherwise impute |

### Encoding

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| `encoding_method` | `label`, `onehot` | `label` | Categorical encoding strategy |

### Scaling

| Parameter | Options | Default | Description |
|-----------|---------|---------|-------------|
| `scaling_method` | `standard`, `minmax` | `standard` | Normalization method |

---

## 📁 Project Structure

```
Prisma-Flow-Preprocessing-Pipeline/
├── app.py                 # Flask web application
├── main.py                # Core pipeline logic
├── cli.py                 # Command-line interface
├── templates/
│   └── index.html         # Web UI template
├── static/
│   ├── style.css          # UI styling
│   └── favicon.svg        # Brand icon
├── null_values.py         # Null handling module
├── clear_columns.py        # Empty column removal
├── remove_columns.py      # Manual column removal
├── finalize_types.py      # Data type conversion
├── outliers_removal.py    # Outlier detection & treatment
├── encoding.py            # Feature encoding
├── scaling.py             # Feature scaling
├── feature_selection.py   # Feature selection
├── temporal_features.py   # Temporal feature extraction
├── remove_target.py       # Target column removal
├── add_target.py          # Target column restoration
├── export_file.py         # CSV export utility
├── divider.py             # Logging utility
└── logs.txt               # Pipeline execution logs
```


## 🎨 Web UI Features

### Data Preview
- **Raw Data Sample**: View first 15 rows with horizontal/vertical scrolling
- **Processed Data Sample**: Preview results after preprocessing
- **Shape Information**: Row and column counts displayed

### Data Report
- **Column Statistics**: Null percentage, unique value counts, data types
- **Scrollable Table**: Easy navigation through large datasets
- **Export Ready**: All information needed for data profiling

### Cleaning Data Mode
- **Null Threshold Configuration**: Set percentage threshold for null value handling
- **Column Removal**: Select specific columns to remove before cleaning
- **Quick Processing**: Fast execution with essential cleaning steps only

### Advanced Configuration
- **Step Selection**: Enable/disable individual pipeline steps
- **Per-Column Control**: Fine-tune outlier handling and scaling per column
- **Real-Time Validation**: Disabled options when no data is uploaded
- **Full Pipeline Control**: Access to all preprocessing transformations

---

## 📝 Logging

Every pipeline run generates detailed logs in `logs.txt`. The log header indicates the mode:

**Cleaning Data Mode:**
```
2026-02-19 10:34:00,493 | INFO | Cleaning Initiated
2026-02-19 10:34:00,503 | INFO | === MANUAL REMOVAL OF COLUMNS STARTED ===
2026-02-19 10:34:00,503 | INFO | Removed column "fdc_id"
2026-02-19 10:34:00,618 | INFO | === AUTO REMOVAL OF EMPTY COLUMNS STARTED ===
...
```

**Advanced Preprocessing Mode:**
```
2026-02-19 10:34:00,493 | INFO | Preprocessing Initiated
2026-02-19 10:34:00,503 | INFO | === MANUAL REMOVAL OF COLUMNS STARTED ===
2026-02-19 10:34:00,503 | INFO | Removed column "fdc_id"
2026-02-19 10:34:00,618 | INFO | === AUTO REMOVAL OF EMPTY COLUMNS STARTED ===
...
```

Logs include:
- Mode indicator - Cleaning/Preprocessing
- Step-by-step execution details
- Column removals and transformations
- Row counts and statistics
- Error messages (if any)

---

## 🔒 Data Privacy

- **In-Memory Processing**: All data is processed in memory; no persistent storage
- **Session-Based**: Data is cleared after 1 hour of inactivity
- **No External APIs**: All processing happens locally
- **Log Files**: Only transformation logs are written (no data content)

---

## 🚧 Future Enhancements

- [ ] Support for Excel, JSON, and database sources
- [ ] Batch processing for multiple files
- [ ] Integration with cloud storage (S3, GCS)
- [ ] Real-time data streaming support
- [ ] Advanced visualization dashboard

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

