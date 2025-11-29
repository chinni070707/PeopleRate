"""
Natural Language Processing Module for PeopleRate
Processes natural language queries and person descriptions
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime

class NLPProcessor:
    """Advanced NLP processor for parsing natural language search and person creation"""
    
    def __init__(self):
        # Industry keywords mapping
        self.industries = {
            "tech": ["technology", "software", "it", "computer", "digital", "tech", "engineering"],
            "consulting": ["consulting", "consultant", "advisory", "strategy"],
            "healthcare": ["healthcare", "medical", "hospital", "doctor", "physician", "nurse", "clinic"],
            "finance": ["finance", "banking", "investment", "accounting", "financial"],
            "education": ["education", "teacher", "professor", "academic", "university", "school"],
            "retail": ["retail", "sales", "store", "shop", "commerce"],
            "manufacturing": ["manufacturing", "production", "factory", "industrial"],
            "marketing": ["marketing", "advertising", "brand", "digital marketing"],
            "design": ["design", "designer", "ux", "ui", "creative"],
            "data": ["data", "analytics", "data science", "business intelligence"]
        }
        
        # Job title keywords
        self.job_titles = [
            "engineer", "developer", "programmer", "architect", "scientist",
            "manager", "director", "lead", "chief", "head", "vp", "ceo", "cto", "cfo",
            "analyst", "consultant", "specialist", "expert", "professional",
            "designer", "architect", "administrator", "coordinator", "associate",
            "doctor", "physician", "surgeon", "nurse", "therapist",
            "teacher", "professor", "instructor", "educator",
            "accountant", "auditor", "lawyer", "attorney"
        ]
        
        # Location indicators
        self.location_keywords = ["in", "from", "at", "based in", "located in", "works in", "lives in"]
        
        # Company indicators
        self.company_keywords = ["at", "with", "works at", "works for", "employed by", "company"]
        
        # Skills indicators
        self.skill_keywords = ["expert in", "skilled in", "knows", "specializes in", "specialist in"]
        
        # Common Indian cities
        self.indian_cities = [
            "mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata",
            "pune", "ahmedabad", "surat", "jaipur", "lucknow", "kanpur",
            "nagpur", "indore", "thane", "bhopal", "visakhapatnam", "pimpri-chinchwad",
            "patna", "vadodara", "ghaziabad", "ludhiana", "agra", "nashik", "kochi"
        ]
        
        # Common US cities
        self.us_cities = [
            "new york", "los angeles", "chicago", "houston", "phoenix", "philadelphia",
            "san antonio", "san diego", "dallas", "san jose", "austin", "jacksonville",
            "seattle", "denver", "boston", "portland", "san francisco", "miami"
        ]
        
        # Experience indicators
        self.experience_patterns = [
            r"(\d+)\+?\s*years?",
            r"(\d+)\+?\s*yrs?",
            r"over\s+(\d+)\s+years?",
            r"more than\s+(\d+)\s+years?"
        ]
    
    def parse_search_query(self, query: str) -> Dict[str, any]:
        """
        Parse natural language search query into structured search parameters
        
        Example: "sasikala who is into consulting business in Hyderabad"
        Returns: {
            "name": "sasikala",
            "industry": "consulting",
            "city": "hyderabad"
        }
        """
        query_lower = query.lower().strip()
        
        result = {
            "name": None,
            "job_title": None,
            "company": None,
            "industry": None,
            "city": None,
            "state": None,
            "country": None,
            "skills": [],
            "experience_years": None,
            "email": None,
            "phone": None,
            "original_query": query
        }
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query)
        if email_match:
            result["email"] = email_match.group()
            query_lower = query_lower.replace(email_match.group().lower(), "")
        
        # Extract phone
        phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,}', query)
        if phone_match:
            result["phone"] = phone_match.group()
            query_lower = query_lower.replace(phone_match.group(), "")
        
        # Extract name (usually first word or first few words before job/location indicators)
        words = query_lower.split()
        if words:
            # Try to get name (first 1-3 words before keywords)
            name_parts = []
            for i, word in enumerate(words):
                if i >= 3:  # Max 3 words for name
                    break
                if word in ["who", "is", "in", "at", "from", "with", "the", "a", "an"]:
                    break
                # Check if it's not a job title or industry keyword
                is_keyword = False
                for title in self.job_titles:
                    if title in word:
                        is_keyword = True
                        break
                if not is_keyword:
                    name_parts.append(word)
                else:
                    break
            
            if name_parts:
                result["name"] = " ".join(name_parts)
        
        # Extract industry
        for industry, keywords in self.industries.items():
            for keyword in keywords:
                if keyword in query_lower:
                    result["industry"] = industry.capitalize()
                    break
            if result["industry"]:
                break
        
        # Extract job title
        for title in self.job_titles:
            if title in query_lower:
                # Get the full job title context
                pattern = rf'\b[\w\s]*{title}[\w\s]*\b'
                match = re.search(pattern, query_lower)
                if match:
                    result["job_title"] = match.group().strip().title()
                    break
        
        # Extract location (city)
        # Check Indian cities
        for city in self.indian_cities:
            if city in query_lower:
                result["city"] = city.title()
                result["country"] = "India"
                # Try to determine state
                result["state"] = self._get_indian_state(city)
                break
        
        # Check US cities if not found in India
        if not result["city"]:
            for city in self.us_cities:
                if city in query_lower:
                    result["city"] = city.title()
                    result["country"] = "USA"
                    result["state"] = self._get_us_state(city)
                    break
        
        # Generic city extraction if not found
        if not result["city"]:
            for keyword in self.location_keywords:
                if keyword in query_lower:
                    # Get word after location keyword
                    pattern = rf'{keyword}\s+([A-Za-z\s]+?)(?:\s+(?:in|at|with|and|or|who)|$)'
                    match = re.search(pattern, query_lower)
                    if match:
                        city = match.group(1).strip()
                        # Clean up common words
                        city = re.sub(r'\b(who|is|in|at|from|with|the|a|an)\b', '', city).strip()
                        if city and len(city) > 2:
                            result["city"] = city.title()
                            break
        
        # Extract company
        for keyword in self.company_keywords:
            if keyword in query_lower:
                pattern = rf'{keyword}\s+([A-Za-z0-9\s&]+?)(?:\s+(?:in|at|and|or|who)|$)'
                match = re.search(pattern, query_lower)
                if match:
                    company = match.group(1).strip()
                    # Clean up
                    company = re.sub(r'\b(who|is|in|at|from|with|the|a|an)\b', '', company).strip()
                    if company and len(company) > 2:
                        result["company"] = company.title()
                        break
        
        # Extract experience years
        for pattern in self.experience_patterns:
            match = re.search(pattern, query_lower)
            if match:
                result["experience_years"] = int(match.group(1))
                break
        
        # Extract skills
        for keyword in self.skill_keywords:
            if keyword in query_lower:
                pattern = rf'{keyword}\s+([A-Za-z0-9\s,/]+?)(?:\s+(?:in|at|and|or|who)|$)'
                match = re.search(pattern, query_lower)
                if match:
                    skills_str = match.group(1).strip()
                    skills = [s.strip().title() for s in re.split(r'[,/]', skills_str) if s.strip()]
                    result["skills"] = skills
                    break
        
        return result
    
    def parse_person_description(self, description: str) -> Dict[str, any]:
        """
        Parse natural language person description into structured person data
        
        Example: "John Smith is a senior software engineer at Google in Mountain View 
                  with 10 years experience in Python and machine learning. 
                  Email: john@gmail.com, Phone: +1-555-0123"
        
        Returns structured person data
        """
        # Use the same parsing logic as search query
        parsed = self.parse_search_query(description)
        
        # Additional extraction for person creation
        
        # Extract Social Media URLs
        # LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/([\w\-]+)', description.lower())
        if linkedin_match:
            parsed["linkedin_url"] = f"https://linkedin.com/in/{linkedin_match.group(1)}"
        
        # Instagram
        instagram_match = re.search(r'instagram\.com/([\w\.\-]+)', description.lower())
        if instagram_match:
            parsed["instagram_url"] = f"https://instagram.com/{instagram_match.group(1)}"
        
        # Facebook
        facebook_match = re.search(r'facebook\.com/([\w\.\-]+)', description.lower())
        if facebook_match:
            parsed["facebook_url"] = f"https://facebook.com/{facebook_match.group(1)}"
        
        # Twitter/X
        twitter_match = re.search(r'(?:twitter|x)\.com/([\w]+)', description.lower())
        if twitter_match:
            parsed["twitter_url"] = f"https://twitter.com/{twitter_match.group(1)}"
        
        # GitHub
        github_match = re.search(r'github\.com/([\w\-]+)', description.lower())
        if github_match:
            parsed["github_url"] = f"https://github.com/{github_match.group(1)}"
        
        # Website/Personal site
        website_match = re.search(r'(?:website|site|portfolio):\s*(https?://[\w\-\.]+\.[a-z]{2,})', description, re.IGNORECASE)
        if website_match:
            parsed["website_url"] = website_match.group(1)
        
        # Extract bio (if description is long enough)
        if len(description) > 100:
            # Use the original description as bio
            parsed["bio"] = description
        
        # Extract title and role context
        role_patterns = [
            r'(senior|junior|lead|principal|staff|chief|head|director|manager|associate)\s+[\w\s]+',
            r'[\w\s]+\s+(engineer|developer|designer|analyst|consultant|specialist|expert)',
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, description.lower())
            if match and not parsed["job_title"]:
                parsed["job_title"] = match.group().strip().title()
                break
        
        return parsed
    
    def _get_indian_state(self, city: str) -> str:
        """Get Indian state for a city"""
        city_state_map = {
            "mumbai": "Maharashtra",
            "pune": "Maharashtra",
            "delhi": "Delhi",
            "bangalore": "Karnataka",
            "hyderabad": "Telangana",
            "chennai": "Tamil Nadu",
            "kolkata": "West Bengal",
            "ahmedabad": "Gujarat",
            "surat": "Gujarat",
            "jaipur": "Rajasthan",
            "lucknow": "Uttar Pradesh",
            "kanpur": "Uttar Pradesh",
            "nagpur": "Maharashtra",
            "indore": "Madhya Pradesh",
            "bhopal": "Madhya Pradesh",
            "visakhapatnam": "Andhra Pradesh",
            "patna": "Bihar",
            "vadodara": "Gujarat",
            "kochi": "Kerala"
        }
        return city_state_map.get(city.lower(), "")
    
    def _get_us_state(self, city: str) -> str:
        """Get US state for a city"""
        city_state_map = {
            "new york": "NY",
            "los angeles": "CA",
            "chicago": "IL",
            "houston": "TX",
            "phoenix": "AZ",
            "philadelphia": "PA",
            "san antonio": "TX",
            "san diego": "CA",
            "dallas": "TX",
            "san jose": "CA",
            "austin": "TX",
            "jacksonville": "FL",
            "seattle": "WA",
            "denver": "CO",
            "boston": "MA",
            "portland": "OR",
            "san francisco": "CA",
            "miami": "FL"
        }
        return city_state_map.get(city.lower(), "")
    
    def generate_search_score(self, person: Dict, parsed_query: Dict) -> float:
        """
        Generate relevance score for a person based on parsed query
        Higher score = better match
        """
        score = 0.0
        
        # Name match (highest priority)
        if parsed_query.get("name") and person.get("name"):
            name_query = parsed_query["name"].lower()
            name_person = person["name"].lower()
            if name_query in name_person or name_person in name_query:
                score += 100
            elif any(part in name_person for part in name_query.split()):
                score += 50
        
        # Industry match
        if parsed_query.get("industry") and person.get("industry"):
            if parsed_query["industry"].lower() in person["industry"].lower():
                score += 40
        
        # Job title match
        if parsed_query.get("job_title") and person.get("job_title"):
            title_query = parsed_query["job_title"].lower()
            title_person = person["job_title"].lower()
            if title_query in title_person or title_person in title_query:
                score += 35
        
        # City match
        if parsed_query.get("city") and person.get("city"):
            if parsed_query["city"].lower() == person["city"].lower():
                score += 30
        
        # Company match
        if parsed_query.get("company") and person.get("company"):
            if parsed_query["company"].lower() in person["company"].lower():
                score += 25
        
        # Skills match
        if parsed_query.get("skills") and person.get("skills"):
            query_skills = set(s.lower() for s in parsed_query["skills"])
            person_skills = set(s.lower() for s in person["skills"])
            matching_skills = query_skills.intersection(person_skills)
            score += len(matching_skills) * 10
        
        # Experience match (if within range)
        if parsed_query.get("experience_years") and person.get("experience_years"):
            exp_diff = abs(parsed_query["experience_years"] - person["experience_years"])
            if exp_diff <= 2:
                score += 15
        
        # Email/Phone exact match (highest priority)
        if parsed_query.get("email") and person.get("email"):
            if parsed_query["email"].lower() == person["email"].lower():
                score += 150
        
        if parsed_query.get("phone") and person.get("phone"):
            if parsed_query["phone"] in person["phone"]:
                score += 150
        
        # Boost by rating and review count
        score += person.get("average_rating", 0) * 3
        score += min(person.get("review_count", 0), 10) * 2
        
        return score
    
    def extract_person_fields(self, text: str) -> Dict[str, any]:
        """
        Extract person fields from a single natural language description
        This is the main method for "Add Person" functionality
        """
        parsed = self.parse_person_description(text)
        
        # Ensure we have at least a name
        if not parsed.get("name"):
            # Try to extract first capitalized words as name
            words = text.split()
            name_parts = []
            for word in words[:4]:  # Check first 4 words
                if word[0].isupper() and word.lower() not in ["is", "in", "at", "the", "a", "an"]:
                    name_parts.append(word)
                elif name_parts:  # Stop after first lowercase word
                    break
            if name_parts:
                parsed["name"] = " ".join(name_parts)
        
        return parsed

# Create singleton instance
nlp_processor = NLPProcessor()
