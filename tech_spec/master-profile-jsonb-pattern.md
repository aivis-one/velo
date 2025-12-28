# MasterProfile Model — JSONB Data Pattern

## Database Schema

```sql
CREATE TABLE master_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    
    -- All master data in JSONB
    data JSONB NOT NULL DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- GIN index for fast JSONB queries
CREATE INDEX idx_master_data_gin ON master_profiles USING GIN (data);

-- Specific indexes for frequently queried fields
CREATE INDEX idx_master_status 
ON master_profiles ((data->'account'->>'status'))
WHERE (data->'account'->>'status') IS NOT NULL;

CREATE INDEX idx_master_is_accepting 
ON master_profiles (((data->'availability'->'is_accepting')::boolean))
WHERE (data->'availability'->'is_accepting') IS NOT NULL;
```

---

## JSONB Structure

### Complete example
```json
{
  "account": {
    "status": "verified",
    "verification": {
      "submitted_at": "2025-01-10T10:00:00Z",
      "verified_at": "2025-01-12T15:30:00Z",
      "verified_by": "admin_user_id",
      "documents": [
        {
          "type": "certification",
          "name": "Yoga Alliance RYT-200",
          "url": "s3://bucket/cert.pdf",
          "uploaded_at": "2025-01-10T10:00:00Z"
        }
      ],
      "notes": "Checked certifications - all valid"
    },
    "moderation": {
      "suspended_at": null,
      "suspension_reason": null,
      "suspended_by": null
    }
  },
  
  "availability": {
    "is_accepting": true,
    "note": "",
    "auto_pause": {
      "enabled": false,
      "threshold_practices_per_month": 20,
      "threshold_students_per_week": 50,
      "last_triggered_at": null
    }
  },
  
  "profile": {
    "bio": {
      "short": "Meditation teacher with 10 years of experience",
      "full": "Long bio text with detailed background...",
      "video_intro_url": null
    },
    "approach_methods": ["Vipassana", "Mindfulness", "Breathwork"],
    "experience": {
      "years": 10,
      "specializations": ["Anxiety relief", "Sleep improvement", "Focus"],
      "training": [
        {
          "name": "Vipassana 10-day retreat",
          "institution": "Dhamma Center",
          "year": 2015,
          "certificate_url": "s3://..."
        }
      ]
    },
    "certifications": [
      {
        "name": "Certified Meditation Instructor",
        "issuer": "International Meditation Society",
        "year": 2020,
        "url": "https://...",
        "expires_at": null
      }
    ],
    "languages": ["en", "ru"],
    "timezone_preferences": ["UTC", "Europe/Moscow"]
  },
  
  "settings": {
    "accepts_groups": true,
    "accepts_one_on_one": true,
    "max_group_size": 20,
    "booking_buffer_minutes": 30,
    "cancellation_policy": "24h notice required",
    "auto_record_practices": false
  },
  
  "stats": {
    "total_practices_held": 150,
    "total_students": 450,
    "total_hours": 300,
    "avg_rating": 4.8,
    "completion_rate": 0.95,
    "response_time_hours": 2.5,
    "monthly_practices": 12,
    "weekly_students": 30
  }
}
```

---

## Account Status

### Status values

| Status | Description | Can create practices? | Visible to users? |
|--------|-------------|----------------------|-------------------|
| `pending_verification` | Waiting for admin approval | ❌ No | ❌ No |
| `verified` | Approved and active | ✅ Yes | ✅ Yes |
| `suspended` | Temporarily banned | ❌ No (existing bookings remain) | ❌ No |
| `banned` | Permanently banned | ❌ No | ❌ No |

### Verification flow

**Step 1: Master creates profile**
```json
{
  "account": {
    "status": "pending_verification",
    "verification": {
      "submitted_at": "2025-01-10T10:00:00Z",
      "documents": [...]
    }
  }
}
```

**Step 2: Admin approves**
```json
{
  "account": {
    "status": "verified",
    "verification": {
      "verified_at": "2025-01-12T15:30:00Z",
      "verified_by": "admin_uuid",
      "notes": "All documents valid"
    }
  }
}
```

**Step 3 (if violations): Suspend**
```json
{
  "account": {
    "status": "suspended",
    "moderation": {
      "suspended_at": "2025-02-01T10:00:00Z",
      "suspension_reason": "Student complaints",
      "suspended_by": "admin_uuid"
    }
  }
}
```

---

## Availability Management

### Simple toggle

**Master pauses accepting bookings:**
```python
master_profile.data['availability']['is_accepting'] = False
master_profile.data['availability']['note'] = "On vacation until Jan 15"
```

**UI displays:**
```
🔴 Not accepting new bookings
Note: On vacation until Jan 15
```

### Auto-pause (future feature)

**Configuration:**
```json
{
  "availability": {
    "auto_pause": {
      "enabled": true,
      "threshold_practices_per_month": 20,
      "threshold_students_per_week": 50
    }
  }
}
```

**Background job checks:**
```python
# Cron job runs daily
if master.monthly_practices >= master.auto_pause_threshold:
    master.data['availability']['is_accepting'] = False
    master.data['availability']['auto_pause']['last_triggered_at'] = now()
    
    # Notify master
    await notification_service.send(
        master_id=master.user_id,
        template="auto_paused_overbooked",
        variables={"monthly_practices": master.monthly_practices}
    )
```

---

## SQLAlchemy 2.0 Model

```python
# models/master_profile.py

from sqlalchemy import ForeignKey, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.mutable import MutableDict
from datetime import datetime
from uuid import UUID as UUIDType
import enum

class MasterProfile(Base):
    __tablename__ = 'master_profiles'
    
    # Primary key (also foreign key to users)
    user_id: Mapped[UUIDType] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True
    )
    
    # All master data in JSONB
    data: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        default=dict
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="master_profile")
    practices: Mapped[list["Practice"]] = relationship(back_populates="master")
    
    # Indexes
    __table_args__ = (
        Index('idx_master_data_gin', data, postgresql_using='gin'),
        Index(
            'idx_master_status',
            (data['account']['status'].astext),
            postgresql_where=(data['account']['status'] != None)
        ),
        Index(
            'idx_master_is_accepting',
            ((data['availability']['is_accepting']).as_boolean()),
            postgresql_where=(data['availability']['is_accepting'] != None)
        ),
    )
    
    # Helper properties
    @property
    def account_status(self) -> str:
        return self.data.get('account', {}).get('status', 'pending_verification')
    
    @property
    def is_verified(self) -> bool:
        return self.account_status == 'verified'
    
    @property
    def is_accepting(self) -> bool:
        return self.data.get('availability', {}).get('is_accepting', True)
    
    @property
    def bio(self) -> str | None:
        return self.data.get('profile', {}).get('bio', {}).get('full')
    
    @property
    def short_bio(self) -> str | None:
        return self.data.get('profile', {}).get('bio', {}).get('short')
    
    @property
    def avg_rating(self) -> float | None:
        return self.data.get('stats', {}).get('avg_rating')
    
    @property
    def total_practices_held(self) -> int:
        return self.data.get('stats', {}).get('total_practices_held', 0)
    
    # Helper methods
    def set_availability(self, is_accepting: bool, note: str = ""):
        """Set availability status."""
        if 'availability' not in self.data:
            self.data['availability'] = {}
        
        self.data['availability']['is_accepting'] = is_accepting
        self.data['availability']['note'] = note
    
    def update_stats(self, **kwargs):
        """Update stats fields."""
        if 'stats' not in self.data:
            self.data['stats'] = {}
        
        self.data['stats'].update(kwargs)
    
    def verify(self, admin_id: str, notes: str = ""):
        """Verify master profile (admin action)."""
        if 'account' not in self.data:
            self.data['account'] = {}
        if 'verification' not in self.data['account']:
            self.data['account']['verification'] = {}
        
        self.data['account']['status'] = 'verified'
        self.data['account']['verification']['verified_at'] = datetime.utcnow().isoformat()
        self.data['account']['verification']['verified_by'] = admin_id
        self.data['account']['verification']['notes'] = notes
    
    def suspend(self, admin_id: str, reason: str):
        """Suspend master profile (admin action)."""
        if 'account' not in self.data:
            self.data['account'] = {}
        if 'moderation' not in self.data['account']:
            self.data['account']['moderation'] = {}
        
        self.data['account']['status'] = 'suspended'
        self.data['account']['moderation']['suspended_at'] = datetime.utcnow().isoformat()
        self.data['account']['moderation']['suspended_by'] = admin_id
        self.data['account']['moderation']['suspension_reason'] = reason
```

---

## Usage Examples

### 1. Create master profile (pending verification)

```python
from models import User, MasterProfile

# User already exists
user = await db.get(User, user_id)

# Create master profile
master_profile = MasterProfile(
    user_id=user.id,
    data={
        "account": {
            "status": "pending_verification",
            "verification": {
                "submitted_at": datetime.utcnow().isoformat(),
                "documents": [
                    {
                        "type": "certification",
                        "name": "Yoga Alliance RYT-200",
                        "url": "s3://bucket/cert.pdf",
                        "uploaded_at": datetime.utcnow().isoformat()
                    }
                ]
            }
        },
        "profile": {
            "bio": {
                "short": "Experienced meditation teacher",
                "full": "I've been teaching meditation for 10 years..."
            },
            "approach_methods": ["Vipassana", "Mindfulness"],
            "certifications": [...]
        },
        "settings": {
            "accepts_groups": True,
            "accepts_one_on_one": True,
            "max_group_size": 20
        }
    }
)

db.add(master_profile)
await db.commit()
```

### 2. Admin verifies master

```python
# Admin endpoint
@router.post("/admin/masters/{master_id}/verify")
async def verify_master(
    master_id: UUID,
    verification: VerificationDecision,
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    master_profile = await db.get(MasterProfile, master_id)
    
    if verification.approved:
        master_profile.verify(
            admin_id=str(current_user.id),
            notes=verification.notes
        )
        
        await db.commit()
        
        # Send notification
        await notification_service.send(
            user_id=master_id,
            template="master_verified",
            variables={}
        )
        
        return {"status": "verified"}
    else:
        # Reject = ban
        master_profile.data['account']['status'] = 'banned'
        await db.commit()
        
        return {"status": "banned"}
```

### 3. Master toggles availability

```python
@router.patch("/masters/me/availability")
async def update_availability(
    update: AvailabilityUpdate,
    current_user: User = Depends(get_current_master),
    db: AsyncSession = Depends(get_db)
):
    master_profile = await db.get(MasterProfile, current_user.id)
    
    master_profile.set_availability(
        is_accepting=update.is_accepting,
        note=update.note or ""
    )
    
    await db.commit()
    
    return {
        "is_accepting": master_profile.is_accepting,
        "note": master_profile.data['availability'].get('note', '')
    }
```

### 4. Query verified masters who are accepting

```python
from sqlalchemy import select

# Find all verified masters accepting bookings
stmt = select(MasterProfile).where(
    MasterProfile.data['account']['status'].astext == 'verified',
    MasterProfile.data['availability']['is_accepting'].as_boolean() == True
)

masters = await db.scalars(stmt).all()
```

### 5. Update stats after practice

```python
# After practice completed
master_profile = await db.get(MasterProfile, practice.master_id)

current_total = master_profile.data.get('stats', {}).get('total_practices_held', 0)

master_profile.update_stats(
    total_practices_held=current_total + 1,
    monthly_practices=12,  # Calculated from practice count
    total_hours=master_profile.data['stats'].get('total_hours', 0) + practice.duration_minutes / 60
)

await db.commit()
```

---

## Migration from Native Columns (Future)

If in the future we decide to migrate some hot-path fields to native columns:

### Step 1: Add column
```sql
ALTER TABLE master_profiles 
  ADD COLUMN account_status VARCHAR(30);
```

### Step 2: Backfill from JSONB
```sql
UPDATE master_profiles 
SET account_status = data->'account'->>'status';

CREATE INDEX idx_master_account_status ON master_profiles (account_status);
```

### Step 3: Update code to use both
```python
@property
def account_status(self) -> str:
    # Try native column first
    if self._account_status:
        return self._account_status
    # Fallback to JSONB
    return self.data.get('account', {}).get('status', 'pending_verification')
```

### Step 4: Eventually remove from JSONB
```sql
UPDATE master_profiles 
SET data = data #- '{account,status}';
```

---

## Performance Considerations

### Query performance

**Bad (slow):**
```python
# Sequential scan
masters = await db.execute(
    select(MasterProfile).where(
        MasterProfile.data['account']['status'].astext == 'verified'
    )
)
```

**Good (uses index):**
```python
# Uses partial index idx_master_status
masters = await db.execute(
    select(MasterProfile).where(
        MasterProfile.data['account']['status'].astext == 'verified'
    )
)
# With proper index, this is fast (~10-20ms for 10k masters)
```

### Update performance

**Bad (full JSONB replace):**
```python
master_profile.data = {
    "account": {...},
    "availability": {...},
    ...
}
```

**Good (partial update):**
```python
master_profile.data['availability']['is_accepting'] = False
# OR using helper method
master_profile.set_availability(False, "On vacation")
```

---

## Validation

### Pydantic schemas for API

```python
from pydantic import BaseModel, Field

class MasterProfileCreate(BaseModel):
    bio_short: str = Field(max_length=200)
    bio_full: str = Field(max_length=2000)
    approach_methods: list[str] = Field(min_items=1, max_items=10)
    experience_years: int = Field(ge=0, le=100)
    certifications: list[dict]
    accepts_groups: bool = True
    accepts_one_on_one: bool = True
    max_group_size: int = Field(ge=1, le=100, default=20)

class AvailabilityUpdate(BaseModel):
    is_accepting: bool
    note: str = Field(max_length=500, default="")

class VerificationDecision(BaseModel):
    approved: bool
    notes: str = Field(max_length=1000, default="")
```

---

## Summary

**Benefits of JSONB approach:**
- ✅ Maximum flexibility (add fields without migrations)
- ✅ Clean schema (no NULL columns)
- ✅ Easy to structure data (nested objects)
- ✅ Safe migrations (just add keys to JSON)

**Trade-offs:**
- ⚠️ Slightly slower queries (2-3x vs native columns)
- ⚠️ Need GIN + partial indexes for performance
- ⚠️ Validation at application level (not database)

**For MVP (<10k masters):** JSONB is perfect choice

**For scale (100k+ masters):** Consider migrating hot-path fields (account_status, is_accepting) to native columns
