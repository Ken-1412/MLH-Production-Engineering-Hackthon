from datetime import datetime

from peewee import (
    AutoField,
    BooleanField,
    CharField,
    DateTimeField,
    IntegerField,
    TextField,
)

from app.database import BaseModel


class Url(BaseModel):
    id = AutoField()
    user_id = IntegerField(null=False)
    short_code = CharField(max_length=20, unique=True, null=False)
    original_url = TextField(null=False)
    title = CharField(max_length=255, null=False)
    is_active = BooleanField(default=True, null=False)
    created_at = DateTimeField(default=datetime.now, null=False)
    updated_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = "urls"

    @classmethod
    def safe_get(cls, record_id):
        """Handle both 'ID not found' and 'ID is not an integer' in one place."""
        try:
            return cls.get_by_id(int(record_id))
        except (cls.DoesNotExist, ValueError, TypeError):
            return None
