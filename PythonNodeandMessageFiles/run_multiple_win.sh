#!/bin/bash

wcorr=68  # manual fix for vertical panels
hcorr=26  # manual fix for horizontal panels


tmps=$(LANG=C xrandr|grep -om1 'current.*,')
tmps=${tmps/,}
tmps=${tmps/current }
echo "screen resolution = $tmps pixels"
wscr=${tmps/ x*}
hscr=${tmps/*x }
wter=$(( (wscr-wcorr)/2 ))
hter=$(( (hscr-hcorr)/2 ))
echo "terminal width  = $wter pixels"
echo "terminal height = $hter pixels"

terminator --borderless --geometry="${wter}x${hter}+0+0" -x &
terminator --borderless --geometry="${wter}x${hter}+0-0" -x sleep 5 &
terminator --borderless --geometry="${wter}x${hter}-0+0" -x sleep 3 &
terminator --borderless --geometry="${wter}x${hter}-0-0" -x sleep 1
