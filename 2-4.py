import pandas as pd
import json
import os
import re
import numpy as np
from datetime import datetime

def load_car_data():
    """Load the car data from CSV file"""
    try:
        if not os.path.exists('otomoto_cars.csv'):
            print("Error: otomoto_cars.csv file not found!")
            return None
        
        # Load CSV with correct data types - both columns should be strings
        df = pd.read_csv('otomoto_cars.csv', dtype={'url': str, 'raw_json': str})
        print(f"Loaded {len(df)} records from otomoto_cars.csv")
        print(f"Data types: {df.dtypes}")
        return df
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None

def extract_field(advert, field, default=None):
    return advert.get(field, default)

def clean_html_tags(text):
    """Remove HTML tags from text and add proper spacing"""
    if not text:
        return text
    # Remove HTML tags and replace with spaces
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    # Remove extra whitespace and normalize to single spaces
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    return clean_text

def extract_details(advert, key):
    """Extract details from the details array"""
    details = advert.get('details', [])
    for detail in details:
        if detail.get('key') == key:
            return detail.get('value')
    return None

def extract_equipment_by_category(advert):
    """Extract equipment organized by category"""
    equipment_dict = {}
    equipment = advert.get('equipment', [])
    for eq_group in equipment:
        category = eq_group.get('label', 'Unknown')
        values = eq_group.get('values', [])
        features = []
        for value in values:
            label = value.get('label')
            if label:
                features.append(label)
        equipment_dict[category] = features
    return equipment_dict

def convert_to_string(value):
    """Convert any value to string, handling None, NaN, and special cases"""
    if value is None or pd.isna(value):
        return ""
    elif isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False)
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        # Handle numeric values - convert to string but preserve the number
        if pd.isna(value) or value == float('inf') or value == float('-inf'):
            return ""
        return str(value)
    else:
        return str(value)

def parse_json_fields(df):
    if df is None or df.empty:
        print("No data to process!")
        return None
    
    records = []
    for idx, row in df.iterrows():
        url = row['url']
        raw_json = row['raw_json']
        record = {'Listing URL': convert_to_string(url)}
        
        if pd.notna(raw_json) and raw_json:
            try:
                json_data = json.loads(raw_json)
                advert = json_data.get('advert', {})
                
                # Basic listing information
                record['Title'] = convert_to_string(extract_field(advert, 'title'))
                record['Description'] = convert_to_string(clean_html_tags(extract_field(advert, 'description')))
                
                # Price information
                price_data = advert.get('price', {})
                record['Price'] = convert_to_string(price_data.get('value') or price_data.get('amount'))
                record['Currency'] = convert_to_string(price_data.get('currency'))
                
                # Seller information
                seller_data = advert.get('seller', {})
                record['Seller Type'] = convert_to_string(seller_data.get('type'))
                
                record['Country_Origin'] = convert_to_string(extract_details(advert, 'country_origin'))
                
                # Extract car specifications using actual field names
                record['Make'] = convert_to_string(extract_details(advert, 'make'))
                record['Model'] = convert_to_string(extract_details(advert, 'model'))
                record['Generation'] = convert_to_string(extract_details(advert, 'generation'))
                record['Version'] = convert_to_string(extract_details(advert, 'version'))
                record['Body_Type'] = convert_to_string(extract_details(advert, 'body_type'))
                record['Fuel_Type'] = convert_to_string(extract_details(advert, 'fuel_type'))
                record['Gearbox'] = convert_to_string(extract_details(advert, 'gearbox'))
                record['Transmission'] = convert_to_string(extract_details(advert, 'transmission'))
                record['Color'] = convert_to_string(extract_details(advert, 'color'))
                record['Color_Type'] = convert_to_string(extract_details(advert, 'colour_type'))
                record['Year_Production'] = convert_to_string(extract_details(advert, 'year'))
                record['Mileage'] = convert_to_string(extract_details(advert, 'mileage'))
                record['Number_Doors'] = convert_to_string(extract_details(advert, 'door_count'))
                record['Number_Seats'] = convert_to_string(extract_details(advert, 'nr_seats'))
                record['Engine_Capacity'] = convert_to_string(extract_details(advert, 'engine_capacity'))
                record['Engine_Power'] = convert_to_string(extract_details(advert, 'engine_power'))
                
                # Vehicle history and condition
                record['No_Accidents'] = convert_to_string(extract_details(advert, 'no_accident'))
                record['Has_Registration'] = convert_to_string(extract_details(advert, 'has_registration'))
                record['Service_Record'] = convert_to_string(extract_details(advert, 'service_record'))
                record['New_Used'] = convert_to_string(extract_details(advert, 'new_used'))
                
                # Additional details
                record['CO2_Emissions'] = convert_to_string(extract_details(advert, 'co2_emissions'))
                record['Urban_Consumption'] = convert_to_string(extract_details(advert, 'urban_consumption'))
                record['Detail_registered'] = convert_to_string(extract_details(advert, 'registered'))
                record['Detail_original_owner'] = convert_to_string(extract_details(advert, 'original_owner'))
                
                # Parameters
                parameters = advert.get('parametersDict', {})
                record['Is_Imported'] = convert_to_string(parameters.get('is_imported_car', {}).get('values', [{}])[0].get('label', ''))
                record['Param_catalog_urn'] = convert_to_string(parameters.get('catalog_urn', {}).get('values', [{}])[0].get('label', ''))
                record['Param_damaged'] = convert_to_string(parameters.get('damaged', {}).get('values', [{}])[0].get('label', ''))
                record['Param_historical_vehicle'] = convert_to_string(parameters.get('historical_vehicle', {}).get('values', [{}])[0].get('label', ''))
                
                # Equipment by category
                equipment_dict = extract_equipment_by_category(advert)
                for category, features in equipment_dict.items():
                    if features:  # Only add if there are features
                        record[f'Equipment_{category}'] = convert_to_string(json.dumps(features, ensure_ascii=False))
                
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
        records.append(record)
    
    # Create DataFrame
    df_result = pd.DataFrame(records)
    
    # Ensure all columns are string type
    for col in df_result.columns:
        df_result[col] = df_result[col].astype(str)
        df_result[col] = df_result[col].replace(['nan', 'None', 'null'], '')
    
    return df_result

def clean_numeric_column(series, suffix, target_type='int'):
    """Clean numeric column by removing suffix and converting to target type"""
    if series.dtype == 'object':
        series_clean = series.fillna('0')
        cleaned = series_clean.astype(str).str.replace(suffix, '', regex=False)
        cleaned = cleaned.str.replace(' ', '', regex=False)
        cleaned = cleaned.str.replace(',', '', regex=False)
        cleaned = cleaned.str.replace('nan', '0', regex=False)
        
        numeric_series = pd.to_numeric(cleaned, errors='coerce')
        
        if target_type == 'int':
            numeric_series = numeric_series.fillna(0).astype('int64')
            return numeric_series
        elif target_type == 'float':
            return numeric_series.astype('float64')
    else:
        if target_type == 'int':
            filled_series = series.fillna(0)
            return filled_series.astype('int64')
        elif target_type == 'float':
            return series.astype('float64')
    return series

def create_cars_subset(df):
    """Create cars_subset with selected columns and processing"""
    print("Creating cars_subset with selected columns...")
    
    # Define the columns we want (matching the notebook)
    selected_columns = [
        'Listing URL', 'Make', 'Model', 'Body_Type',
        'Fuel_Type', 'Gearbox', 'Transmission', 'Year_Production', 'Mileage', 
        'Engine_Capacity', 'Engine_Power', 'No_Accidents',
        'Service_Record', 'New_Used', 
         'Is_Imported', 'Param_catalog_urn', 'Param_damaged',
        'Detail_original_owner', 
        'Seller Type', 'Equipment_Audio i multimedia', 'Equipment_Komfort i dodatki',
        'Equipment_Systemy wspomagania kierowcy', 'Equipment_Osiągi i tuning',
        'Equipment_Bezpieczeństwo', 'Title', 'Description', 'Price', 'Currency'
    ]
    
    # Check which columns exist
    existing_columns = [col for col in selected_columns if col in df.columns]
    missing_columns = [col for col in selected_columns if col not in df.columns]
    
    print(f"Selected columns that exist: {len(existing_columns)}")
    if missing_columns:
        print(f"Missing columns: {missing_columns}")
    
    # Create subset with existing columns only
    cars_subset = df[existing_columns].copy()
    print(f"cars_subset shape: {cars_subset.shape}")
    
    # Handle duplicate Has_Registration columns
    has_reg_columns = [col for col in cars_subset.columns if 'Has_Registration' in col or 'Has Registration' in col]
    if len(has_reg_columns) > 1:
        for col in has_reg_columns[1:]:
            cars_subset = cars_subset.drop(columns=[col])
    
    # Rename columns
    rename_mapping = {
        'Listing URL': 'Listing_URL',
        'Year_Production': 'Year',
        'Detail_original_owner': 'First_Owner',
        'Seller Type': 'Seller_Type',
        'Equipment_Audio i multimedia': 'Equipment_Audio_and_Multimedia',
        'Equipment_Komfort i dodatki': 'Equipment_Comfort_and_Extras',
        'Equipment_Systemy wspomagania kierowcy': 'Equipment_Driver_Assistance_Systems',
        'Equipment_Osiągi i tuning': 'Equipment_Performance_and_Tuning',
        'Equipment_Bezpieczeństwo': 'Equipment_Safety'
    }
    
    existing_rename_columns = {old: new for old, new in rename_mapping.items() if old in cars_subset.columns}
    cars_subset = cars_subset.rename(columns=existing_rename_columns)
    
    # Convert data types
    print("Converting data types...")
    
    # Convert Year to int
    year_col = 'Year' if 'Year' in cars_subset.columns else 'Year_Production'
    if year_col in cars_subset.columns:
        cars_subset[year_col] = pd.to_numeric(cars_subset[year_col], errors='coerce').fillna(0).astype('int')
    
    # Convert Price to numeric and handle currency conversion
    if 'Price' in cars_subset.columns:
        cars_subset['Price'] = pd.to_numeric(cars_subset['Price'], errors='coerce').fillna(0)
        
        # Convert EUR to PLN if Currency column exists
        if 'Currency' in cars_subset.columns:
            # Convert EUR prices to PLN using exchange rate 1 EUR = 4.2509 PLN
            eur_mask = cars_subset['Currency'].str.upper() == 'EUR'
            cars_subset.loc[eur_mask, 'Price'] = cars_subset.loc[eur_mask, 'Price'] * 4.2509
            print(f"Converted {eur_mask.sum()} EUR prices to PLN")
        
        # Convert to int after currency conversion
        cars_subset['Price'] = cars_subset['Price'].astype('int')
        
        price_null_count = cars_subset['Price'].isnull().sum()
        if price_null_count > 0:
            cars_subset = cars_subset.dropna(subset=['Price'])
            print(f"Dropped {price_null_count} rows with null Price")
    
    # Clean numeric columns
    if 'Engine_Capacity' in cars_subset.columns:
        cars_subset['Engine_Capacity'] = clean_numeric_column(cars_subset['Engine_Capacity'], ' cm3', 'int')
    
    if 'Engine_Power' in cars_subset.columns:
        cars_subset['Engine_Power'] = clean_numeric_column(cars_subset['Engine_Power'], ' KM', 'int')
    
    if 'Mileage' in cars_subset.columns:
        cars_subset['Mileage'] = clean_numeric_column(cars_subset['Mileage'], ' km', 'int')
    
    # Concatenate Title and Description into Full_Description
    if 'Title' in cars_subset.columns and 'Description' in cars_subset.columns:
        # Fill NaN values with empty strings to avoid concatenation issues
        title_filled = cars_subset['Title'].fillna('')
        description_filled = cars_subset['Description'].fillna('')
        
        # Concatenate with space separator
        cars_subset['Full_Description'] = title_filled + ' ' + description_filled
        
        # Remove extra whitespace
        cars_subset['Full_Description'] = cars_subset['Full_Description'].str.strip()
        
        print(f"Created Full_Description column from Title and Description")
        
        # Reorder columns to place Full_Description after Seller_Type
        if 'Seller_Type' in cars_subset.columns:
            # Get current column order
            cols = list(cars_subset.columns)
            # Remove Full_Description from its current position
            cols.remove('Full_Description')
            # Find Seller_Type position and insert Full_Description after it
            seller_type_idx = cols.index('Seller_Type')
            cols.insert(seller_type_idx + 1, 'Full_Description')
            # Reorder the DataFrame
            cars_subset = cars_subset[cols]
            print(f"Repositioned Full_Description column after Seller_Type")
    

    # Filter to drop damaged vehicles (Param_damaged == "Tak")
    if 'Param_damaged' in cars_subset.columns:
        initial_count = len(cars_subset)
        # Drop rows where Param_damaged is "Tak" (damaged vehicles)
        cars_subset = cars_subset[cars_subset['Param_damaged'] != 'Tak']
        filtered_count = len(cars_subset)
        print(f"Filtered dataset: dropped vehicles with Param_damaged == 'Tak', kept {filtered_count} vehicles out of {initial_count} total vehicles")
    
    # Filter to keep only used vehicles (New_Used == "Używany")
    if 'New_Used' in cars_subset.columns:
        initial_count = len(cars_subset)
        cars_subset = cars_subset[cars_subset['New_Used'] == 'Używany']
        filtered_count = len(cars_subset)
        print(f"Filtered dataset: kept {filtered_count} used vehicles out of {initial_count} total vehicles")
    
    # Final column drops (matching the notebook)
    cars_subset = cars_subset.drop(columns=['Param_catalog_urn', 'CO2_Emissions', 'Urban_Consumption', 'Currency', 'Title', 'Description', 'Param_damaged', 'New_Used'], errors='ignore')
    
    print(f"Final cars_subset shape: {cars_subset.shape}")
    return cars_subset

def save_processed_data(df, filename='otomoto_cars_parsed.csv'):
    try:
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Processed data saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving processed data: {e}")
        return False

def main():
    print("Starting car data parsing and processing pipeline...")
    print("=" * 60)
    
    # Step 1: Load and parse raw data
    df = load_car_data()
    if df is None:
        return
    
    print(f"Processing {len(df)} records...")
    parsed_df = parse_json_fields(df)
    if parsed_df is None:
        print("Failed to parse data!")
        return
    
    print(f"Parsed data shape: {parsed_df.shape}")
    print(f"Total columns extracted: {len(parsed_df.columns)}")
    
    # Step 2: Create cars_subset (matching the notebook approach)
    cars_subset = create_cars_subset(parsed_df)
    
    # Step 3: Save the final processed data
    success = save_processed_data(cars_subset, 'otomoto_cars_parsed.csv')
    
    if success:
        print("\n" + "=" * 60)
        print("Simplified data pipeline completed successfully!")
        print(f"Original records: {len(df)}")
        print(f"Final processed records: {len(cars_subset)}")
        print(f"Final columns: {len(cars_subset.columns)}")
        print(f"Output file: otomoto_cars_parsed.csv")
        
        # Show final data info
        print(f"\nFinal data types:")
        print(cars_subset.dtypes.value_counts())
        
        print(f"\nSample columns: {list(cars_subset.columns[:10])}")
    else:
        print("\nData processing failed!")

if __name__ == "__main__":
    main()
