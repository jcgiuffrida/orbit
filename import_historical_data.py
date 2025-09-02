#!/usr/bin/env python
"""
Historical Data Import Script for Orbit

This script imports data from the previous version's CSV files:
- seeds_person.csv
- seeds_conversation.csv 
- seeds_conversation_people.csv
- seeds_company.csv

Run this script within a Django shell:
python manage.py shell
exec(open('import_historical_data.py').read())
"""

import pandas as pd
import os
from datetime import datetime
from django.contrib.auth.models import User
from orbit.models import Person, Conversation, ContactAttempt, Relationship

def parse_birthday(birthday_str):
    """Parse birthday string and return month, day, year components"""
    if not birthday_str or pd.isna(birthday_str):
        return None, None, None
    
    try:
        # Handle format like "11/9/88"
        if isinstance(birthday_str, str):
            # Try different date formats
            for fmt in ['%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']:
                try:
                    date_obj = datetime.strptime(birthday_str.strip(), fmt)
                    # Handle 2-digit years (assume 1900s if > 50, 2000s if <= 50)
                    if date_obj.year < 1950:
                        date_obj = date_obj.replace(year=date_obj.year + 100)
                    return date_obj.month, date_obj.day, date_obj.year
                except ValueError:
                    continue
        print(f"Warning: Could not parse birthday: {birthday_str}")
        return None, None, None
    except Exception as e:
        print(f"Error parsing birthday '{birthday_str}': {e}")
        return None, None, None

def map_conversation_type(mode):
    """Map old conversation mode to new type"""
    mode_mapping = {
        'one on one': 'in_person',
        'in group': 'in_person',  # Assume group meetings are in person
        'phone': 'phone',
        'text': 'text',
        'email': 'email',
        'skype': 'video',  # Skype is video call
    }
    
    if pd.isna(mode) or not mode:
        return 'other'
    
    mode_lower = str(mode).lower().strip()
    return mode_mapping.get(mode_lower, 'other')

def map_contact_attempt_type(mode):
    """Map old conversation mode to contact attempt type"""
    mode_mapping = {
        'phone': 'call',
        'text': 'text', 
        'email': 'email',
        'social': 'social',
        'facebook': 'social',
        'instagram': 'social',
        'twitter': 'social',
        'linkedin': 'social',
    }
    
    if pd.isna(mode) or not mode:
        return 'other'
    
    mode_lower = str(mode).lower().strip()
    return mode_mapping.get(mode_lower, 'other')

def import_historical_data():
    """Main import function"""
    
    # File paths (assuming they're in the project root)
    base_path = '.'
    
    person_file = os.path.join(base_path, 'seeds_person.csv')
    conversation_file = os.path.join(base_path, 'seeds_conversation.csv')
    conv_people_file = os.path.join(base_path, 'seeds_conversation_people.csv')
    company_file = os.path.join(base_path, 'seeds_company.csv')
    
    # Check if files exist
    missing_files = []
    for file_path, name in [(person_file, 'seeds_person.csv'),
                           (conversation_file, 'seeds_conversation.csv'),
                           (conv_people_file, 'seeds_conversation_people.csv'),
                           (company_file, 'seeds_company.csv')]:
        if not os.path.exists(file_path):
            missing_files.append(name)
    
    if missing_files:
        print(f"Missing files: {', '.join(missing_files)}")
        print(f"Please ensure these files are in: {base_path}")
        return
    
    print("Starting historical data import...")
    
    # Get or create a default user for created_by fields
    try:
        default_user = User.objects.get(id=1)
    except User.DoesNotExist:
        default_user = User.objects.first()
        if not default_user:
            print("Error: No users found in database. Please create a user first.")
            return
    
    print(f"Using user '{default_user.username}' for created_by fields")
    
    # 1. Load and process companies first (for company names)
    print("\n1. Loading companies...")
    companies_df = pd.read_csv(company_file)
    print(f"Found {len(companies_df)} companies")
    
    # Create company name mapping
    company_mapping = {}
    for _, row in companies_df.iterrows():
        if not pd.isna(row['name']):
            company_mapping[row['id']] = row['name'].strip()
    
    # 2. Load and process people
    print("\n2. Loading people...")
    people_df = pd.read_csv(person_file)
    print(f"Found {len(people_df)} people")
    
    # Track old_id -> new Person mapping for relationships
    person_id_mapping = {}
    partner_relationships = []  # Store partner relationships for later
    friend_relationships = []   # Store friend relationships for later
    
    people_created = 0
    for _, row in people_df.iterrows():
        try:
            # Skip inactive records
            if row.get('active', 1) == 0:
                continue
                
            # Combine first and last name
            first_name = str(row.get('first_name', '')).strip() if not pd.isna(row.get('first_name')) else ''
            last_name = str(row.get('last_name', '')).strip() if not pd.isna(row.get('last_name')) else ''
            
            if not first_name and not last_name:
                print(f"Skipping person with no name: {row.get('id')}")
                continue
                
            name = f"{first_name} {last_name}".strip()
            
            # Parse birthday
            birthday_month, birthday_day, birth_year = parse_birthday(row.get('birthday'))
            
            # Get company name
            company_name = ''
            if not pd.isna(row.get('company_id')) and row.get('company_id') in company_mapping:
                company_name = company_mapping[row.get('company_id')]
            
            # Create person
            person = Person.objects.create(
                name=name,
                name_ext='',  # No equivalent field in old data
                email='',  # No email in old data
                phone='',  # No phone in old data  
                location=str(row.get('city', '')).strip() if not pd.isna(row.get('city')) else '',
                address=str(row.get('address', '')).strip() if not pd.isna(row.get('address')) else '',
                company=company_name,
                birthday_month=birthday_month,
                birthday_day=birthday_day,
                birth_year=birth_year,
                how_we_met='',  # No equivalent field
                notes=str(row.get('notes', '')).strip() if not pd.isna(row.get('notes')) else '',
                ai_summary='',  # New field
                created_by=default_user
            )
            
            person_id_mapping[row['id']] = person
            people_created += 1
            
            # Store relationships for later processing
            if not pd.isna(row.get('partner_id')):
                partner_relationships.append((row['id'], row['partner_id']))
            
            if not pd.isna(row.get('known_via_id')):
                friend_relationships.append((row['id'], row['known_via_id']))
                
        except Exception as e:
            print(f"Error creating person {row.get('id')}: {e}")
    
    print(f"Created {people_created} people")
    
    # 3. Create relationships
    print("\n3. Creating relationships...")
    
    # Partner relationships
    partners_created = 0
    for person1_old_id, person2_old_id in partner_relationships:
        try:
            if person1_old_id in person_id_mapping and person2_old_id in person_id_mapping:
                person1 = person_id_mapping[person1_old_id]
                person2 = person_id_mapping[person2_old_id]
                
                # Avoid duplicate relationships
                if not Relationship.objects.filter(
                    person1=person1, person2=person2
                ).exists() and not Relationship.objects.filter(
                    person1=person2, person2=person1
                ).exists():
                    Relationship.objects.create(
                        person1=person1,
                        person2=person2,
                        relationship_type='partner',
                        description='Imported from historical data',
                        created_by=default_user
                    )
                    partners_created += 1
        except Exception as e:
            print(f"Error creating partner relationship: {e}")
    
    # Friend relationships (known_via)
    friends_created = 0
    for person1_old_id, person2_old_id in friend_relationships:
        try:
            if person1_old_id in person_id_mapping and person2_old_id in person_id_mapping:
                person1 = person_id_mapping[person1_old_id]
                person2 = person_id_mapping[person2_old_id]
                
                # Avoid duplicate relationships
                if not Relationship.objects.filter(
                    person1=person1, person2=person2
                ).exists() and not Relationship.objects.filter(
                    person1=person2, person2=person1
                ).exists():
                    Relationship.objects.create(
                        person1=person1,
                        person2=person2,
                        relationship_type='friend',
                        description='Known via (imported from historical data)',
                        created_by=default_user
                    )
                    friends_created += 1
        except Exception as e:
            print(f"Error creating friend relationship: {e}")
    
    print(f"Created {partners_created} partner relationships")
    print(f"Created {friends_created} friend relationships")
    
    # 4. Load conversations and contact attempts
    print("\n4. Loading conversations and contact attempts...")
    conversations_df = pd.read_csv(conversation_file)
    conversation_people_df = pd.read_csv(conv_people_file)
    
    print(f"Found {len(conversations_df)} conversation records")
    
    conversations_created = 0
    contact_attempts_created = 0
    
    for _, row in conversations_df.iterrows():
        try:
            # Skip inactive records
            if row.get('active', 1) == 0:
                continue
            
            # Parse date
            date_str = str(row.get('date', '')).strip()
            if not date_str or pd.isna(row.get('date')):
                print(f"Skipping record {row.get('id')} - no date")
                continue
            
            # Try to parse the date
            record_date = None
            for fmt in ['%m/%d/%y', '%m/%d/%Y', '%Y-%m-%d']:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    # Handle 2-digit years
                    if date_obj.year < 1950:
                        date_obj = date_obj.replace(year=date_obj.year + 100)
                    record_date = date_obj.date()
                    break
                except ValueError:
                    continue
            
            if not record_date:
                print(f"Could not parse date '{date_str}' for record {row.get('id')}")
                continue
            
            # Combine summary and notes
            summary = str(row.get('summary', '')).strip() if not pd.isna(row.get('summary')) else ''
            notes = str(row.get('notes', '')).strip() if not pd.isna(row.get('notes')) else ''
            
            combined_notes = summary
            if summary and notes:
                combined_notes = f"{summary}\n\n{notes}"
            elif notes:
                combined_notes = notes
            
            # Check if this should be a contact attempt (seed == 1)
            is_contact_attempt = row.get('seed', 0) == 1
            
            if is_contact_attempt:
                # Create contact attempt(s) - one per participant
                participants = conversation_people_df[
                    conversation_people_df['conversation_id'] == row['id']
                ]
                
                attempt_type = map_contact_attempt_type(row.get('mode'))
                
                for _, participant_row in participants.iterrows():
                    old_person_id = participant_row['person_id']
                    if old_person_id in person_id_mapping:
                        person = person_id_mapping[old_person_id]
                        
                        ContactAttempt.objects.create(
                            person=person,
                            date=record_date,
                            type=attempt_type,
                            notes=combined_notes or 'Imported contact attempt',
                            led_to_conversation=False,  # Since it's marked as seed=1
                            private=False,
                            created_by=default_user
                        )
                        contact_attempts_created += 1
            
            else:
                # Create conversation
                conversation_type = map_conversation_type(row.get('mode'))
                
                if not combined_notes:
                    combined_notes = 'Imported conversation'
                
                conversation = Conversation.objects.create(
                    date=record_date,
                    type=conversation_type,
                    location=str(row.get('location', '')).strip() if not pd.isna(row.get('location')) else '',
                    notes=combined_notes,
                    private=False,  # Assume historical conversations are not private
                    created_by=default_user
                )
                
                # Add participants
                participants_added = 0
                conversation_participants = conversation_people_df[
                    conversation_people_df['conversation_id'] == row['id']
                ]
                
                for _, participant_row in conversation_participants.iterrows():
                    old_person_id = participant_row['person_id']
                    if old_person_id in person_id_mapping:
                        person = person_id_mapping[old_person_id]
                        conversation.participants.add(person)
                        participants_added += 1
                
                if participants_added > 0:
                    conversations_created += 1
                else:
                    # Delete conversation if no participants could be added
                    conversation.delete()
                    print(f"Deleted conversation {row.get('id')} - no valid participants")
                
        except Exception as e:
            print(f"Error creating record {row.get('id')}: {e}")
    
    print(f"Created {conversations_created} conversations")
    print(f"Created {contact_attempts_created} contact attempts")
    
    # 5. Summary
    print("\n" + "="*50)
    print("IMPORT SUMMARY")
    print("="*50)
    print(f"People created: {people_created}")
    print(f"Partner relationships: {partners_created}")
    print(f"Friend relationships: {friends_created}")
    print(f"Conversations created: {conversations_created}")
    print(f"Contact attempts created: {contact_attempts_created}")
    print("\nImport completed successfully!")
    
    return {
        'people_created': people_created,
        'partners_created': partners_created,
        'friends_created': friends_created,
        'conversations_created': conversations_created,
        'contact_attempts_created': contact_attempts_created
    }

# Run the import
if __name__ == "__main__":
    print("This script should be run within Django shell:")
    print("python manage.py shell")
    print("exec(open('import_historical_data.py').read())")
else:
    # Running within Django shell
    try:
        import_historical_data()
    except Exception as e:
        print(f"Import failed: {e}")
        import traceback
        traceback.print_exc()