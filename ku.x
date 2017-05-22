#!/bin/bash
title="Keski-Uusimaa-Rastit"
#python parse3.py title=${title} date=6.4.2017     place="Tuusulan uimahalli" url="http://www.ku-rastit.net/tulokset/valiajat0604.html"
#python parse3.py title=${title} date=12.4.2017    place=Pilvijärvi           url="http://www.ku-rastit.net/tulokset/valiajat1204.html"
python parse3.py title=${title} date=20.4.2017    place=Martinkylä           url="http://www.ku-rastit.net/tulokset/valiajat2004.html" parser=regex
exit
python parse3.py title=${title} date=27.4.2017    place=Hakkari
python parse3.py title=${title} date=4.5.2017     place=Rusutjärvi
python parse3.py title=${title} date=11.5.2017    place=Nikkilä
python parse3.py title=${title} date=18.5.2017    place=Keinukallio
python parse3.py title=${title} date=25.5.2017    place=Varuskunta
python parse3.py title=${title} date=1.6.2017     place=Flisberget
python parse3.py title=${title} date=8.6.2017     place=Massby
python parse3.py title=${title} date=15.6.2017    place=Talma
python parse3.py title=${title} date=21.6.2017    place=Valkjärvi
python parse3.py title=${title} date=29.6.2017    place=Nahkela
python parse3.py title=${title} date=6.7.2017     place=Immersby
python parse3.py title=${title} date=13.7.2017    place=Bastmossen
python parse3.py title=${title} date=20.7.2017    place=Kummelberg
python parse3.py title=${title} date=27.7.2017    place=Vaunukangas
python parse3.py title=${title} date=3.8.2017     place=Linnanpelto
python parse3.py title=${title} date=10.8.2017    place=Kirkkokallio
python parse3.py title=${title} date=17.8.2017    place=Martinkylä
python parse3.py title=${title} date=24.8.2017    place="Joensuun tila"
python parse3.py title=${title} date=31.8.2017    place=Terrisuo
python parse3.py title=${title} date=7.9.2017     place="Solbeg, Paippinen"
python parse3.py title=${title} date=14.9.2017    place=Kellokoski
python parse3.py title=${title} date=21.9.2017    place=Mätäkivenmäki
python parse3.py title=${title} date=28.9.2017    place="Box, Skattåkersberg"
python parse3.py title=${title} date=5.10.2017    place=Tuomala
python parse3.py title=${title} date=12.10.2017   place=Isokytö
python parse3.py title=${title} date=19.10.2017   place=Keinukallio
exit
python print_contests.py title=${title} date=6.4.2017     place="Tuusulan uimahalli"
python print_contests.py title=${title} date=12.4.2017    place=Pilvijärvi
python print_contests.py title=${title} date=20.4.2017    place=Martinkylä
python print_contests.py title=${title} date=27.4.2017    place=Hakkari
python print_contests.py title=${title} date=4.5.2017     place=Rusutjärvi
python print_contests.py title=${title} date=11.5.2017    place=Nikkilä
python print_contests.py title=${title} date=18.5.2017    place=Keinukallio
python print_contests.py title=${title} date=25.5.2017    place=Varuskunta
python print_contests.py title=${title} date=1.6.2017     place=Flisberget
python print_contests.py title=${title} date=8.6.2017     place=Massby
python print_contests.py title=${title} date=15.6.2017    place=Talma
python print_contests.py title=${title} date=21.6.2017    place=Valkjärvi
python print_contests.py title=${title} date=29.6.2017    place=Nahkela
python print_contests.py title=${title} date=6.7.2017     place=Immersby
python print_contests.py title=${title} date=13.7.2017    place=Bastmossen
python print_contests.py title=${title} date=20.7.2017    place=Kummelberg
python print_contests.py title=${title} date=27.7.2017    place=Vaunukangas
python print_contests.py title=${title} date=3.8.2017     place=Linnanpelto
python print_contests.py title=${title} date=10.8.2017    place=Kirkkokallio
python print_contests.py title=${title} date=17.8.2017    place=Martinkylä
python print_contests.py title=${title} date=24.8.2017    place="Joensuun tila"
python print_contests.py title=${title} date=31.8.2017    place=Terrisuo
python print_contests.py title=${title} date=7.9.2017     place="Solbeg, Paippinen"
python print_contests.py title=${title} date=14.9.2017    place=Kellokoski
python print_contests.py title=${title} date=21.9.2017    place=Mätäkivenmäki
python print_contests.py title=${title} date=28.9.2017    place="Box, Skattåkersberg"
python print_contests.py title=${title} date=5.10.2017    place=Tuomala
python print_contests.py title=${title} date=12.10.2017   place=Isokytö
python print_contests.py title=${title} date=19.10.2017   place=Keinukallio
