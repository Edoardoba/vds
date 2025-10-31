
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
output_dir = _Path(r"C:\Users\canta\Desktop\VDS - new\src\temp_scripts\data_quality_audit_20251031_144019_196")
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
    data_file = r"C:\Users\canta\Desktop\VDS - new\src\temp_scripts\data_quality_audit_20251031_144019_196\data.csv"
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
    import logging
    from datetime import datetime
    import json
    from pathlib import Path

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # Create output directory
    output_dir = Path('data_quality_audit_results')
    output_dir.mkdir(exist_ok=True)

    def assess_completeness(df):
        """Assess data completeness - missing values and null counts"""
        completeness_report = {
            'total_rows': len(df),
            'columns': {}
        }
    
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / len(df)) * 100
            completeness_report['columns'][col] = {
                'missing_count': int(missing_count),
                'missing_percentage': round(missing_pct, 2),
                'completeness_score': round(100 - missing_pct, 2)
            }
    
        return completeness_report

    def assess_accuracy(df):
        """Assess data accuracy - format validation and logical consistency"""
        accuracy_report = {
            'patient_id': {'valid': 0, 'invalid': 0, 'issues': []},
            'age': {'valid': 0, 'invalid': 0, 'issues': []},
            'satisfaction': {'valid': 0, 'invalid': 0, 'issues': []},
            'dates': {'valid': 0, 'invalid': 0, 'issues': []}
        }
    
        # Validate patient_id format (PAT-XXXXXXXX)
        for idx, pid in enumerate(df['patient_id']):
            if pd.isna(pid) or not str(pid).startswith('PAT-'):
                accuracy_report['patient_id']['invalid'] += 1
                if len(accuracy_report['patient_id']['issues']) < 5:
                    accuracy_report['patient_id']['issues'].append(f"Row {idx}: {pid}")
            else:
                accuracy_report['patient_id']['valid'] += 1
    
        # Validate age (reasonable range: 0-120)
        for idx, age in enumerate(df['age']):
            if pd.isna(age) or age < 0 or age > 120:
                accuracy_report['age']['invalid'] += 1
                if len(accuracy_report['age']['issues']) < 5:
                    accuracy_report['age']['issues'].append(f"Row {idx}: {age}")
            else:
                accuracy_report['age']['valid'] += 1
    
        # Validate satisfaction (0-100 scale)
        for idx, sat in enumerate(df['satisfaction']):
            if pd.isna(sat) or sat < 0 or sat > 100:
                accuracy_report['satisfaction']['invalid'] += 1
                if len(accuracy_report['satisfaction']['issues']) < 5:
                    accuracy_report['satisfaction']['issues'].append(f"Row {idx}: {sat}")
            else:
                accuracy_report['satisfaction']['valid'] += 1
    
        # Validate dates
        for idx, row in df.iterrows():
            try:
                arr_date = pd.to_datetime(row['arrival_date'])
                dep_date = pd.to_datetime(row['departure_date'])
                if dep_date < arr_date:
                    accuracy_report['dates']['invalid'] += 1
                    if len(accuracy_report['dates']['issues']) < 5:
                        accuracy_report['dates']['issues'].append(f"Row {idx}: departure before arrival")
                else:
                    accuracy_report['dates']['valid'] += 1
            except:
                accuracy_report['dates']['invalid'] += 1
                if len(accuracy_report['dates']['issues']) < 5:
                    accuracy_report['dates']['issues'].append(f"Row {idx}: invalid date format")
    
        return accuracy_report

    def assess_consistency(df):
        """Assess data consistency - duplicate checks and value distributions"""
        consistency_report = {
            'duplicate_patient_ids': int(df['patient_id'].duplicated().sum()),
            'duplicate_rows': int(df.duplicated().sum()),
            'service_values': df['service'].value_counts().to_dict(),
            'age_statistics': {
                'min': int(df['age'].min()),
                'max': int(df['age'].max()),
                'mean': round(float(df['age'].mean()), 2),
                'median': int(df['age'].median())
            },
            'satisfaction_statistics': {
                'min': int(df['satisfaction'].min()),
                'max': int(df['satisfaction'].max()),
                'mean': round(float(df['satisfaction'].mean()), 2),
                'median': int(df['satisfaction'].median())
            }
        }
    
        return consistency_report

    def assess_validity(df):
        """Assess data validity - business rule validation"""
        validity_report = {
            'business_rules': {},
            'violations': []
        }
    
        # Rule 1: All patients should have a name
        name_empty = (df['name'].isna() | (df['name'].str.strip() == '')).sum()
        validity_report['business_rules']['patients_with_names'] = {
            'rule': 'All patients must have a name',
            'valid_count': int(len(df) - name_empty),
            'violation_count': int(name_empty)
        }
    
        # Rule 2: Service should be from valid list
        valid_services = ['surgery', 'general_medicine', 'emergency', 'ICU', 'pediatrics', 'cardiology']
        invalid_services = df[~df['service'].isin(valid_services)]['service'].unique()
        validity_report['business_rules']['valid_services'] = {
            'rule': f'Service must be one of: {valid_services}',
            'valid_count': int((df['service'].isin(valid_services)).sum()),
            'invalid_services': list(invalid_services)
        }
    
        # Rule 3: Departure date should be after arrival date
        date_violations = 0
        for idx, row in df.iterrows():
            try:
                if pd.to_datetime(row['departure_date']) < pd.to_datetime(row['arrival_date']):
                    date_violations += 1
            except:
                pass
    
        validity_report['business_rules']['date_logic'] = {
            'rule': 'Departure date must be after or equal to arrival date',
            'valid_count': int(len(df) - date_violations),
            'violation_count': date_violations
        }
    
        return validity_report

    def calculate_quality_score(completeness, accuracy, consistency, validity):
        """Calculate overall data quality score (0-100)"""
        # Completeness score (40% weight)
        completeness_scores = [v['completeness_score'] for v in completeness['columns'].values()]
        completeness_avg = np.mean(completeness_scores)
    
        # Accuracy score (30% weight)
        total_valid = sum(v['valid'] for v in accuracy.values() if isinstance(v, dict) and 'valid' in v)
        total_checks = sum(v['valid'] + v['invalid'] for v in accuracy.values() if isinstance(v, dict) and 'valid' in v)
        accuracy_score = (total_valid / total_checks * 100) if total_checks > 0 else 0
    
        # Consistency score (20% weight)
        consistency_score = 100 - (consistency['duplicate_patient_ids'] / len(df) * 100)
    
        # Validity score (10% weight)
        total_violations = sum(v.get('violation_count', 0) for v in validity['business_rules'].values())
        validity_score = 100 - (total_violations / len(df) * 100)
    
        overall_score = (
            completeness_avg * 0.4 +
            accuracy_score * 0.3 +
            consistency_score * 0.2 +
            validity_score * 0.1
        )
    
        return {
            'overall_score': round(overall_score, 2),
            'completeness_score': round(completeness_avg, 2),
            'accuracy_score': round(accuracy_score, 2),
            'consistency_score': round(consistency_score, 2),
            'validity_score': round(validity_score, 2)
        }

    def generate_audit_report(df):
        """Generate comprehensive data quality audit report"""
        logger.info("Starting data quality audit...")
    
        # Run all assessments
        completeness = assess_completeness(df)
        accuracy = assess_accuracy(df)
        consistency = assess_consistency(df)
        validity = assess_validity(df)
        quality_scores = calculate_quality_score(completeness, accuracy, consistency, validity)
    
        # Compile full report
        audit_report = {
            'audit_timestamp': datetime.now().isoformat(),
            'dataset_summary': {
                'total_rows': len(df),
                'total_columns': len(df.columns)
            },
            'quality_scores': quality_scores,
            'completeness_assessment': completeness,
            'accuracy_assessment': accuracy,
            'consistency_assessment': consistency,
            'validity_assessment': validity
        }
    
        # Save JSON report
        json_path = output_dir / 'data_quality_audit_report.json'
        with open(json_path, 'w') as f:
            json.dump(audit_report, f, indent=2)
        logger.info(f"JSON report saved to {json_path}")
    
        # Save CSV summary
        summary_data = {
            'Metric': [
                'Total Rows',
                'Total Columns',
                'Overall Quality Score',
                'Completeness Score',
                'Accuracy Score',
                'Consistency Score',
                'Validity Score',
                'Duplicate Patient IDs',
                'Duplicate Rows'
            ],
            'Value': [
                len(df),
                len(df.columns),
                quality_scores['overall_score'],
                quality_scores['completeness_score'],
                quality_scores['accuracy_score'],
                quality_scores['consistency_score'],
                quality_scores['validity_score'],
                consistency['duplicate_patient_ids'],
                consistency['duplicate_rows']
            ]
        }
    
        summary_df = pd.DataFrame(summary_data)
        csv_path = output_dir / 'data_quality_summary.csv'
        summary_df.to_csv(csv_path, index=False)
        logger.info(f"Summary CSV saved to {csv_path}")
    
        return audit_report, summary_df

    # Main execution
    if __name__ == "__main__":
        # Assume df is already loaded
        # df = pd.read_csv('patients.csv')
    
        # For demonstration, create sample data
        sample_data = [
            {"patient_id": "PAT-09484753", "name": "Richard Rodriguez", "age": 24, "arrival_date": "2025-03-16", "departure_date": "2025-03-22", "service": "surgery", "satisfaction": 61},
            {"patient_id": "PAT-f0644084", "name": "Shannon Walker", "age": 6, "arrival_date": "2025-12-13", "departure_date": "2025-12-14", "service": "surgery", "satisfaction": 83},
            {"patient_id": "PAT-ac6162e4", "name": "Julia Torres", "age": 24, "arrival_date": "2025-06-29", "departure_date": "2025-07-05", "service": "general_medicine", "satisfaction": 83},
            {"patient_id": "PAT-3dda2bb5", "name": "Crystal Johnson", "age": 32, "arrival_date": "2025-10-12", "departure_date": "2025-10-23", "service": "emergency", "satisfaction": 81},
            {"patient_id": "PAT-08591375", "name": "Garrett Lin", "age": 25, "arrival_date": "2025-02-18", "departure_date": "2025-02-25", "service": "ICU", "satisfaction": 76}
        ]
        df = pd.DataFrame(sample_data)
    
        # Generate audit report
        audit_report, summary_df = generate_audit_report(df)
    
        # Print summary to console
        print("\n" + "="*60)
        print("DATA QUALITY AUDIT REPORT - SUMMARY")
        print("="*60)
        print(f"\nAudit Timestamp: {audit_report['audit_timestamp']}")
        print(f"Total Rows: {audit_report['dataset_summary']['total_rows']}")
        print(f"Total Columns: {audit_report['dataset_summary']['total_columns']}")
        print("\n--- QUALITY SCORES ---")
        for key, value in audit_report['quality_scores'].items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        print("\n--- COMPLETENESS ---")
        for col, metrics in audit_report['completeness_assessment']['columns'].items():
            print(f"{col}: {metrics['completeness_score']}% complete ({metrics['missing_count']} missing)")
        print("\n--- CONSISTENCY ---")
        print(f"Duplicate Patient IDs: {audit_report['consistency_assessment']['duplicate_patient_ids']}")
        print(f"Duplicate Rows: {audit_report['consistency_assessment']['duplicate_rows']}")
        print("\n--- VALIDITY VIOLATIONS ---")
        for rule, details in audit_report['validity_assessment']['business_rules'].items():
            print(f"{rule}: {details['violation_count']} violations")
        print("\n" + "="*60)
        print(f"Results saved to: {output_dir}")
        print("="*60 + "\n")
    
    print("Analysis completed successfully!")
    
except Exception as e:
    print("Error during analysis: " + str(e))
    print("Full traceback:")
    _traceback.print_exc()
    _sys.exit(1)
