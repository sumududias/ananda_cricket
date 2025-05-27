#!/usr/bin/env python
"""
Script to import data from Excel files and configure import-export functionality
"""
import os
import sys
import django
import pandas as pd
from django.apps import apps
from django.contrib import admin

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def check_import_export_config():
    """Check if import-export is properly configured in admin.py"""
    try:
        # Import the admin module
        from cricket_stats import admin as cricket_admin
        
        # Check if ImportExportModelAdmin is being used
        from import_export.admin import ImportExportModelAdmin
        
        # Get all registered models in the admin
        registered_models = []
        for model, model_admin in admin.site._registry.items():
            app_label = model._meta.app_label
            if app_label == 'cricket_stats':
                registered_models.append({
                    'model': model.__name__,
                    'admin_class': model_admin.__class__.__name__,
                    'has_import_export': isinstance(model_admin, ImportExportModelAdmin)
                })
        
        # Print the results
        print("\n=== Import/Export Configuration Check ===")
        if not registered_models:
            print("No cricket_stats models are registered in the admin.")
            return False
        
        all_configured = True
        for model_info in registered_models:
            status = "✓ Configured" if model_info['has_import_export'] else "✗ Not configured"
            print(f"{model_info['model']}: {status}")
            if not model_info['has_import_export']:
                all_configured = False
        
        return all_configured
    
    except ImportError as e:
        print(f"Error importing modules: {e}")
        return False

def setup_import_export():
    """Add code to configure import-export in admin.py"""
    admin_file = os.path.join('cricket_stats', 'admin.py')
    
    # Check if the file exists
    if not os.path.exists(admin_file):
        print(f"Admin file not found: {admin_file}")
        return False
    
    # Read the current content
    with open(admin_file, 'r') as f:
        content = f.read()
    
    # Check if import-export is already imported
    if 'import_export' not in content:
        # Add import statements at the top
        import_stmt = """from import_export import resources
from import_export.admin import ImportExportModelAdmin
"""
        # Find the position after the existing imports
        import_end = content.find('\n\n', content.find('import'))
        if import_end == -1:
            import_end = content.find('\n', content.find('import'))
        
        if import_end != -1:
            content = content[:import_end] + '\n' + import_stmt + content[import_end:]
        else:
            content = import_stmt + content
    
    # Replace ModelAdmin with ImportExportModelAdmin
    content = content.replace('admin.ModelAdmin', 'ImportExportModelAdmin')
    
    # Add resource classes for each model
    models = [
        'Player', 'Team', 'Tournament', 'Match', 'MatchPlayer',
        'BattingInnings', 'BowlingInnings', 'MatchFormat',
        'TeamStanding', 'TrainingSession', 'PlayerAttendance'
    ]
    
    # Check if resource classes already exist
    if 'class PlayerResource' not in content:
        # Add resource classes before the admin classes
        resources = "\n\n# Import/Export Resources\n"
        for model in models:
            resources += f"""
class {model}Resource(resources.ModelResource):
    class Meta:
        model = {model}
        skip_unchanged = True
        report_skipped = False
        import_id_fields = ['id']
"""
        
        # Find the position to insert the resources
        admin_start = content.find('class ')
        if admin_start != -1:
            content = content[:admin_start] + resources + content[admin_start:]
        else:
            content += resources
    
    # Update admin classes to use resources
    for model in models:
        admin_class = f"class {model}Admin"
        resource_line = f"    resource_class = {model}Resource"
        
        if admin_class in content and resource_line not in content:
            # Find the position after the class definition
            class_start = content.find(admin_class)
            class_end = content.find(')', content.find('(', class_start))
            
            if class_end != -1:
                # Find the position after the opening brace
                brace_pos = content.find('{', class_end)
                if brace_pos == -1:
                    brace_pos = content.find(':', class_end)
                
                if brace_pos != -1:
                    insert_pos = content.find('\n', brace_pos) + 1
                    content = content[:insert_pos] + resource_line + '\n' + content[insert_pos:]
    
    # Write the updated content
    with open(admin_file + '.new', 'w') as f:
        f.write(content)
    
    print(f"\nCreated updated admin file: {admin_file}.new")
    print("Review this file and if it looks good, replace the original admin.py with it.")
    return True

def import_excel_data(file_path, model_name):
    """Import data from an Excel file into a model"""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        # Get the model
        model = apps.get_model('cricket_stats', model_name)
        
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Get the field names
        field_names = [field.name for field in model._meta.fields if not field.auto_created]
        
        # Check if all required columns are present
        missing_columns = [col for col in field_names if col not in df.columns and not model._meta.get_field(col).null]
        if missing_columns:
            print(f"Missing required columns: {', '.join(missing_columns)}")
            return False
        
        # Import the data
        records_created = 0
        records_updated = 0
        errors = 0
        
        for _, row in df.iterrows():
            try:
                # Convert row to dict, handling NaN values
                data = {}
                for col in df.columns:
                    if col in field_names:
                        value = row[col]
                        if pd.isna(value):
                            value = None
                        data[col] = value
                
                # Try to get an existing record by ID
                obj_id = data.get('id')
                if obj_id and not pd.isna(obj_id):
                    try:
                        obj = model.objects.get(id=obj_id)
                        # Update existing record
                        for key, value in data.items():
                            setattr(obj, key, value)
                        obj.save()
                        records_updated += 1
                    except model.DoesNotExist:
                        # Create new record with specified ID
                        obj = model.objects.create(**data)
                        records_created += 1
                else:
                    # Create new record without ID
                    if 'id' in data:
                        del data['id']
                    obj = model.objects.create(**data)
                    records_created += 1
            
            except Exception as e:
                print(f"Error importing row: {e}")
                errors += 1
        
        print(f"Import results for {model_name}:")
        print(f"  - Created: {records_created}")
        print(f"  - Updated: {records_updated}")
        print(f"  - Errors: {errors}")
        
        return errors == 0
    
    except Exception as e:
        print(f"Error importing data: {e}")
        return False

def main():
    """Main function"""
    print("=== Ananda Cricket Data Import Tool ===\n")
    
    # Check if import-export is configured
    is_configured = check_import_export_config()
    
    if not is_configured:
        print("\nImport/Export is not fully configured in your admin interface.")
        setup = input("Would you like to set it up now? (y/n): ")
        if setup.lower() == 'y':
            setup_import_export()
    
    # Import data from Excel files
    excel_dir = input("\nEnter the directory containing Excel files (default: excel_templates): ")
    if not excel_dir:
        excel_dir = 'excel_templates'
    
    if not os.path.exists(excel_dir):
        print(f"Directory not found: {excel_dir}")
        return
    
    # Get all Excel files in the directory
    excel_files = [f for f in os.listdir(excel_dir) if f.endswith('.xlsx') or f.endswith('.xls')]
    
    if not excel_files:
        print(f"No Excel files found in {excel_dir}")
        return
    
    print(f"\nFound {len(excel_files)} Excel files:")
    for i, file in enumerate(excel_files):
        print(f"{i+1}. {file}")
    
    # Ask which files to import
    file_indices = input("\nEnter the numbers of the files to import (comma-separated, or 'all'): ")
    
    if file_indices.lower() == 'all':
        files_to_import = excel_files
    else:
        try:
            indices = [int(idx.strip()) - 1 for idx in file_indices.split(',')]
            files_to_import = [excel_files[idx] for idx in indices if 0 <= idx < len(excel_files)]
        except:
            print("Invalid input. Please enter comma-separated numbers.")
            return
    
    # Import the selected files
    print("\nImporting data...")
    for file in files_to_import:
        # Extract model name from filename
        model_name = file.split('_')[0].capitalize()
        if model_name.endswith('.xlsx') or model_name.endswith('.xls'):
            model_name = model_name[:-5]
        
        print(f"\nImporting {file} into {model_name}...")
        import_excel_data(os.path.join(excel_dir, file), model_name)
    
    print("\nImport process completed.")

if __name__ == "__main__":
    main()
