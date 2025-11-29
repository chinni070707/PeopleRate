"""
Content Moderation System for PeopleRate
Provides profanity filtering, content flagging, and moderation tools
"""

# Basic profanity list (expandable)
PROFANITY_LIST = {
    # Common offensive words (abbreviated for demonstration)
    "damn", "hell", "crap", "stupid", "idiot", "dumb", "sucks", 
    "hate", "worst", "terrible", "horrible", "awful", "garbage",
    # Add more as needed - this is a starter list
}

def contains_profanity(text: str) -> bool:
    """Check if text contains profanity"""
    if not text:
        return False
    
    text_lower = text.lower()
    for word in PROFANITY_LIST:
        if word in text_lower:
            return True
    return False

def filter_profanity(text: str, replacement: str = "***") -> str:
    """Replace profanity with asterisks"""
    if not text:
        return text
    
    filtered_text = text
    for word in PROFANITY_LIST:
        # Case-insensitive replacement
        import re
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        filtered_text = pattern.sub(replacement, filtered_text)
    
    return filtered_text

def analyze_content(text: str) -> dict:
    """Analyze content for moderation issues"""
    result = {
        "has_profanity": False,
        "profanity_count": 0,
        "is_spam": False,
        "is_too_short": False,
        "is_all_caps": False,
        "warnings": []
    }
    
    if not text:
        return result
    
    # Check profanity
    text_lower = text.lower()
    profanity_count = sum(1 for word in PROFANITY_LIST if word in text_lower)
    if profanity_count > 0:
        result["has_profanity"] = True
        result["profanity_count"] = profanity_count
        result["warnings"].append(f"Contains {profanity_count} potentially offensive word(s)")
    
    # Check spam patterns
    if text.count("http") > 3 or text.count("www.") > 2:
        result["is_spam"] = True
        result["warnings"].append("May contain spam links")
    
    # Check if too short for meaningful review
    if len(text.strip()) < 20:
        result["is_too_short"] = True
        result["warnings"].append("Content may be too short")
    
    # Check if all caps (shouting)
    if len(text) > 20 and text.isupper():
        result["is_all_caps"] = True
        result["warnings"].append("All caps detected (consider moderating)")
    
    return result

def get_moderation_score(text: str) -> int:
    """
    Calculate moderation score (0-100)
    Higher score = more likely to need moderation
    """
    analysis = analyze_content(text)
    score = 0
    
    if analysis["has_profanity"]:
        score += analysis["profanity_count"] * 20
    
    if analysis["is_spam"]:
        score += 40
    
    if analysis["is_all_caps"]:
        score += 15
    
    # Cap at 100
    return min(score, 100)

def should_auto_flag(text: str) -> bool:
    """Determine if content should be automatically flagged"""
    score = get_moderation_score(text)
    return score >= 40  # Auto-flag if score is 40 or higher


# Moderation guidelines
MODERATION_GUIDELINES = """
# PeopleRate Moderation Guidelines

## Our Commitment
PeopleRate is committed to maintaining a respectful, professional platform for authentic peer reviews.

## What We Allow
✅ Honest professional feedback (positive and negative)
✅ Constructive criticism with specific examples
✅ Factual accounts of professional experiences
✅ Balanced reviews highlighting strengths and weaknesses

## What We Don't Allow
❌ Personal attacks or harassment
❌ Profanity or vulgar language
❌ Spam or promotional content
❌ False or defamatory statements
❌ Discrimination based on protected characteristics
❌ Reviews about yourself (must be third-party)
❌ Reviews from competitors with malicious intent

## Content Standards
- **Be Specific**: Include concrete examples and context
- **Be Professional**: Focus on work-related interactions
- **Be Honest**: Share your genuine experience
- **Be Respectful**: Critique behavior, not character
- **Be Fair**: Consider both positives and negatives

## Flagging Content
Users can flag reviews that violate our guidelines. Our moderation team reviews flagged content within 48 hours.

### How to Flag
1. Click "Report" button on the review
2. Select reason for flagging
3. Optionally provide additional context
4. Submit - we'll review promptly

### What Happens Next
- **Automatic Review**: High-risk content is auto-flagged
- **Human Review**: Our team reviews all flags
- **Actions**: We may hide, edit, or remove violating content
- **Appeals**: Authors can appeal moderation decisions

## For Reviewers
- Write reviews as if the person will read them
- Use professional language
- Provide constructive feedback
- Focus on observable behaviors and outcomes

## For Profile Owners
- You can respond to reviews on your claimed profile
- Responses must also follow guidelines
- Disputing false information is encouraged
- Personal attacks in responses will be removed

## Legal Protection
- PeopleRate is protected under Section 230 of the Communications Decency Act
- We are a platform for user-generated content
- We act quickly on valid legal requests
- We cooperate with law enforcement when appropriate

## Reporting Serious Issues
For serious concerns (threats, illegal content, etc.):
- Email: moderation@peoplerate.com
- Include: URL, description, your concern
- We respond to urgent matters within 24 hours

---
**Last Updated**: November 2025
"""
