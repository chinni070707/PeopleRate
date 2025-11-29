"""
Test script for Natural Language Processing features
"""

# Example test queries for search
test_queries = [
    # Simple name search
    "sasikala",
    
    # Name + location
    "sasikala bangalore",
    "sasikala who is in hyderabad",
    
    # Industry + location
    "sasikala who is into consulting business in Hyderabad",
    
    # Job title + company
    "software engineer at Microsoft",
    "senior engineer at Google in Seattle",
    
    # Skills-based
    "data scientist with Python experience",
    "designer skilled in Figma",
    
    # Contact information
    "+91-9952282170",
    "alice.johnson@microsoft.com",
    
    # Complex queries
    "senior software engineer at Microsoft in Seattle with 8 years experience",
    "product manager in Mountain View working on mobile apps",
]

# Example person descriptions for creation
test_person_descriptions = [
    # Simple
    "Sasikala who is into consulting business in Hyderabad, phone: +91-9952282170",
    
    # Detailed
    "John Smith is a senior software engineer at Google in Mountain View with 10 years experience in Python and machine learning. Email: john@gmail.com, Phone: +1-555-0123",
    
    # With LinkedIn
    "Emily Rodriguez, UX Design Director at Apple in Cupertino. LinkedIn: linkedin.com/in/emily-rodriguez. Specializes in user research and Figma.",
    
    # With skills
    "David Chen, data analyst at Amazon in Seattle. Expert in SQL, Python, and Tableau. 5 years experience. Email: david@email.com",
    
    # Consulting
    "Sarah Thompson is a management consultant at McKinsey in New York. Specializes in digital transformation and strategy. Phone: +1-555-9876",
    
    # Healthcare
    "Dr. Michael Brown, cardiologist at Johns Hopkins Hospital in Baltimore. 15 years experience. Email: dr.brown@hospital.com",
]

print("🧪 Natural Language Processing Test Cases\n")
print("=" * 60)

print("\n📝 Search Test Queries:")
print("-" * 60)
for i, query in enumerate(test_queries, 1):
    print(f"{i}. \"{query}\"")

print("\n\n📝 Person Creation Test Descriptions:")
print("-" * 60)
for i, desc in enumerate(test_person_descriptions, 1):
    print(f"{i}. \"{desc}\"")
    print()

print("=" * 60)
print("\n✅ To test these:")
print("1. Open http://localhost:8000 in your browser")
print("2. Login with: john.reviewer@email.com / password123")
print("3. Try the search queries in the search box")
print("4. Try 'Add New Person' with the descriptions")
print("5. Check the 'Preview Parsing' feature!")
