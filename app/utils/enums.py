from enum import Enum


class TaskRepeatRule(str, Enum):
    none = "none"
    daily = "daily"
    weekly = "weekly"
    custom = "custom"


class TaskStatusEnum(str, Enum):
    pending = "pending"
    done = "done"
    canceled = "canceled"


class ReminderScheduleType(str, Enum):
    interval = "interval"  
    weekly = "weekly"      
