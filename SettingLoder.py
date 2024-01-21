from typing import Any, Dict, Optional
from typing import Dict
from dataclasses import dataclass,field
import json
import yaml


with open("settings.yaml", 'r') as settingFileStream:
    SETTING_FILE_STREAM = yaml.safe_load(settingFileStream)

@dataclass
class LastMessage:
    Minutes: int = 0
    Hours: int = 0
    Days: int = 0
    Months: int = 0
    Years: int = 0


@dataclass
class TimePeriod:
    duration: int = 0
    count: int = 0
    completed: int = 1

    def to_dict(self):
        return self.__dict__


@dataclass
class FollowUp:
    Minute: TimePeriod = field(default_factory=TimePeriod)
    Hour: TimePeriod = field(default_factory=TimePeriod)
    Day: TimePeriod = field(default_factory=TimePeriod)
    Month: TimePeriod = field(default_factory=TimePeriod)
    Year: TimePeriod = field(default_factory=TimePeriod)

    @property
    def to_dict(self) -> Dict[str, Optional[Dict[str, Any]]]:
        return {k: v.__dict__ if v else None for k, v in vars(self).items()}

    @property
    def to_jsonStr(self) -> str:
        return json.dumps(self.to_dict)


def parseFollowUpSetting(data):
    result = FollowUp()
    if 'Minute' in data:
        if data['Minute']['duration'] and data['Minute']['count']:
            result.Minute = TimePeriod(**data['Minute'])
    if 'Hour' in data:
        if data['Hour']['duration'] and data['Hour']['count']:
            result.Hour = TimePeriod(**data['Hour'])
    if 'Day' in data:
        if data['Day']['duration'] and data['Day']['count']:
            result.Day = TimePeriod(**data['Day'])
    if 'Month' in data:
        if data['Month']['duration'] and data['Month']['count']:
            result.Month = TimePeriod(**data['Month'])
    if 'Year' in data:
        if data['Year']['duration'] and data['Year']['count']:
            result.Year = TimePeriod(**data['Year'])
    return result



FOLLOWUPSETTING = parseFollowUpSetting(SETTING_FILE_STREAM['FollowUpDurations'])

BOT_WELCOME_MESSAGE = SETTING_FILE_STREAM['WelcomeMsg']

BOT_PERSONA = SETTING_FILE_STREAM['ChatBotPersona']

WAIT_FOR_RESPONSE = SETTING_FILE_STREAM['WAIT_FOR_RESPONSE']

USER_PERSEPECTIVE_RULE = SETTING_FILE_STREAM['HighPriorityUserPersepectiveRule']