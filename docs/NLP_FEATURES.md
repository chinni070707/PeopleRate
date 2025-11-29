# Natural Language Processing Features

## Overview

PeopleRate now features advanced **Natural Language Processing (NLP)** for both search and person creation. Users can interact with the platform using natural, conversational language instead of filling out structured forms.

---

## 🔍 Natural Language Search

### How It Works

Instead of using structured filters, users can search naturally:

### Example Queries:

1. **Name-based search:**
   - `"sasikala"`
   - `"John Smith"`
   - `"Dr. Michael Brown"`

2. **Industry + Location search:**
   - `"sasikala who is into consulting business in Hyderabad"`
   - `"software engineer in Seattle"`
   - `"doctor in Baltimore"`

3. **Company + Role search:**
   - `"engineer at Google"`
   - `"designer at Apple in Cupertino"`
   - `"consultant at McKinsey in New York"`

4. **Skills-based search:**
   - `"data scientist with Python experience"`
   - `"expert in machine learning"`
   - `"UX designer skilled in Figma"`

5. **Contact information search:**
   - `"+91-9952282170"` (phone number)
   - `"john@email.com"` (email address)
   - `"linkedin.com/in/username"` (LinkedIn profile)

6. **Complex multi-criteria:**
   - `"senior software engineer at Microsoft in Seattle with 8 years experience"`
   - `"product manager in Mountain View working on mobile apps"`

---

## ✨ Natural Language Person Creation

### How It Works

Instead of filling multiple form fields, users can describe a person in natural language:

### Example Descriptions:

#### Example 1: Simple Description
```
Sasikala who is into consulting business in Hyderabad, phone: +91-9952282170
```

**AI Extracts:**
- Name: Sasikala
- Industry: Consulting
- City: Hyderabad
- State: Telangana
- Country: India
- Phone: +91-9952282170

#### Example 2: Detailed Professional
```
John Smith is a senior software engineer at Google in Mountain View with 10 years experience in Python and machine learning. Email: john@gmail.com, Phone: +1-555-0123
```

**AI Extracts:**
- Name: John Smith
- Job Title: Senior Software Engineer
- Company: Google
- City: Mountain View
- State: CA
- Country: USA
- Experience: 10 years
- Skills: Python, Machine Learning
- Email: john@gmail.com
- Phone: +1-555-0123

#### Example 3: LinkedIn Profile
```
Emily Rodriguez, UX Design Director at Apple in Cupertino. LinkedIn: linkedin.com/in/emily-rodriguez. Specializes in user research and Figma.
```

**AI Extracts:**
- Name: Emily Rodriguez
- Job Title: UX Design Director
- Company: Apple
- City: Cupertino
- LinkedIn: https://linkedin.com/in/emily-rodriguez
- Skills: User Research, Figma

---

## 🧠 NLP Intelligence

### What the NLP System Understands:

1. **Names:**
   - Extracts first 1-3 capitalized words before keywords
   - Handles multiple name formats

2. **Job Titles:**
   - Recognizes 20+ common job titles
   - Extracts title context (e.g., "Senior Software Engineer")

3. **Industries:**
   - Technology, Consulting, Healthcare, Finance, Education
   - Retail, Manufacturing, Marketing, Design, Data Science
   - And more...

4. **Locations:**
   - 25+ Indian cities (Chennai, Hyderabad, Bangalore, etc.)
   - 18+ US cities (Seattle, New York, San Francisco, etc.)
   - Automatically determines state/country

5. **Companies:**
   - Extracts company names after "at", "with", "works at"
   - Handles company names with special characters

6. **Skills:**
   - Extracts skills mentioned after "expert in", "skilled in", "knows"
   - Parses comma-separated or slash-separated skills

7. **Experience:**
   - Understands "X years", "X+ years", "over X years"
   - Extracts numerical experience values

8. **Contact Information:**
   - Email addresses (any format)
   - Phone numbers (international formats)
   - LinkedIn URLs

---

## 📊 Scoring Algorithm

The NLP system scores search results based on:

| Match Type | Score Weight |
|-----------|--------------|
| Email exact match | 150 |
| Phone exact match | 150 |
| Name match (full) | 100 |
| Name match (partial) | 50 |
| Industry match | 40 |
| Job title match | 35 |
| City match | 30 |
| Company match | 25 |
| Skill match (per skill) | 10 |
| Average rating boost | rating × 3 |
| Review count boost | min(count, 10) × 2 |

---

## 🎯 API Endpoints

### 1. Natural Language Search
```http
GET /api/persons/search?q={natural_language_query}
```

**Response:**
```json
{
  "query": "sasikala who is into consulting business in Hyderabad",
  "parsed": {
    "name": "sasikala",
    "industry": "Consulting",
    "city": "Hyderabad",
    "state": "Telangana",
    "country": "India"
  },
  "count": 1,
  "persons": [...]
}
```

### 2. Create Person from Natural Language
```http
POST /api/persons/nlp
Content-Type: multipart/form-data

description: "John Smith is a senior software engineer at Google..."
```

**Response:**
```json
{
  "message": "Person created successfully from natural language description",
  "person_id": "person123",
  "parsed_data": {
    "name": "John Smith",
    "job_title": "Senior Software Engineer",
    "company": "Google",
    "city": "Mountain View",
    "email": "john@gmail.com",
    ...
  },
  "person": {...}
}
```

---

## 💻 Frontend Integration

### Search Component

```html
<input 
  type="text" 
  placeholder="e.g., 'software engineer at Google in Seattle'" 
  oninput="searchPeople()"
>
```

### Add Person Modal

```html
<textarea 
  placeholder="Example: 'John Smith is a senior software engineer at Google...'"
  id="personDescription"
></textarea>
<button onclick="previewParsedPerson()">🔍 Preview Parsing</button>
<button onclick="submitNewPersonNLP()">Add Person</button>
```

---

## 🎨 User Experience

### Search Page Features:
- ✅ Natural language placeholder examples
- ✅ Search suggestion examples below search bar
- ✅ Real-time search with debouncing
- ✅ Parsed query displayed in results

### Add Person Modal Features:
- ✅ Instruction box with examples
- ✅ Large textarea for natural description
- ✅ "Preview Parsing" button to see AI extraction
- ✅ Preview box showing parsed fields
- ✅ Auto-redirect after successful creation

---

## 🔧 Technical Implementation

### NLP Processor (`nlp_processor.py`)

The `NLPProcessor` class handles:
- Pattern recognition (email, phone, LinkedIn)
- Keyword extraction (industry, job title, location)
- Entity extraction (name, company, skills)
- Scoring algorithm for relevance
- State/country determination

### Key Methods:

1. **`parse_search_query(query)`**
   - Parses natural language search into structured data
   - Returns dict with extracted fields

2. **`parse_person_description(description)`**
   - Extracts person details from natural language
   - Handles various description formats

3. **`generate_search_score(person, parsed_query)`**
   - Scores person relevance to query
   - Returns float score (higher = better match)

4. **`extract_person_fields(text)`**
   - Main method for person creation
   - Ensures at least name is extracted

---

## 🚀 Benefits

### For Users:
- ✅ **Faster**: No form fields to fill
- ✅ **Intuitive**: Just type naturally
- ✅ **Flexible**: Multiple ways to describe same thing
- ✅ **Powerful**: Complex multi-criteria search

### For Platform:
- ✅ **Higher conversion**: Less friction
- ✅ **Better data**: More complete profiles
- ✅ **User satisfaction**: Modern, AI-powered experience
- ✅ **Competitive advantage**: Unique feature

---

## 📈 Future Enhancements

### Planned Features:
1. **Machine Learning Integration**
   - Train on user queries for better parsing
   - Learn common patterns in descriptions

2. **Multi-language Support**
   - Support for Hindi, Spanish, etc.
   - Transliteration for Indian names

3. **Autocomplete Suggestions**
   - Smart suggestions based on partial input
   - Popular search patterns

4. **Voice Input**
   - Speech-to-text for mobile users
   - Voice search on homepage

5. **Advanced Entity Recognition**
   - Company aliases (MSFT = Microsoft)
   - Degree/certification parsing
   - Date/time period parsing

---

## 🧪 Testing Examples

### Test Case 1: Basic Name Search
**Input:** `"sasikala"`
**Expected:** Find all persons named Sasikala

### Test Case 2: Industry + Location
**Input:** `"sasikala who is into consulting business in Hyderabad"`
**Expected:** 
- Name: sasikala
- Industry: Consulting
- City: Hyderabad

### Test Case 3: Complex Query
**Input:** `"senior software engineer at Google in Mountain View with Python experience"`
**Expected:**
- Job Title: Senior Software Engineer
- Company: Google
- City: Mountain View
- Skills: Python

### Test Case 4: Contact Search
**Input:** `"+91-9952282170"`
**Expected:** Find person with exact phone match

### Test Case 5: Email Search
**Input:** `"alice.johnson@microsoft.com"`
**Expected:** Find person with exact email match

---

## 📝 Implementation Notes

### Dependencies:
- **Python Standard Library**: `re` for regex patterns
- **No External NLP Libraries**: Custom implementation for lightweight solution

### Performance:
- **Search**: O(n) where n = number of persons
- **Parsing**: O(1) constant time per query
- **Memory**: Minimal overhead (~1MB for processor)

### Error Handling:
- Graceful degradation if parsing fails
- Minimum requirement: name extraction
- Clear error messages for users

---

## 🎓 User Education

### Homepage Tips:
- Display example queries prominently
- Show parsed results to educate users
- Provide search tips below search bar

### Add Person Modal:
- Clear instructions in highlighted box
- Multiple examples with different formats
- Preview feature to show AI understanding

---

## 🏆 Success Metrics

### Key Performance Indicators:
1. **Search Success Rate**: % queries returning results
2. **Person Creation Completion**: % users completing form
3. **Time to Complete**: Average time to add person
4. **User Satisfaction**: Feedback on NLP features

---

## 📞 Support

For questions or issues with NLP features:
- Check examples in this documentation
- Try the preview feature before submitting
- Contact support if AI misunderstands input

---

**Last Updated:** November 6, 2025
**Version:** 2.6.0 - Natural Language Processing Release
