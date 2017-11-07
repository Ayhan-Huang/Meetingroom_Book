from django.db import models
from rbac.models import User


class Staff(models.Model):
    auth = models.ForeignKey(verbose_name='账户', to=User, null=True)
    username = models.CharField(verbose_name='用户名', max_length=32, null=True)
    # 剩下的用rbac中的User表字段

    def __str__(self):
        return self.username


class MeetingRoom(models.Model):
    room_number = models.CharField(verbose_name='会议室名称', max_length=32)
    desc = models.CharField(verbose_name='描述', max_length=128, null=True, blank=True)

    def __str__(self):
        return self.room_number


class BookingRecord(models.Model):
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    theme = models.CharField(verbose_name='会议主题',max_length=64)
    cause = models.TextField(verbose_name='预定事由', null=True)

    proposer = models.ForeignKey(verbose_name='预定人', to='Staff')
    meeting_room = models.ForeignKey(verbose_name='会议室', to='MeetingRoom')

    def __str__(self):
        return self.theme


