from datetime import datetime
from datetime import timedelta
from typing import List
from booking.source.event import EventsSource
from ..model import Event, EventImpl
from .model import DatabaseEvent
from booking.utils.database import get_db


class DatabaseEventsSource(EventsSource):
    def __init__(self):
        db = get_db()
        db.create_table(DatabaseEvent, safe=True)
        self._db = db

    def add_event(self, event: Event):
        DatabaseEvent.get_or_create(name=event.get_name(),
                                    start=event.get_begin(), end=event.get_end(), desc=event.get_description(),
                                    classroom_identifier=event.get_classroom_identifier())

    def get_current_event(self, classroom_identifier: str, date_time: datetime) -> Event:
        events = DatabaseEvent.select() \
            .where(DatabaseEvent.start <= date_time,
                   DatabaseEvent.end > date_time,
                   DatabaseEvent.classroom_identifier == classroom_identifier)
        event = None
        if len(events) > 0:
            event = query_result_to_event(events[0])
        return event

    def get_all_events(self):
        return query_result_to_events(DatabaseEvent.select())

    def get_next_event(self, classroom_identifier: str, date_time: datetime) -> Event:
        events = DatabaseEvent.select() \
            .where(DatabaseEvent.start >= date_time, DatabaseEvent.classroom_identifier == classroom_identifier)
        event = None
        if len(events) > 0:
            event = query_result_to_event(events[0])
        return event

    def get_all_classroom_events(self, classroom_identifier: str):
        return query_result_to_events(DatabaseEvent.select()
                                      .where(DatabaseEvent.classroom_identifier == classroom_identifier))

    def get_today_classroom_events(self, classroom_identifier: str) -> List[Event]:
        start = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        end = datetime.today().replace(hour=23, minute=59, second=59, microsecond=0)
        return query_result_to_events(DatabaseEvent.select()
                                      .where(DatabaseEvent.classroom_identifier == classroom_identifier,
                                             DatabaseEvent.start >= start, DatabaseEvent.end <= end))

    def delete_old_events(self):
        old_time_value = datetime.now().replace(hour=23, minute=59, second=59, microsecond=0) - timedelta(days=1)
        DatabaseEvent.delete() \
            .where(DatabaseEvent.start <= old_time_value) \
            .execute()

    def delete_all_events(self):
        DatabaseEvent.delete().execute()

    def is_classroom_free(self, classroom_identifier: str, date_time: datetime) -> bool:
        return self.get_current_event(classroom_identifier, date_time) is None


def query_result_to_event(event: DatabaseEvent) -> Event:
    return EventImpl(str(event.name),
                     str(event.desc),
                     event.classroom_identifier,
                     event.start,
                     event.end)


def query_result_to_events(events: List[DatabaseEvent]) -> List[Event]:
    results = []
    for event in events:
        results.append(query_result_to_event(event))
    return results
