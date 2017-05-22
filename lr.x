#!/bin/bash
title="Länsirastit"

#python parse3.py title=${title} date=27.4.2017 place=Haukkalampi    url="http://ok77.fi/images/tulokset/lansirastit/2017/v170427.html"
#python parse3.py title=${title} date=4.5.2017  place=Kasavuori      url="http://ok77.fi/images/tulokset/lansirastit/2017/v170504.html"
#python parse3.py title=${title} date=11.5.2017 place=Oittaa         url="http://ok77.fi/images/tulokset/lansirastit/2017/v170511.html"
python parse3.py title=${title} date=18.5.2017 place=Kaitakorpi     url="http://ok77.fi/images/tulokset/lansirastit/2017/v170518.html"
exit
python parse3.py title=${title} date=25.5.2017 place=Hanikka
python parse3.py title=${title} date=1.6.2017  place=Puolarmaari
python parse3.py title=${title} date=8.6.2017  place=Kellonummi
python parse3.py title=${title} date=15.6.2017 place=Lahnus
python parse3.py title=${title} date=3.8.2017  place=Olari
python parse3.py title=${title} date=10.8.2017 place=Lahnus
python parse3.py title=${title} date=17.8.2017 place=Kaitakorpi
python parse3.py title=${title} date=24.8.2017 place=Hanikka
python parse3.py title=${title} date=31.8.2017 place=Kellonummi
python parse3.py title=${title} date=7.9.2017  place=Oittaa
python parse3.py title=${title} date=14.9.2017 place=Haukkalampi
python parse3.py title=${title} date=21.9.2017 place=Kasavuori
exit

python print_contests.py title=${title} date=27.4.2017 place=Haukkalampi
python print_contests.py title=${title} date=4.5.2017  place=Kasavuori
python print_contests.py title=${title} date=11.5.2017 place=Oittaa
python print_contests.py title=${title} date=18.5.2017 place=Kaitakorpi
python print_contests.py title=${title} date=25.5.2017 place=Hanikka
python print_contests.py title=${title} date=1.6.2017  place=Puolarmaari
python print_contests.py title=${title} date=8.6.2017  place=Kellonummi
python print_contests.py title=${title} date=15.6.2017 place=Lahnus
python print_contests.py title=${title} date=3.8.2017  place=Olari
python print_contests.py title=${title} date=10.8.2017 place=Lahnus
python print_contests.py title=${title} date=17.8.2017 place=Kaitakorpi
python print_contests.py title=${title} date=24.8.2017 place=Hanikka
python print_contests.py title=${title} date=31.8.2017 place=Kellonummi
python print_contests.py title=${title} date=7.9.2017  place=Oittaa
python print_contests.py title=${title} date=14.9.2017 place=Haukkalampi
python print_contests.py title=${title} date=21.9.2017 place=Kasavuori
exit

