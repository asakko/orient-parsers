# -*- coding: utf-8 -*-
import pymysql as MySQLdb
#import MySQLdb
#from string import join

class database:
    def __init__(self, host, user, db, passwd, port=3306):
        self.db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=port);
        self.cursor = self.db.cursor()

    def close(self):
        self.cursor.close()
        self.db.close()

    def AddContest(self, title, place, datestr, organizer, output=None):
        input_args = (title, place, datestr, organizer, 0);
        try:
            str0 = "CALL AddContest('%s', '%s', '%s', '%s', @contest_id)" % (title, place, datestr, organizer)
            print(str0.encode('utf-8'))
            if output is not None:
                ##output.write(str0.encode('utf-8')+';\n');
                output.write(str0+';\n');
            result_args = self.cursor.callproc("AddContest", input_args);
            self.cursor.execute('SELECT @_AddContest_4')
            contest_id = self.cursor.fetchall()[0][0]
            return contest_id
        except MySQLdb.IntegrityError as e:
            print("MySQLdb.IntegrityError (%s): %s" % (datestr, str(e[1])))
            pass

    def AddTrack(self, id_contest, length, tag=None, intervals=None, track_type='NORMAL', output=None):
        input_args = (id_contest, length, intervals, track_type, tag, 0);
        try:
            str0 = "CALL AddTrack(@contest_id, %9.2f, %i, '%s', '%s', @track_id)" % (length, intervals, tag, track_type)
            print(str0.encode('utf-8'))
            if output is not None:
                #output.write(str0.encode('utf-8')+';\n');
                output.write(str0+';\n');
            result_args = self.cursor.callproc("AddTrack", input_args);
            self.cursor.execute('SELECT @_AddTrack_5')
            track_id = self.cursor.fetchall()[0][0]
            return track_id
        except MySQLdb.IntegrityError as e:
            print("MySQLdb.IntegrityError (%f km): " % (length), e[1])
            return -1

    def CheckNumberOfIntervals(self, perf_id):
        input_args = (perf_id, 0)
        try:
            #print "CALL CheckNumberOfIntervals(performance_id=%u, correct_number)" % (perf_id)
            result_args = self.cursor.callproc("CheckNumberOfIntervals", input_args);
            self.cursor.execute('SELECT @_CheckNumberOfIntervals_1')
            correct_number = self.cursor.fetchall()[0][0]
            return correct_number
        except MySQLdb.IntegrityError as e:
            print("MySQLdb.IntegrityError: ", e[1])
            pass

    def AddPerformance(self, id_track, family_name, first_name, total_time_sec, datestr, output=None):
        input_args = (id_track, family_name, first_name, total_time_sec, datestr, 0)
        try:
            str0 = "CALL AddPerformance(@track_id, '%s', '%s', %u, '%s', @perf_id)" % (family_name, first_name, total_time_sec, datestr)
            print(str0.encode('utf-8'))
            if output is not None:
                #output.write(str0.encode('utf-8')+';\n');
                output.write(str0+';\n');
            result_args = self.cursor.callproc("AddPerformance", input_args);
            self.cursor.execute('SELECT @_AddPerformance_5')
            perf_id = self.cursor.fetchall()[0][0]
            return perf_id
        except MySQLdb.IntegrityError as e:
            print("MySQLdb.IntegrityError (%s %s): " % (family_name, first_name), e[1])
            pass

    def AddInterval(self, id_perf, id_track, interval_num, time_sec, output=None):
        if time_sec==0:
            return
        input_args = (id_perf, id_track, interval_num, time_sec)
        try:
            str0 = "CALL AddInterval(@perf_id, @track_id, %u, %u)" % (interval_num, time_sec)
            print(str0); ##.encode('utf-8'))
            if output is not None:
                #output.write(str0.encode('utf-8')+';\n');
                output.write(str0+';\n');
            self.cursor.callproc("AddInterval", input_args);
        except MySQLdb.IntegrityError as e:
            print("MySQLdb.IntegrityError at AddInterval (%u): " % (interval_num), e[1])
            raise e


    def query(self, cmd):
        # Print results
        #self.db.query(cmd);
        #r=self.db.store_result()
        ##d=r.fetch_row(how=1) #,maxrows=5);
        #d=r.fetchall()
        #output = []
        #for item in d:
        #    output.append(item)
        self.cursor.execute(cmd)
        output = self.cursor.fetchall()
        return output
        #db.commit()


    def commit(self):
        self.db.commit()



