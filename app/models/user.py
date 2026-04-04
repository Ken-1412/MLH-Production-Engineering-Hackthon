from datetime import datetime

from peewee import AutoField, CharField, DateTimeField

from app.database import BaseModel


class User(BaseModel):
    id = AutoField()
    username = CharField(max_length=50, unique=True, null=False)
    email = CharField(max_length=255, unique=True, null=False)
    created_at = DateTimeField(default=datetime.now, null=False)

    class Meta:
        table_name = "users"

    @classmethod
    def safe_get(cls, record_id):
        """Handle both 'ID not found' and 'ID is not an integer' in one place."""
        try:
            return cls.get_by_id(int(record_id))
        except (cls.DoesNotExist, ValueError, TypeError):
            return None
