"""
Generate 50 Diverse Sample Users for Testing
Simulates realistic user base across industries, roles, and locations
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from datetime import datetime, timedelta
import random

# Sample data pools for diversity
FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Emily", "Frank", "Grace", "Henry", "Iris", "Jack",
    "Karen", "Leo", "Maria", "Nathan", "Olivia", "Peter", "Quinn", "Rachel", "Sam", "Tara",
    "Uma", "Victor", "Wendy", "Xavier", "Yara", "Zoe", "Aiden", "Bella", "Connor", "Diana",
    "Ethan", "Fiona", "George", "Hannah", "Isaac", "Julia", "Kevin", "Luna", "Mason", "Nina",
    "Oscar", "Penny", "Quincy", "Ruby", "Sean", "Tina", "Ulysses", "Vera", "Wade", "Xena"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"
]

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Apple", "Meta", "Netflix", "Tesla", "SpaceX",
    "Salesforce", "Oracle", "Adobe", "IBM", "Intel", "Cisco", "VMware", "Dell",
    "McKinsey", "BCG", "Deloitte", "PwC", "EY", "KPMG", "Accenture", "Bain",
    "Goldman Sachs", "JPMorgan", "Morgan Stanley", "Bank of America", "Wells Fargo", "Citi",
    "Johnson & Johnson", "Pfizer", "Merck", "Bristol Myers", "Abbott", "Medtronic",
    "Harvard University", "Stanford University", "MIT", "Yale", "Princeton", "Columbia",
    "SpaceX", "Blue Origin", "Rivian", "Cruise", "Waymo", "Unity", "Epic Games", "Roblox"
]

JOB_TITLES = [
    "Software Engineer", "Senior Software Engineer", "Staff Engineer", "Principal Engineer",
    "Product Manager", "Senior Product Manager", "Director of Product", "VP Product",
    "Data Scientist", "Senior Data Scientist", "ML Engineer", "AI Research Scientist",
    "UX Designer", "Senior UX Designer", "Design Director", "Creative Director",
    "Engineering Manager", "Director of Engineering", "VP Engineering", "CTO",
    "Sales Manager", "Account Executive", "VP Sales", "Chief Revenue Officer",
    "Marketing Manager", "Director of Marketing", "CMO", "Brand Manager",
    "HR Manager", "Director of People Operations", "CHRO", "Talent Acquisition Lead",
    "Financial Analyst", "Finance Manager", "CFO", "Investment Banker",
    "Consultant", "Senior Consultant", "Principal Consultant", "Partner",
    "DevOps Engineer", "Site Reliability Engineer", "Cloud Architect", "Security Engineer",
    "Project Manager", "Program Manager", "Scrum Master", "Agile Coach",
    "Business Analyst", "Strategy Consultant", "Operations Manager", "CEO"
]

INDUSTRIES = [
    "Technology", "Software", "Internet", "Cloud Computing", "AI/ML",
    "Consulting", "Management Consulting", "Strategy", "Financial Services",
    "Healthcare", "Medical", "Pharmaceuticals", "Biotechnology",
    "Education", "Higher Education", "E-Learning", "EdTech",
    "Finance", "Banking", "Investment", "Venture Capital",
    "Retail", "E-commerce", "Consumer Goods", "Fashion",
    "Media", "Entertainment", "Gaming", "Streaming",
    "Real Estate", "Construction", "Manufacturing", "Automotive"
]

CITIES = [
    ("San Francisco", "CA"), ("Seattle", "WA"), ("New York", "NY"), ("Boston", "MA"),
    ("Austin", "TX"), ("Denver", "CO"), ("Los Angeles", "CA"), ("San Diego", "CA"),
    ("Portland", "OR"), ("Chicago", "IL"), ("Atlanta", "GA"), ("Miami", "FL"),
    ("Dallas", "TX"), ("Houston", "TX"), ("Phoenix", "AZ"), ("Detroit", "MI"),
    ("Philadelphia", "PA"), ("Washington", "DC"), ("Nashville", "TN"), ("Charlotte", "NC"),
    ("Raleigh", "NC"), ("Salt Lake City", "UT"), ("Minneapolis", "MN"), ("Pittsburgh", "PA"),
    ("Boulder", "CO"), ("Palo Alto", "CA"), ("Mountain View", "CA"), ("Cupertino", "CA"),
    ("Redmond", "WA"), ("Cambridge", "MA"), ("Arlington", "VA"), ("San Jose", "CA")
]

SKILLS_BY_ROLE = {
    "engineer": ["Python", "Java", "JavaScript", "React", "Node.js", "AWS", "Docker", "Kubernetes", "SQL", "Git", "TypeScript", "Go"],
    "product": ["Product Strategy", "User Research", "Data Analysis", "Agile", "Roadmapping", "SQL", "Figma", "Jira", "Scrum", "Metrics"],
    "data": ["Python", "SQL", "Machine Learning", "TensorFlow", "PyTorch", "Statistics", "Data Visualization", "Spark", "R", "Tableau"],
    "design": ["Figma", "Sketch", "Adobe XD", "Prototyping", "User Research", "Design Systems", "Accessibility", "Illustrator", "Animation"],
    "business": ["Excel", "PowerPoint", "SQL", "Strategy", "Analytics", "Stakeholder Management", "Leadership", "Communication", "Planning"],
    "marketing": ["SEO", "Content Marketing", "Analytics", "Social Media", "Branding", "Campaign Management", "Copywriting", "Ads"],
    "sales": ["CRM", "Salesforce", "Negotiation", "Prospecting", "Account Management", "Business Development", "Communication", "Closing"]
}

SOCIAL_PLATFORMS = [
    "linkedin", "instagram", "twitter", "github", "facebook", "website"
]

def generate_user(index):
    """Generate a single diverse user"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    username = f"{first}_{last}_{random.randint(100, 999)}"
    
    return {
        "id": f"user{index + 4}",  # Start from user4 (user1-3 already exist)
        "email": f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@email.com",
        "full_name": f"{first} {last}",
        "username": username,
        "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "is_active": True,
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 365)),
        "review_count": random.randint(0, 20),
        "reputation_score": random.randint(50, 100)
    }

def generate_person(index):
    """Generate a single diverse person profile"""
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    company = random.choice(COMPANIES)
    job_title = random.choice(JOB_TITLES)
    industry = random.choice(INDUSTRIES)
    city, state = random.choice(CITIES)
    
    # Determine role category for skills
    role_category = "business"
    if any(word in job_title.lower() for word in ["engineer", "developer", "architect"]):
        role_category = "engineer"
    elif "product" in job_title.lower():
        role_category = "product"
    elif any(word in job_title.lower() for word in ["data", "scientist", "analyst"]):
        role_category = "data"
    elif "design" in job_title.lower():
        role_category = "design"
    elif any(word in job_title.lower() for word in ["marketing", "brand"]):
        role_category = "marketing"
    elif "sales" in job_title.lower():
        role_category = "sales"
    
    skills = random.sample(SKILLS_BY_ROLE.get(role_category, SKILLS_BY_ROLE["business"]), 
                          k=random.randint(4, 7))
    
    # Generate social profiles (60% have LinkedIn, 40% have others)
    social_urls = {}
    if random.random() < 0.8:  # 80% have LinkedIn
        social_urls["linkedin_url"] = f"https://linkedin.com/in/{first.lower()}-{last.lower()}"
    if random.random() < 0.3:  # 30% have GitHub
        social_urls["github_url"] = f"https://github.com/{first.lower()}{last.lower()}"
    if random.random() < 0.2:  # 20% have Twitter
        social_urls["twitter_url"] = f"https://twitter.com/{first.lower()}_{last.lower()}"
    if random.random() < 0.15:  # 15% have Instagram
        social_urls["instagram_url"] = f"https://instagram.com/{first.lower()}.{last.lower()}"
    if random.random() < 0.1:  # 10% have personal website
        social_urls["website_url"] = f"https://{first.lower()}{last.lower()}.com"
    
    experience_years = random.randint(2, 20)
    review_count = random.randint(0, 15)
    
    person = {
        "id": f"person{index + 11}",  # Start from person11
        "name": f"{first} {last}",
        "email": f"{first.lower()}.{last.lower()}@{company.lower().replace(' ', '')}.com",
        "phone": f"+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
        "job_title": job_title,
        "company": company,
        "industry": industry,
        "city": city,
        "state": state,
        "country": "USA",
        "bio": f"{'Experienced' if experience_years > 7 else 'Skilled'} {job_title.lower()} at {company} with {experience_years} years in {industry.lower()}.",
        "skills": skills,
        "experience_years": experience_years,
        "education": f"{'MS' if random.random() < 0.4 else 'BS'} {random.choice(['Computer Science', 'Engineering', 'Business', 'Design', 'Data Science'])}",
        "certifications": random.sample(["AWS Certified", "PMP", "Scrum Master", "Six Sigma"], 
                                       k=random.randint(0, 2)),
        "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 730)),
        "updated_at": datetime.utcnow(),
        "review_count": review_count,
        "average_rating": round(random.uniform(3.5, 5.0), 1) if review_count > 0 else 0.0,
        "total_rating": 0
    }
    
    if person["review_count"] > 0:
        person["total_rating"] = int(person["average_rating"] * person["review_count"])
    
    # Add social URLs
    person.update(social_urls)
    
    return person

def generate_all_users():
    """Generate 50 diverse users"""
    users = []
    for i in range(47):  # 47 + 3 existing = 50
        users.append(generate_user(i))
    return users

def generate_all_persons():
    """Generate 50 diverse persons"""
    persons = []
    for i in range(40):  # 40 + 10 existing = 50
        persons.append(generate_person(i))
    return persons

# Integration with main.py database
def add_to_inmemory_database():
    """Add generated data to in-memory database"""
    users = generate_all_users()
    persons = generate_all_persons()
    
    # This would be imported and called in main.py
    return {
        "users": users,
        "persons": persons
    }

if __name__ == "__main__":
    print("🌱 Generating 50 diverse users for testing...")
    users = generate_all_users()
    persons = generate_all_persons()
    
    print(f"\n✅ Generated {len(users)} users")
    print(f"✅ Generated {len(persons)} persons")
    print(f"\n📊 Sample Users:")
    for user in users[:5]:
        print(f"   - {user['full_name']} (@{user['username']}) - {user['email']}")
    
    print(f"\n📊 Sample Persons:")
    for person in persons[:5]:
        print(f"   - {person['name']} - {person['job_title']} at {person['company']}")
    
    print(f"\n🎯 Distribution:")
    industries = {}
    for person in persons:
        ind = person["industry"]
        industries[ind] = industries.get(ind, 0) + 1
    print(f"   Industries covered: {len(industries)}")
    for ind, count in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"      - {ind}: {count} persons")
