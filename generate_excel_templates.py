#!/usr/bin/env python
"""
Script to generate Excel templates for data import
"""
import os
import sys
import django
import pandas as pd
from django.apps import apps

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def get_model_fields(model_name):
    """Get fields for a given model"""
    try:
        model = apps.get_model('cricket_stats', model_name)
        fields = []
        
        for field in model._meta.fields:
            if not field.auto_created:  # Skip auto-created fields like id
                fields.append({
                    'name': field.name,
                    'type': field.get_internal_type(),
                    'required': not field.null and not field.blank and not field.has_default(),
                })
        
        return fields
    except LookupError:
        print(f"Model {model_name} not found")
        return []

def create_excel_template(model_name, output_dir='excel_templates'):
    """Create an Excel template for a model"""
    fields = get_model_fields(model_name)
    
    if not fields:
        return False
    
    # Create a DataFrame with column headers
    df = pd.DataFrame(columns=[field['name'] for field in fields])
    
    # Add a sample row with empty values
    sample_row = {}
    for field in fields:
        if field['type'] == 'ForeignKey' or field['type'] == 'ManyToManyField':
            sample_row[field['name']] = "Enter ID here"
        elif field['type'] == 'DateField' or field['type'] == 'DateTimeField':
            sample_row[field['name']] = "YYYY-MM-DD"
        elif field['type'] == 'BooleanField':
            sample_row[field['name']] = "True/False"
        elif field['type'] == 'IntegerField':
            sample_row[field['name']] = 0
        elif field['type'] == 'FloatField' or field['type'] == 'DecimalField':
            sample_row[field['name']] = 0.0
        else:
            sample_row[field['name']] = ""
    
    df = df.append(sample_row, ignore_index=True)
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Save to Excel
    output_file = os.path.join(output_dir, f"{model_name.lower()}_template.xlsx")
    df.to_excel(output_file, index=False)
    
    print(f"Template created: {output_file}")
    return True

def main():
    """Main function to generate templates for all models"""
    # Create output directory
    output_dir = 'excel_templates'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # List of models to create templates for
    models = [
        'Player',
        'Team',
        'Tournament',
        'Match',
        'MatchPlayer',
        'BattingInnings',
        'BowlingInnings',
        'MatchFormat',
        'TeamStanding',
        'TrainingSession',
        'PlayerAttendance',
    ]
    
    print("Generating Excel templates...")
    
    for model_name in models:
        success = create_excel_template(model_name, output_dir)
        if success:
            print(f"✓ Created template for {model_name}")
        else:
            print(f"✗ Failed to create template for {model_name}")
    
    print(f"\nAll templates have been saved to the '{output_dir}' directory.")
    print("You can download these files and use them to prepare your data for import.")

if __name__ == "__main__":
    main()
