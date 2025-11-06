# PeopleRate - People Review Platform

PeopleRate is a web platform similar to TrustPilot but for rating and reviewing individuals. Users can search for people by name, phone number, email, company, city, or LinkedIn profile and leave reviews based on their experiences.

## Features

### Core Features
- **User Authentication**: JWT-based registration and login
- **Person Profiles**: Create and manage profiles for people to be reviewed
- **Review System**: 5-star rating system with detailed reviews
- **Advanced Search**: Search by multiple criteria (name, phone, email, company, LinkedIn, etc.)
- **Review Categories**: Professional, Personal, Service-related reviews

### Search Capabilities
- Name-based search with partial matching
- Phone number pattern recognition
- Email address matching
- LinkedIn profile URL detection
- Company and city-based filtering
- Combined search across multiple fields

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: MongoDB with Motor async driver
- **Authentication**: JWT tokens with bcrypt password hashing
- **Frontend**: HTML/CSS/JavaScript (Vanilla JS)
- **Development**: Local MongoDB instance

## Project Structure

```
PeopleRate/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # User data models
│   │   ├── person.py        # Person profile models
│   │   └── review.py        # Review models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── persons.py       # Person profile endpoints
│   │   └── reviews.py       # Review management
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── database.py      # MongoDB connection
│   │   └── auth.py          # Authentication utilities
│   └── __init__.py
├── static/
│   ├── css/
│   │   └── style.css        # Application styles
│   └── js/
│       └── script.js        # Frontend JavaScript
├── templates/
│   └── index.html           # Main page template
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── main.py                  # FastAPI application entry point
└── README.md               # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd PeopleRate
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup MongoDB

#### Option A: Local MongoDB
1. Install MongoDB from [mongodb.com](https://www.mongodb.com/try/download/community)
2. Start MongoDB service
3. MongoDB will run on `mongodb://localhost:27017` by default

#### Option B: MongoDB Atlas (Cloud)
1. Create account at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create a cluster
3. Get connection string
4. Update `.env` file with your connection string

### 5. Configure Environment Variables
Create or update the `.env` file:
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=peopleRate_db
SECRET_KEY=your-very-secure-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Change the `SECRET_KEY` to a secure random string in production!

### 6. Run the Application
```bash
python main.py
```

The application will start on `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative API docs**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Person Management
- `POST /api/persons/` - Create person profile
- `GET /api/persons/search` - Search for people
- `GET /api/persons/{person_id}` - Get person details
- `PUT /api/persons/{person_id}` - Update person profile

### Reviews
- `POST /api/reviews/` - Create review
- `GET /api/reviews/person/{person_id}` - Get reviews for a person
- `GET /api/reviews/my-reviews` - Get current user's reviews

## Usage Examples

### 1. Search for People
```javascript
// Search by name
GET /api/persons/search?q=John Smith

// Search by phone
GET /api/persons/search?q=+1234567890

// Search by company
GET /api/persons/search?q=Microsoft

// Search by LinkedIn
GET /api/persons/search?q=https://linkedin.com/in/johnsmith
```

### 2. Create a Review
```javascript
POST /api/reviews/
{
  "person_id": "507f1f77bcf86cd799439011",
  "rating": 5,
  "title": "Excellent collaboration",
  "content": "John was very professional and delivered quality work on time.",
  "category": "Professional"
}
```

## Development

### Database Schema

#### Users Collection
```javascript
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password_hash": String,
  "full_name": String,
  "is_active": Boolean,
  "created_at": Date,
  "updated_at": Date
}
```

#### Persons Collection
```javascript
{
  "_id": ObjectId,
  "full_name": String,
  "nickname": String,
  "phone_number": String,
  "email": String,
  "linkedin_url": String,
  "company": String,
  "job_title": String,
  "city": String,
  "country": String,
  "bio": String,
  "is_verified": Boolean,
  "claimed_by_user_id": ObjectId,
  "total_reviews": Number,
  "average_rating": Number,
  "created_at": Date,
  "updated_at": Date
}
```

#### Reviews Collection
```javascript
{
  "_id": ObjectId,
  "reviewer_id": ObjectId,
  "person_id": ObjectId,
  "rating": Number (1-5),
  "title": String,
  "content": String,
  "category": String,
  "is_verified": Boolean,
  "is_flagged": Boolean,
  "moderation_status": String,
  "helpful_count": Number,
  "reported_count": Number,
  "created_at": Date,
  "updated_at": Date
}
```

### Adding Features

To add new features:
1. Create/update models in `app/models/`
2. Add API endpoints in `app/routes/`
3. Update frontend JavaScript in `static/js/script.js`
4. Add new HTML templates in `templates/`

### Running Tests
```bash
# Install test dependencies (add to requirements.txt)
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## Deployment

### Production Considerations
1. **Security**:
   - Change `SECRET_KEY` to a secure random string
   - Use HTTPS in production
   - Set up proper CORS policies
   - Implement rate limiting

2. **Database**:
   - Use MongoDB Atlas or properly configured MongoDB instance
   - Set up database backups
   - Configure indexes for better search performance

3. **Environment**:
   - Use environment variables for all configuration
   - Set up logging
   - Configure monitoring

### Docker Deployment (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Privacy & Legal Considerations

⚠️ **Important**: This platform deals with personal information and reviews about individuals. Consider:

1. **Privacy Laws**: Ensure compliance with GDPR, CCPA, and local privacy laws
2. **Consent**: Implement consent mechanisms for profile creation
3. **Content Moderation**: Set up review moderation to prevent abuse
4. **Right to Deletion**: Implement user data deletion capabilities
5. **Terms of Service**: Create comprehensive terms of service
6. **Content Policy**: Define what constitutes appropriate reviews

## License

[Add your license here]

## Support

For questions or issues, please [create an issue](link-to-issues) in the repository.