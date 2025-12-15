# Version 1.0
from datetime import datetime
import re

class UserProfile:
    """User profile management system"""
    
    def __init__(self):
        self.profiles = {}
        self.next_id = 1
    
    def create_profile(self, username, email, full_name=None, bio=None, avatar_url=None):
        """
        Create a new user profile
        
        Args:
            username: Unique username (3-20 chars, alphanumeric + underscore)
            email: Valid email address
            full_name: User's full name (optional)
            bio: User biography (optional, max 500 chars)
            avatar_url: URL to user's avatar image (optional)
            
        Returns:
            dict: Created profile data with ID
        """
        # Validate username
        if not username or len(username) < 3 or len(username) > 20:
            raise ValueError("Username must be 3-20 characters")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("Username can only contain letters, numbers, and underscores")
        
        # Check if username already exists
        if any(p['username'] == username for p in self.profiles.values()):
            raise ValueError("Username already exists")
        
        # Validate email
        if not email or not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValueError("Invalid email address")
        
        # Check if email already exists
        if any(p['email'] == email for p in self.profiles.values()):
            raise ValueError("Email already exists")
        
        # Validate bio length
        if bio and len(bio) > 500:
            raise ValueError("Bio cannot exceed 500 characters")
        
        # Validate avatar URL
        if avatar_url and not avatar_url.startswith(('http://', 'https://')):
            raise ValueError("Avatar URL must be a valid HTTP/HTTPS URL")
        
        # Create profile
        profile_id = self.next_id
        self.next_id += 1
        
        profile = {
            'id': profile_id,
            'username': username,
            'email': email,
            'full_name': full_name,
            'bio': bio,
            'avatar_url': avatar_url,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        self.profiles[profile_id] = profile
        return profile
    
    def get_profile(self, profile_id):
        """
        Retrieve a user profile by ID
        
        Args:
            profile_id: Profile ID to retrieve
            
        Returns:
            dict: Profile data or None if not found
        """
        if not isinstance(profile_id, int) or profile_id < 1:
            raise ValueError("Profile ID must be a positive integer")
        
        return self.profiles.get(profile_id)
    
    def update_profile(self, profile_id, full_name=None, bio=None, avatar_url=None):
        """
        Update an existing user profile
        
        Args:
            profile_id: Profile ID to update
            full_name: New full name (optional)
            bio: New biography (optional)
            avatar_url: New avatar URL (optional)
            
        Returns:
            dict: Updated profile data
        """
        profile = self.get_profile(profile_id)
        
        if not profile:
            raise ValueError("Profile not found")
        
        # Validate bio if provided
        if bio is not None:
            if len(bio) > 500:
                raise ValueError("Bio cannot exceed 500 characters")
            profile['bio'] = bio
        
        # Validate avatar URL if provided
        if avatar_url is not None:
            if avatar_url and not avatar_url.startswith(('http://', 'https://')):
                raise ValueError("Avatar URL must be a valid HTTP/HTTPS URL")
            profile['avatar_url'] = avatar_url
        
        # Update full name if provided
        if full_name is not None:
            profile['full_name'] = full_name
        
        # Update timestamp
        profile['updated_at'] = datetime.now().isoformat()
        
        return profile
    
    def delete_profile(self, profile_id):
        """
        Delete a user profile
        
        Args:
            profile_id: Profile ID to delete
            
        Returns:
            bool: True if deleted, False if not found
        """
        if profile_id in self.profiles:
            del self.profiles[profile_id]
            return True
        return False
    
    def search_profiles(self, query):
        """
        Search profiles by username or full name
        
        Args:
            query: Search string
            
        Returns:
            list: List of matching profiles
        """
        if not query or len(query) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        query_lower = query.lower()
        results = []
        
        for profile in self.profiles.values():
            if (query_lower in profile['username'].lower() or 
                (profile['full_name'] and query_lower in profile['full_name'].lower())):
                results.append(profile)
        
        return results
    
    def list_all_profiles(self, limit=10, offset=0):
        """
        List all profiles with pagination
        
        Args:
            limit: Maximum number of profiles to return (default 10)
            offset: Number of profiles to skip (default 0)
            
        Returns:
            dict: Paginated profile list with metadata
        """
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        if offset < 0:
            raise ValueError("Offset cannot be negative")
        
        all_profiles = list(self.profiles.values())
        total = len(all_profiles)
        
        paginated = all_profiles[offset:offset + limit]
        
        return {
            'profiles': paginated,
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        }
```

5. Commit directly to `feature/user-profile-api` branch

---

## 📝 **STEP 3: Create Pull Request**

1. You'll see the yellow banner: **"feature/user-profile-api had recent pushes"**
2. Click **"Compare & pull request"**
3. **Title:** `Implement user profile management API`
4. **Body:**
```
Implements user profile CRUD operations as requested in #[issue_number]

Features:
✅ Create profile with validation
✅ Get profile by ID
✅ Update profile fields
✅ Delete profile
✅ Search profiles by username/name
✅ List all profiles with pagination

Validation includes:
- Username format and uniqueness
- Email format and uniqueness
- Bio length limits (500 chars)
- Avatar URL format
- Input sanitization
