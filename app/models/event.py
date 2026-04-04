import json
from datetime import datetime

from peewee import AutoField, CharField, DateTimeField, IntegerField, TextField

from app.database import BaseModel


class Event(BaseModel):
    id = AutoField()
    url_id = IntegerField(null=False)
    user_id = IntegerField(null=False)
    event_type = CharField(max_length=50, null=False)
    timestamp = DateTimeField(default=datetime.now, null=False)
    details = TextField(null=True)

    class Meta:
        table_name = "events"

    @classmethod
    def safe_get(cls, record_id):
        """Handle both 'ID not found' and 'ID is not an integer' in one place."""
        try:
            return cls.get_by_id(int(record_id))
        except (cls.DoesNotExist, ValueError, TypeError):
            return None

    def get_details(self):
        if self.details:
            try:
                return json.loads(self.details)
            except json.JSONDecodeError:
                return {}
        return {}
