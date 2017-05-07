grep AddTrack insert.sql 
cat insert.sql |sed -r 's/[0-9]/0/g' |sort |uniq --count |grep -v "1 CALL AddPerf" |grep AddPerf

