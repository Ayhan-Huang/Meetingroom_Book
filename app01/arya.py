#! user/bin/env python
# -*- coding: utf-8 -*-

from arya.service import sites
from . import models
from django.utils.safestring import mark_safe


class StaffConfig(sites.AryaConfig):
    def show_role(self,obj=None,is_header=False):
        if is_header:
            return '用户角色'
        roles = obj.auth.roles.all() # 一对一正向查询 --》 多对多查询
        list = []
        for role in roles:
            tpl = '<span syle="margin:3px">{role}</span>'.format(role=role.title)
            list.append(tpl)
        return mark_safe(''.join(list))

    list_display = ['username', show_role]


class MeetingRoomConfig(sites.AryaConfig):
    list_display = ['room_number', 'desc']


class BookingRecordConfig(sites.AryaConfig):
    list_display = ['theme', 'proposer', 'meeting_room']

sites.site.register(models.Staff, StaffConfig)
sites.site.register(models.MeetingRoom, MeetingRoomConfig)
sites.site.register(models.BookingRecord, BookingRecordConfig)