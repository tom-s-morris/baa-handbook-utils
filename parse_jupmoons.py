#!/usr/bin/python3
# parse_jupmoons.py

# Copyright © 2026 Thomas Morris/British Astronomical Association

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the “Software”), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import csv

MONTH=0
DAY=1
HOUR=2
MINUTE=3
SATELLITE=4
EVENT=5
EVENT_TYPE=6

def sort_by_date(item):
    # Order by number of 'minutes' since beginning of the year using 31 days
    # per month.
    return int(item[MONTH]) * 44640 + int(item[DAY]) * 1440 + int(item[HOUR]) * 60 + int(item[MINUTE])

event_data = []

def find_next(event_enum, sat, event, event_type):
    idx = event_enum[0]
    for event2 in event_data[idx+1:]:
        if event2[SATELLITE] == sat and event2[EVENT] == event and event2[EVENT_TYPE] == event_type:
            return event2
    return None

# *********************************************************
# Read the Jupiter moon events data from a CSV file.
# The expected data format is that used in the ICCME table:

# https://ftp.imcce.fr/pub/ephem/satel/phenjupiter/ftp_jupiter_Events_UT_2026.txt
#   YY,month,[day,hour(UT),min(UT),satellite,event,event_type] repeated 4x
#   Some repeats may be blank.
# satellite: I=Io, II=Europa III=Ganymede IV=Callisto
# event: SH=shadow TR=transit EC=eclipse OC=occultation
# event_type: I=ingress E=egress D=disappearance R=reappearance
# *********************************************************
with open("ftp_jupiter_Events_UT_2026.csv") as csv_file:
    rd = csv.reader(csv_file, delimiter=",")
    next(rd, None)  # skip the header row
    for row in rd:
        year = row[0]
        month = row[1]
        for t in range(4):
            if row[2+t*6] != '':
                event_data.append([month] + row[2+t*6:8+t*6])

event_data.sort(key=sort_by_date)
print("Found ", len(event_data), " events.")
paired_events = []

# *********************************************************
# Match paired events
# (ingress, egress) or (disappearance, reappearance)
# *********************************************************
for ev_enum in enumerate(event_data):
    ev = ev_enum[1] # Current event
    sat = ev[SATELLITE]
    event = ev[EVENT]
    event_type = ev[EVENT_TYPE]

    ev2 = None
    if event_type == 'I':
        ev2 = find_next(ev_enum, sat, event, 'E')
    elif event == 'EC' and event_type == 'D':
        # Before opposition, the satellite disappears during eclipse and
        # reappears from occultation behind Jupiter.
        ev2 = find_next(ev_enum, sat, 'OC', 'R')
    elif event == 'OC' and event_type == 'D':
        # After opposition the sequence is reversed.
        ev2 = find_next(ev_enum, sat, 'EC', 'R')
    else:
        continue

    if ev2 is not None:
        paired_events.append( (ev,ev2) )
    else:
        print("Warning: no match found for: ", ev)

for ev_pair in paired_events:
    print(ev_pair)

