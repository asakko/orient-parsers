# -*- coding: utf-8 -*-
import sys
kwargs  = dict(x.split('=', 1) for x in sys.argv[1:])
title   = kwargs.pop("title", "").upper()
place   = kwargs.pop("place", "").upper()
date    = kwargs.pop("date", "1.1.1982")
datestr = '%04u-%02u-%02u' % (int(date.split(".")[2]), int(date.split(".")[1]), int(date.split(".")[0]))
str0 = "CALL AddContest('%s', '%s', '%s', 'NULL', @contest_id);" % (title, place, datestr)
print(str0)
