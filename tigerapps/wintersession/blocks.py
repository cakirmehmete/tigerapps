import datetime
from dateutil import parser
from itertools import tee, izip
import re

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

dayofweek_order = ["Su", "M","Tu","W","Th","F","Sa"]

def friendly_to_blocks(s):
    # split into groups by &
    meetings = s.split('&')
    all_blocks = []
    for m in meetings:
        days = re.split('\d.*', m)[0].strip()
        times = re.search('\d.*', m).group().strip()

        # days
        days = re.split('\W+', days)
        days_of_week = ['%s' % dayofweek_order.index(d) for d in days]

        # times
        time_blocks = []
        times = re.split('-', times)

        assert len(times) == 2 # need start and end time only
        start, end = [parser.parse(t) for t in times]
        while start < end:
            # loop through half-hour slices
            start_hour = '%02d' % start.hour # 0-padded 24-hr start hour
            half_hour_bits = '0' if start.minute == 0 else '5' # 0 or 5
            time_blocks.append(start_hour + half_hour_bits)
            start += datetime.timedelta(minutes = 30)

        # make blocks
        blocks = []
        for day in days_of_week:
            for time_block in time_blocks:
                blocks.append(day + time_block)

        all_blocks += blocks
    return [int(b) for b in all_blocks]

def blocks_to_friendly(blocks):
    if blocks is None or not isinstance(blocks, list) :
        return blocks
    blocks = [int(b) for b in blocks]
    blocks = sorted(blocks) # arrange by day

    # collapse blocks
    start_blocks = []
    end_blocks = [] # note that real end time will be 30 mins after final block

    continuing_a_span = False
    for b1, b2 in pairwise(blocks):
        if not continuing_a_span:
            start_blocks.append(b1)
            continuing_a_span = True
        b1_day, b2_day = str(b1)[0], str(b2)[0]
        b1_hour, b2_hour = int(str(b1)[1:]), int(str(b2)[1:]) # parse times as ints: 100, 105, 110, 115,...
        if b1_day != b2_day or b2_hour - b1_hour > 5: #if b2 - b1 is not half hour or not same day
            # then b1 is an ending
            end_blocks.append(b1)
            continuing_a_span = False
    #manually add very last thing in blocks to end_blocks, because it must be an end block
    end_blocks.append(blocks[-1])

    # to get real end times, add 30 minutes to each end block
    end_blocks = [eb + 5 for eb in end_blocks]

    friendly_parts = []
    for start, end in zip(start_blocks, end_blocks):
        day_of_week = dayofweek_order[int(str(start)[0])]
        format_str = '%I:%M%p'
        start_time = datetime.time(hour = int(str(start)[1:3]), minute=(0 if str(start)[-1]=='0' else 30)).strftime(format_str)
        end_time = datetime.time(hour = int(str(end)[1:3]), minute=(0 if str(end)[-1]=='0' else 30)).strftime(format_str)
        friendly_parts.append('%s %s-%s' % (day_of_week, start_time, end_time))

    return ' & '.join(friendly_parts)
