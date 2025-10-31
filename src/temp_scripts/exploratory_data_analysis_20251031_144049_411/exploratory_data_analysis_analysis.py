
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

# Try to import seaborn, but continue without it if unavailable
try:
    import seaborn as sns
    _has_seaborn = True
except ImportError as e:
    print("Warning: seaborn not available - some visualization features may be limited")
    print(f"Import error")
    _has_seaborn = False
    # Create a dummy sns object to avoid NameError
    class _DummySeaborn:
        def set_palette(self, *args, **kwargs):
            pass
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    sns = _DummySeaborn()

import sys as _sys
import os as _os
from pathlib import Path as _Path
import traceback as _traceback
import time as _time

# Set output directory
output_dir = _Path(r"C:\Users\canta\Desktop\VDS - new\src\temp_scripts\exploratory_data_analysis_20251031_144049_411")
_os.chdir(output_dir)

# Set matplotlib style
plt.style.use('default')
if _has_seaborn:
    try:
        sns.set_palette("husl")
    except Exception as e:
        print(f"Warning: Could not set seaborn palette: ")

# Configure matplotlib for better compatibility
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100
plt.rcParams['savefig.bbox'] = 'tight'

def _auto_save_show(*args, **kwargs):
    try:
        filename = "figure_" + str(int(_time.time()*1000)) + ".png"
        plt.savefig(filename)
        plt.close()
        print("Saved figure: " + filename)
    except Exception as e:
        print("Failed to save figure: " + str(e))

plt.show = _auto_save_show

try:
    # Load the data
    data_file = r"C:\Users\canta\Desktop\VDS - new\src\temp_scripts\exploratory_data_analysis_20251031_144049_411\data.csv"
    file_extension = _Path(data_file).suffix.lower()
    
    print("Loading data from: " + str(data_file))
    print("File extension: " + str(file_extension))
    
    if file_extension == '.csv':
        df = pd.read_csv(data_file)
    elif file_extension in ['.xlsx', '.xls']:
        df = pd.read_excel(data_file)
    else:
        raise ValueError("Unsupported file format: " + str(file_extension))
    
    print("Data loaded successfully. Shape: " + str(df.shape))
    print("Columns: " + str(list(df.columns)))
    print("Data types: " + str(df.dtypes.to_dict()))
    
    # Execute user code
    import pandas as pd
    import numpy as np
    import warnings
    from datetime import datetime
    import json
    import logging

    warnings.filterwarnings('ignore')

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logger = logging.getLogger(__name__)

    # Assume df is already loaded
    # df = pd.read_csv('patients.csv')

    def exploratory_data_analysis(df):
        """
        Comprehensive exploratory data analysis of patient dataset
        """
    
        results = {
            'dataset_overview': {},
            'data_quality': {},
            'distributions': {},
            'relationships': {},
            'business_insights': []
        }
    
        # ===== DATASET OVERVIEW =====
        logger.info("\n" + "="*60)
        logger.info("EXPLORATORY DATA ANALYSIS - PATIENTS DATASET")
        logger.info("="*60)
    
        results['dataset_overview']['total_rows'] = len(df)
        results['dataset_overview']['total_columns'] = len(df.columns)
        results['dataset_overview']['columns'] = list(df.columns)
        results['dataset_overview']['data_types'] = df.dtypes.astype(str).to_dict()
    
        logger.info(f"\n📊 DATASET OVERVIEW")
        logger.info(f"  • Total Records: {len(df):,}")
        logger.info(f"  • Total Features: {len(df.columns)}")
        logger.info(f"  • Date Range: Analysis Period")
    
        # ===== DATA QUALITY ASSESSMENT =====
        logger.info(f"\n🔍 DATA QUALITY ASSESSMENT")
    
        missing_data = df.isnull().sum()
        results['data_quality']['missing_values'] = missing_data.to_dict()
        results['data_quality']['completeness_pct'] = ((1 - df.isnull().sum() / len(df)) * 100).round(2).to_dict()
    
        logger.info(f"  • Missing Values: {missing_data.sum()} total")
        for col in df.columns:
            if missing_data[col] > 0:
                logger.info(f"    - {col}: {missing_data[col]} ({missing_data[col]/len(df)*100:.1f}%)")
    
        if missing_data.sum() == 0:
            logger.info(f"    ✓ No missing values detected")
    
        # Duplicate check
        duplicates = df.duplicated().sum()
        results['data_quality']['duplicate_rows'] = int(duplicates)
        logger.info(f"  • Duplicate Rows: {duplicates}")
    
        # ===== AGE DISTRIBUTION =====
        logger.info(f"\n📈 AGE DISTRIBUTION")
        age_stats = {
            'mean': float(df['age'].mean()),
            'median': float(df['age'].median()),
            'std': float(df['age'].std()),
            'min': int(df['age'].min()),
            'max': int(df['age'].max()),
            'q25': float(df['age'].quantile(0.25)),
            'q75': float(df['age'].quantile(0.75))
        }
        results['distributions']['age'] = age_stats
    
        logger.info(f"  • Mean Age: {age_stats['mean']:.1f} years")
        logger.info(f"  • Median Age: {age_stats['median']:.1f} years")
        logger.info(f"  • Std Dev: {age_stats['std']:.1f} years")
        logger.info(f"  • Range: {age_stats['min']} - {age_stats['max']} years")
    
        # Age groups
        age_bins = [0, 18, 35, 50, 65, 100]
        age_labels = ['0-17', '18-34', '35-49', '50-64', '65+']
        df['age_group'] = pd.cut(df['age'], bins=age_bins, labels=age_labels, right=False)
        age_group_dist = df['age_group'].value_counts().sort_index().to_dict()
        results['distributions']['age_groups'] = {str(k): int(v) for k, v in age_group_dist.items()}
    
        logger.info(f"  • Age Groups Distribution:")
        for group, count in sorted(age_group_dist.items()):
            pct = count / len(df) * 100
            logger.info(f"    - {group}: {count} ({pct:.1f}%)")
    
        # ===== SATISFACTION ANALYSIS =====
        logger.info(f"\n😊 SATISFACTION ANALYSIS")
        satisfaction_stats = {
            'mean': float(df['satisfaction'].mean()),
            'median': float(df['satisfaction'].median()),
            'std': float(df['satisfaction'].std()),
            'min': int(df['satisfaction'].min()),
            'max': int(df['satisfaction'].max())
        }
        results['distributions']['satisfaction'] = satisfaction_stats
    
        logger.info(f"  • Mean Satisfaction: {satisfaction_stats['mean']:.1f}/100")
        logger.info(f"  • Median Satisfaction: {satisfaction_stats['median']:.1f}/100")
        logger.info(f"  • Std Dev: {satisfaction_stats['std']:.1f}")
    
        # Satisfaction categories
        df['satisfaction_level'] = pd.cut(df['satisfaction'], 
                                           bins=[0, 40, 70, 100], 
                                           labels=['Low', 'Medium', 'High'],
                                           right=True)
        sat_dist = df['satisfaction_level'].value_counts().to_dict()
        results['distributions']['satisfaction_levels'] = {str(k): int(v) for k, v in sat_dist.items()}
    
        logger.info(f"  • Satisfaction Levels:")
        for level in ['Low', 'Medium', 'High']:
            count = sat_dist.get(level, 0)
            pct = count / len(df) * 100
            logger.info(f"    - {level}: {count} ({pct:.1f}%)")
    
        # ===== SERVICE ANALYSIS =====
        logger.info(f"\n🏥 SERVICE DISTRIBUTION")
        service_dist = df['service'].value_counts().to_dict()
        results['distributions']['services'] = {str(k): int(v) for k, v in service_dist.items()}
    
        for service, count in service_dist.items():
            pct = count / len(df) * 100
            logger.info(f"  • {service}: {count} ({pct:.1f}%)")
    
        # ===== LENGTH OF STAY ANALYSIS =====
        logger.info(f"\n⏱️  LENGTH OF STAY ANALYSIS")
        df['arrival_date'] = pd.to_datetime(df['arrival_date'])
        df['departure_date'] = pd.to_datetime(df['departure_date'])
        df['length_of_stay'] = (df['departure_date'] - df['arrival_date']).dt.days
    
        los_stats = {
            'mean': float(df['length_of_stay'].mean()),
            'median': float(df['length_of_stay'].median()),
            'std': float(df['length_of_stay'].std()),
            'min': int(df['length_of_stay'].min()),
            'max': int(df['length_of_stay'].max())
        }
        results['distributions']['length_of_stay'] = los_stats
    
        logger.info(f"  • Mean LOS: {los_stats['mean']:.1f} days")
        logger.info(f"  • Median LOS: {los_stats['median']:.1f} days")
        logger.info(f"  • Range: {los_stats['min']} - {los_stats['max']} days")
    
        # ===== RELATIONSHIPS & CORRELATIONS =====
        logger.info(f"\n🔗 KEY RELATIONSHIPS")
    
        # Satisfaction by Service
        sat_by_service = df.groupby('service')['satisfaction'].agg(['mean', 'count']).round(2)
        results['relationships']['satisfaction_by_service'] = sat_by_service.to_dict()
    
        logger.info(f"  • Satisfaction by Service:")
        for service in sat_by_service.index:
            mean_sat = sat_by_service.loc[service, 'mean']
            count = int(sat_by_service.loc[service, 'count'])
            logger.info(f"    - {service}: {mean_sat:.1f}/100 (n={count})")
    
        # Satisfaction by Age Group
        sat_by_age = df.groupby('age_group')['satisfaction'].agg(['mean', 'count']).round(2)
        results['relationships']['satisfaction_by_age_group'] = sat_by_age.to_dict()
    
        logger.info(f"  • Satisfaction by Age Group:")
        for age_grp in sat_by_age.index:
            mean_sat = sat_by_age.loc[age_grp, 'mean']
            count = int(sat_by_age.loc[age_grp, 'count'])
            logger.info(f"    - {age_grp}: {mean_sat:.1f}/100 (n={count})")
    
        # Correlation: Age vs Satisfaction
        age_sat_corr = df['age'].corr(df['satisfaction'])
        results['relationships']['age_satisfaction_correlation'] = float(age_sat_corr)
        logger.info(f"  • Age-Satisfaction Correlation: {age_sat_corr:.3f}")
    
        # Correlation: Length of Stay vs Satisfaction
        los_sat_corr = df['length_of_stay'].corr(df['satisfaction'])
        results['relationships']['los_satisfaction_correlation'] = float(los_sat_corr)
        logger.info(f"  • LOS-Satisfaction Correlation: {los_sat_corr:.3f}")
    
        # ===== BUSINESS INSIGHTS =====
        logger.info(f"\n💡 BUSINESS INSIGHTS")
    
        insights = []
    
        # Insight 1: High satisfaction rate
        high_sat_pct = (df['satisfaction'] >= 70).sum() / len(df) * 100
        insights.append(f"✓ {high_sat_pct:.1f}% of patients report high satisfaction (≥70)")
    
        # Insight 2: Service performance
        best_service = sat_by_service['mean'].idxmax()
        best_sat = sat_by_service['mean'].max()
        insights.append(f"✓ Best performing service: {best_service} ({best_sat:.1f}/100)")
    
        worst_service = sat_by_service['mean'].idxmin()
        worst_sat = sat_by_service['mean'].min()
        insights.append(f"⚠ Lowest performing service: {worst_service} ({worst_sat:.1f}/100)")
    
        # Insight 3: Age impact
        if abs(age_sat_corr) < 0.1:
            insights.append(f"✓ Age has minimal impact on satisfaction (r={age_sat_corr:.3f})")
        elif age_sat_corr > 0:
            insights.append(f"✓ Older patients tend to be more satisfied (r={age_sat_corr:.3f})")
        else:
            insights.append(f"⚠ Younger patients tend to be more satisfied (r={age_sat_corr:.3f})")
    
        # Insight 4: LOS impact
        if abs(los_sat_corr) < 0.1:
            insights.append(f"✓ Length of stay has minimal impact on satisfaction (r={los_sat_corr:.3f})")
        elif los_sat_corr < 0:
            insights.append(f"✓ Shorter stays correlate with higher satisfaction (r={los_sat_corr:.3f})")
        else:
            insights.append(f"⚠ Longer stays correlate with higher satisfaction (r={los_sat_corr:.3f})")
    
        # Insight 5: Patient demographics
        dominant_age_group = age_group_dist.get(max(age_group_dist, key=age_group_dist.get))
        dominant_age_label = max(age_group_dist, key=age_group_dist.get)
        insights.append(f"✓ Largest patient cohort: {dominant_age_label} ({dominant_age_group} patients)")
    
        results['business_insights'] = insights
    
        for i, insight in enumerate(insights, 1):
            logger.info(f"  {i}. {insight}")
    
        logger.info("\n" + "="*60)
    
        return results, df

    # Execute analysis
    if __name__ == "__main__":
        # Load data
        df = pd.read_csv('patients.csv')
    
        # Run analysis
        results, df_enhanced = exploratory_data_analysis(df)
    
        # Save results to JSON
        with open('eda_results.json', 'w') as f:
            json.dump(results, f, indent=2)
    
        # Save enhanced dataset with computed features
        df_enhanced.to_csv('patients_enhanced.csv', index=False)
    
        # Create summary statistics CSV
        summary_stats = pd.DataFrame({
            'Metric': ['Total Patients', 'Mean Age', 'Mean Satisfaction', 'Mean LOS (days)', 
                       'High Satisfaction %', 'Missing Values'],
            'Value': [
                len(df_enhanced),
                f"{df_enhanced['age'].mean():.1f}",
                f"{df_enhanced['satisfaction'].mean():.1f}",
                f"{df_enhanced['length_of_stay'].mean():.1f}",
                f"{(df_enhanced['satisfaction'] >= 70).sum() / len(df_enhanced) * 100:.1f}%",
                df_enhanced.isnull().sum().sum()
            ]
        })
        summary_stats.to_csv('eda_summary.csv', index=False)
    
        logger.info("\n✅ Analysis complete. Files saved:")
        logger.info("   • eda_results.json")
        logger.info("   • patients_enhanced.csv")
        logger.info("   • eda_summary.csv")
    
    print("Analysis completed successfully!")
    
except Exception as e:
    print("Error during analysis: " + str(e))
    print("Full traceback:")
    _traceback.print_exc()
    _sys.exit(1)
