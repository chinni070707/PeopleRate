"""
Sample Data Initialization Script
Creates sample users, persons, and reviews for testing and development
"""

import bcrypt
from datetime import datetime, timedelta
from app.models.mongodb_models import User, Person, Review


async def create_sample_data():
    """Create comprehensive sample data"""
    
    print("🌱 Creating sample users...")
    
    # Sample Users
    users_data = [
        {
            "email": "john.reviewer@email.com",
            "username": "TechReviewer2024",
            "full_name": "John Reviewer",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "email_verified": True,
            "review_count": 3,
            "reputation_score": 85,
            "subscription_tier": "professional"
        },
        {
            "email": "sarah.manager@email.com",
            "username": "ProjectManager_Pro",
            "full_name": "Sarah Manager",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "email_verified": True,
            "review_count": 4,
            "reputation_score": 92,
            "subscription_tier": "basic"
        },
        {
            "email": "mike.colleague@email.com",
            "username": "DataScience_Mike",
            "full_name": "Mike Colleague",
            "password": bcrypt.hashpw("password123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
            "email_verified": True,
            "review_count": 2,
            "reputation_score": 78,
            "subscription_tier": "free"
        }
    ]
    
    created_users = []
    for user_data in users_data:
        user = User(**user_data)
        await user.insert()
        created_users.append(user)
        print(f"  ✅ Created user: {user.username}")
    
    print(f"\n👥 Creating sample persons...")
    
    # Sample Persons
    persons_data = [
        {
            "name": "Alice Johnson",
            "email": "alice.johnson@microsoft.com",
            "phone": "+1-555-0123",
            "job_title": "Senior Software Engineer",
            "company": "Microsoft",
            "industry": "Technology",
            "city": "Seattle",
            "state": "WA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/alice-johnson",
            "bio": "Experienced software engineer specializing in cloud computing and AI. Lead developer on Azure ML platform with 8+ years in tech industry.",
            "skills": ["Python", "Azure", "Machine Learning", "JavaScript", "React"],
            "experience_years": 8,
            "education": "MS Computer Science, University of Washington",
            "certifications": ["Azure Solutions Architect", "AWS Certified Developer"],
            "review_count": 5,
            "average_rating": 4.6,
            "total_rating": 23
        },
        {
            "name": "Robert Chen",
            "email": "r.chen@google.com",
            "phone": "+1-555-0234",
            "job_title": "Product Manager",
            "company": "Google",
            "industry": "Technology",
            "city": "Mountain View",
            "state": "CA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/robert-chen",
            "bio": "Strategic product manager with expertise in mobile applications and user experience. Led product launches reaching 100M+ users.",
            "skills": ["Product Strategy", "Data Analysis", "User Research", "Agile", "SQL"],
            "experience_years": 6,
            "education": "MBA Stanford, BS Engineering UC Berkeley",
            "certifications": ["Certified Scrum Product Owner", "Google Analytics"],
            "review_count": 3,
            "average_rating": 4.3,
            "total_rating": 13
        },
        {
            "name": "Emily Rodriguez",
            "email": "emily.rodriguez@apple.com",
            "phone": "+1-555-0345",
            "job_title": "UX Design Director",
            "company": "Apple",
            "industry": "Technology",
            "city": "Cupertino",
            "state": "CA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/emily-rodriguez",
            "bio": "Award-winning UX designer with 10+ years creating intuitive user experiences. Led design teams for major product launches at Apple.",
            "skills": ["UX Design", "Figma", "Design Systems", "User Research", "Prototyping"],
            "experience_years": 10,
            "education": "MFA Design, Art Center College of Design",
            "certifications": ["Google UX Design Certificate", "Adobe Certified Expert"],
            "review_count": 7,
            "average_rating": 4.8,
            "total_rating": 34
        },
        {
            "name": "Sasikala",
            "email": "sasikala.chennai@email.com",
            "phone": "+91-9952282170",
            "job_title": "Software Developer",
            "company": "Tech Solutions",
            "industry": "Technology",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "India",
            "linkedin_url": "https://linkedin.com/in/sasikala-chennai",
            "instagram_url": "https://instagram.com/sasikala.dev",
            "twitter_url": "https://twitter.com/sasikala_tech",
            "github_url": "https://github.com/sasikala-chennai",
            "bio": "Experienced software developer with expertise in full-stack development and cloud technologies.",
            "skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
            "experience_years": 5,
            "education": "BTech Computer Science",
            "certifications": ["AWS Certified Developer"],
            "review_count": 0,
            "average_rating": 0.0,
            "total_rating": 0
        },
        {
            "name": "Sasikala",
            "email": "sasikala.sanjose@email.com",
            "phone": "+1-408-555-0999",
            "job_title": "Senior Engineer",
            "company": "Silicon Valley Tech",
            "industry": "Technology",
            "city": "San Jose",
            "state": "CA",
            "country": "USA",
            "linkedin_url": "https://linkedin.com/in/sasikala-sanjose",
            "facebook_url": "https://facebook.com/sasikala.engineer",
            "github_url": "https://github.com/sasikala-sj",
            "website_url": "https://sasikala.dev",
            "bio": "Senior engineer with extensive experience in distributed systems and microservices architecture.",
            "skills": ["Java", "Kubernetes", "Docker", "Microservices", "System Design"],
            "experience_years": 8,
            "education": "MS Computer Science, San Jose State University",
            "certifications": ["Kubernetes Certified", "Java Certified Professional"],
            "review_count": 0,
            "average_rating": 0.0,
            "total_rating": 0
        }
    ]
    
    created_persons = []
    for person_data in persons_data:
        person = Person(**person_data)
        await person.insert()
        created_persons.append(person)
        print(f"  ✅ Created person: {person.name}")
    
    print(f"\n⭐ Creating sample reviews...")
    
    # Sample Reviews
    reviews_data = [
        {
            "person_id": str(created_persons[0].id),
            "reviewer_id": str(created_users[0].id),
            "reviewer_username": created_users[0].username,
            "rating": 5,
            "title": "Outstanding technical expertise and mentorship",
            "comment": "Alice is an exceptional software engineer. I worked with her on the Azure ML platform project and was consistently impressed by her technical expertise and problem-solving abilities. She has a knack for breaking down complex problems into manageable solutions and always delivers high-quality code. Her knowledge of machine learning and cloud architecture is outstanding. Highly recommend working with Alice on any technical project.",
            "relationship": "colleague",
            "work_quality": 5,
            "communication": 5,
            "reliability": 5,
            "professionalism": 5,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=5),
            "is_verified": True,
            "helpful_count": 12,
            "moderation_status": "approved"
        },
        {
            "person_id": str(created_persons[0].id),
            "reviewer_id": str(created_users[1].id),
            "reviewer_username": created_users[1].username,
            "rating": 4,
            "title": "Great developer, excellent team player",
            "comment": "Had the pleasure of managing Alice for 2 years. She's incredibly talented and always goes above and beyond. Her ability to mentor junior developers is remarkable, and she consistently contributes innovative ideas to our team. The only minor area for improvement would be her presentation skills, but her technical abilities more than make up for it.",
            "relationship": "manager",
            "work_quality": 5,
            "communication": 4,
            "reliability": 5,
            "professionalism": 5,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=15),
            "is_verified": True,
            "helpful_count": 8,
            "moderation_status": "approved"
        },
        {
            "person_id": str(created_persons[1].id),
            "reviewer_id": str(created_users[0].id),
            "reviewer_username": created_users[0].username,
            "rating": 4,
            "title": "Solid product management skills",
            "comment": "Robert is a solid product manager with great analytical skills. He led our mobile app redesign project and delivered excellent results. His data-driven approach to decision making is impressive, and he's great at stakeholder management. Communication is clear and he keeps everyone aligned on priorities.",
            "relationship": "team member",
            "work_quality": 4,
            "communication": 5,
            "reliability": 4,
            "professionalism": 4,
            "would_recommend": True,
            "created_at": datetime.utcnow() - timedelta(days=10),
            "is_verified": True,
            "helpful_count": 6,
            "moderation_status": "approved"
        }
    ]
    
    for review_data in reviews_data:
        review = Review(**review_data)
        await review.insert()
        print(f"  ✅ Created review for {created_persons[0].name if review_data['person_id'] == str(created_persons[0].id) else 'person'}")
    
    print(f"\n✅ Sample data initialization complete!")
    print(f"   📊 {len(created_users)} users")
    print(f"   👥 {len(created_persons)} persons")
    print(f"   ⭐ {len(reviews_data)} reviews")
