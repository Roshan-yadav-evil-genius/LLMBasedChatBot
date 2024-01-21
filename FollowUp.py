from datetime import datetime,timedelta
from SettingLoder import LastMessage
from rich import print
from DBPipeline import DBInstance

class FollowUp:
    def __init__(self,userid):
        self.userid=userid
        self.db = DBInstance()
        self.FOLLOWUPSETTING,self.rowid  = self.db.getFollowUPTrackByUserId(userid)


    def GetFollowUpTimeTrack(self,createdon):
        """Compute the difference between past time and current time objects."""
        delta = datetime.now()-datetime.strptime(createdon, "%Y-%m-%d %H:%M:%S")
        diff = {'years': 0, 'months': 0, 'days': 0,
                'hours': 0, 'minutes': 0, 'seconds': 0}
        diff = dict()
        diff['Years'] = delta.days // 365
        remainder = delta.days % 365
        diff['Months'] = remainder // 30
        diff['Days'] = remainder % 30
        diff['Hours'], rem = divmod(
            int(delta.seconds + delta.microseconds / 1000000), 3600)
        diff['Minutes'], _ = divmod(int(round(rem)), 60)
        return diff

    def wantFollowUp(self,timestamp: str):
        LastSeen = LastMessage(**self.GetFollowUpTimeTrack(timestamp))

        if self.FOLLOWUPSETTING.Minute.completed <= self.FOLLOWUPSETTING.Minute.count and LastSeen.Minutes >= self.FOLLOWUPSETTING.Minute.duration*self.FOLLOWUPSETTING.Minute.completed:
            self.FOLLOWUPSETTING.Minute.completed += 1
            self.db.updateFollowUpTrackByUserId(self.rowid,self.FOLLOWUPSETTING.to_jsonStr)
            print(f"[{self.FOLLOWUPSETTING.Minute.completed-1}] Minute Followup")
            print(LastSeen.__dict__)
            return f"{LastSeen.Minutes} Minutes"

        elif self.FOLLOWUPSETTING.Hour.completed <= self.FOLLOWUPSETTING.Hour.count and LastSeen.Hours >= self.FOLLOWUPSETTING.Hour.duration*self.FOLLOWUPSETTING.Hour.completed:
            self.FOLLOWUPSETTING.Hour.completed += 1
            self.db.updateFollowUpTrackByUserId(self.rowid,self.FOLLOWUPSETTING.to_jsonStr)
            print("Hour Followup")
            print(self.FOLLOWUPSETTING)
            print(LastSeen.__dict__)
            return f"{LastSeen.Hours} Hours"    


        elif self.FOLLOWUPSETTING.Day.completed <= self.FOLLOWUPSETTING.Day.count and LastSeen.Days >= self.FOLLOWUPSETTING.Day.duration*self.FOLLOWUPSETTING.Day.completed:
            self.FOLLOWUPSETTING.Day.completed += 1
            self.db.updateFollowUpTrackByUserId(self.rowid,self.FOLLOWUPSETTING.to_jsonStr)
            print("Day Followup")
            print(self.FOLLOWUPSETTING)
            print(LastSeen.__dict__)
            return f"{LastSeen.Days} Days"    


        elif self.FOLLOWUPSETTING.Month.completed <= self.FOLLOWUPSETTING.Month.count and LastSeen.Months >= self.FOLLOWUPSETTING.Month.duration*self.FOLLOWUPSETTING.Month.completed:
            self.FOLLOWUPSETTING.Month.completed += 1
            self.db.updateFollowUpTrackByUserId(self.rowid,self.FOLLOWUPSETTING.to_jsonStr)
            print("Month Followup")
            print(self.FOLLOWUPSETTING)
            print(LastSeen.__dict__)
            return f"{LastSeen.Months} Months"    


        elif self.FOLLOWUPSETTING.Year.completed <= self.FOLLOWUPSETTING.Year.count and LastSeen.Years >= self.FOLLOWUPSETTING.Year.duration*self.FOLLOWUPSETTING.Year.completed:
            self.FOLLOWUPSETTING.Year.completed += 1
            self.db.updateFollowUpTrackByUserId(self.rowid,self.FOLLOWUPSETTING.to_jsonStr)
            print("Year Followup")
            print(self.FOLLOWUPSETTING)
            print(LastSeen.__dict__)
            return f"{LastSeen.Years} Years"
        
        return False
            


