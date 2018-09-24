import pycurl
import sys 
import sqlite3

WEB_SITE = sys.argv[1]
DATABASE = sys.argv[2]

def main():
    conn = sqlite3.connect(DATABASE)
    table = """ CREATE TABLE IF NOT EXISTS performance_analysis (
			id integer PRIMARY KEY, 
			website text,
			dns_time text, 
			conn_time text, 
			ssl_handshake_time text,  
			time_before_ttfb text, 
			ttfb text, 
                        file_time text,
			total_time text, 
			remote_ip text, 
			local_ip text, 
			response_code text, 
			redirect_time text, 
			redirect_counts text,
                        content_type text);
                        """
    cur = conn.cursor()
    cur.execute(table)
    sqlcheck = """ select * from performance_analysis where website='%s' """ % WEB_SITE
    cur.execute(sqlcheck)
    rows = cur.fetchall()
    print len(rows)
    if len(rows) > 0: 
        sys.exit(0)
    c = pycurl.Curl()
    c.setopt(pycurl.URL, WEB_SITE)              #set url
    c.setopt(pycurl.FOLLOWLOCATION, 1)  
    c.setopt(c.HEADER, 1)
    c.setopt(c.NOBODY, 1)
    c.setopt(c.TIMEOUT, 25)
    #c.setopt(c.SSL_VERIFYPEER, 0)
    #c.setopt(c.SSL_VERIFYHOST, 0)
    content = c.perform()                                   #execute 
    dns_time = c.getinfo(pycurl.NAMELOOKUP_TIME)            #save the amount of time for DNS query
    conn_time = c.getinfo(pycurl.CONNECT_TIME)              #TCP/IP 3-way handshaking time
    ssl_handshake_time = c.getinfo(pycurl.APPCONNECT_TIME)  #time to ssl handshake
    time_before_ttfb = c.getinfo(pycurl.PRETRANSFER_TIME)   #time before TTFB
    ttfb = c.getinfo(pycurl.STARTTRANSFER_TIME)             #time-to-first-byte time
    response_code = c.getinfo(pycurl.RESPONSE_CODE)         #http response code
    file_time = c.getinfo(pycurl.INFO_FILETIME)             #This should count the amount of time of file transfert but it doesn't work a I expected
    total_time =  c.getinfo(pycurl.TOTAL_TIME)              #total maount of time the connection kept
    request_size = c.getinfo(pycurl.REQUEST_SIZE)           #
    remote_ip = c.getinfo(pycurl.PRIMARY_IP)                #
    local_ip = c.getinfo(pycurl.LOCAL_IP)                   #
    content_type = c.getinfo(pycurl.CONTENT_TYPE)           #
    redirect_time = c.getinfo(pycurl.REDIRECT_TIME)         #time spent for redirects while loading a landing page
    redirect_counts = c.getinfo(pycurl.REDIRECT_COUNT)      #
    c.close()                                               #close http connection
    delta_time = total_time - ttfb

    data_insert = ( WEB_SITE , dns_time , conn_time , ssl_handshake_time , time_before_ttfb , ttfb , file_time, total_time, remote_ip, local_ip , response_code , redirect_time, redirect_counts , content_type)
    sql_insert = """ insert into performance_analysis (website, dns_time , conn_time, ssl_handshake_time , time_before_ttfb , ttfb , file_time, total_time, remote_ip, local_ip , response_code , redirect_time, redirect_counts, content_type) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?) """
    
    cur.execute(sql_insert,data_insert)
    
    conn.commit()
    conn.close()
if __name__ == "__main__":    
    main()
