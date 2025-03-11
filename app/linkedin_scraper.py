from linkedin_api import Linkedin
import pandas as pd
import time
import os
from datetime import datetime

class LinkedInAlumniScraper:
    def __init__(self, email, password):
        """Initialize LinkedIn API client"""
        self.api = Linkedin(email, password)
        if self.api:
            print("Login successful!")
        self.results = []
        
    def search_alumni(self, school_name="Politeknik Negeri Malang", limit=100):
        """Search for alumni of a specific school and filter by school name in education."""
        try:
            # Step 1: Search for profiles using school name keyword
            search_results = self.api.search_people(
                keywords=school_name,
                limit=limit
            )
            
            # Step 2: Extract profile URLs
            profile_urls = []
            
            for result in search_results:
                if 'urn_id' in result:
                    urn_id = result['urn_id']
                    # Step 3: Fetch detailed profile information using the urn_id
                    profile = self.api.get_profile(urn_id)
                    
                    # Check if the person has attended the specific school
                    if self.verify_alumni(profile):
                        profile_urls.append(urn_id)
                        
            print(f"Found {len(profile_urls)} alumni profiles from {school_name}")
            return profile_urls
            
        except Exception as e:
            print(f"Error during search: {str(e)}")
            return []
    
    def verify_alumni(self, profile):
        """Verify if the profile is actually related to Politeknik Negeri Malang and has graduated"""
        # Check education records
        education = profile.get('education', [])
        
        # Relevant keywords for the school
        relevant_keywords = ['politeknik negeri malang', 'polinema']
        
        # Iterate through education history to find relevant education and graduation status
        for school in education:
            school_name = (school.get('schoolName', '') or '').lower()
            
            # Check if the school name matches "Politeknik Negeri Malang" or "Polinema"
            if any(keyword in school_name for keyword in relevant_keywords):
                # Check if the person has an end date (graduation year)
                time_period = school.get('timePeriod', {})
                end_date = time_period.get('endDate', {})
                graduation_year = end_date.get('year')
                
                # If there's a graduation year, verify it's in the past
                if graduation_year and graduation_year < 2025:
                    return True  # The person has graduated
                
        return False  # No relevant graduation found
    
    def get_profile_data(self, profile_id):
        """Extract basic profile data using limited API access"""
        try:
            # Get basic profile data
            profile = self.api.get_profile(profile_id)
            
            # Verify if actually an alumni
            if not self.verify_alumni(profile):
                return None
            
            # Extract available information
            data = {
                'name': f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip(),
                'current_company': None,
                'current_title': None,
                'graduation_year': None
            }
            
            # Extract current position if available
            experience = profile.get('experience', [])
            if experience:
                current_job = experience[0]  # Most recent position
                data['current_company'] = current_job.get('companyName', '')
                data['current_title'] = current_job.get('title', '')
            
            # Try to get graduation year
            education = profile.get('education', [])
            for edu in education:
                if 'Politeknik Negeri Malang' in (edu.get('schoolName', '') or ''):
                    if 'timePeriod' in edu and 'endDate' in edu['timePeriod']:
                        graduation_year = edu['timePeriod']['endDate'].get('year')
                        if graduation_year and graduation_year < 2025:
                            data['graduation_year'] = graduation_year
                        else:
                            return None  # Skip if still a student (graduation year >= 2025)
                    break   
            
            return data
            
        except Exception as e:
            print(f"Error processing {profile_id}: {str(e)}")
            return None
    
    def scrape_alumni(self, limit=100, delay=2):
        """Main function to search and scrape alumni data"""
        print("Searching for Politeknik Negeri Malang alumni...")
        profile_ids = self.search_alumni("Politeknik Negeri Malang", limit)
        
        print(f"Processing {len(profile_ids)} profiles...")
        for profile_id in profile_ids:
            try:
                profile_data = self.get_profile_data(profile_id)
                
                if profile_data:
                    self.results.append(profile_data)
                    print(f"Successfully processed profile: {profile_data['name']}")
                
                # Wait between requests to respect rate limits
                time.sleep(delay)
                
            except Exception as e:
                print(f"Failed to process {profile_id}: {str(e)}")
                time.sleep(delay * 2)  # Wait longer after an error
                continue
    
    def save_results(self, filename=None):
        """Save results to CSV file"""
        if not filename:
            # timestamp = datetime.now().strftime('%d_%m_%Y_%H%M')
            filename = f'polinema_alumni.csv'
            
        df = pd.DataFrame(self.results)
        df.to_csv(filename, index=False)
        print(f"Data saved to {filename}")
        print(f"Total alumni profiles collected: {len(self.results)}")
        return df

def load_credentials(config_path='app/config/credentials.txt'):
    """Load LinkedIn credentials from a config file"""
    try:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Credentials file not found at {config_path}")
            
        with open(config_path, 'r') as file:
            lines = file.readlines()
            if len(lines) < 2:
                raise ValueError("Credentials file must contain email on first line and password on second line")
                
            email = lines[0].strip()
            password = lines[1].strip()
            
            return email, password
    except Exception as e:
        print(f"Error loading credentials: {str(e)}")
        return None, None
    
# Example usage
if __name__ == "__main__":
    # Load credentials from file
    email, password = load_credentials()
    
    if email and password:
        # Initialize scraper
        scraper = LinkedInAlumniScraper(
            email=email,
            password=password
        )
        
        # Start scraping (default limit is 100, can be changed)
        scraper.scrape_alumni(limit=100)
        
        # Save results
        df = scraper.save_results()
    else:
        print("Failed to load credentials. Please check your credentials file.")

