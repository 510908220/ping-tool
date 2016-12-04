# -*- encoding: utf-8 -*-

import subprocess
import re
import yagmail
import datetime
import time
import logging
import sys

logging.basicConfig(level=logging.INFO)


class PingMonitor(object):
    def __init__(self, hosts, email_subject, email_recipient, email_user, email_password, email_host, email_port,
                 interval_sec=30):
        self.hosts = hosts
        self.interval_sec = interval_sec
        self.email_subject = email_subject
        self.email_recipient = email_recipient
        self.email_user = email_user
        self.email_password = email_password
        self.email_host = email_host
        self.email_port = email_port
        self.alert_template = """ <h1><span style="color: #5e9ca0;">官人,</span></h1>
<h1><span style="color: #5e9ca0;">&nbsp; &nbsp;朝廷</span><span style="color: #5e9ca0;">600里加急！</span>如下ip无法ping通:</h1>
<ol style="list-style: none; font-size: 14px; line-height: 32px; font-weight: bold;">
{content}</ol><p>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp;<strong>&nbsp;</strong></p>
<p><strong>by大清朝巡逻小组.{date}</strong><br /><strong>Enjoy!</strong></p>
<p><strong>&nbsp;</strong></p>
        """

    def _ping_ok(self, host):
        try:
            output = subprocess.check_output("ping -c 3 " + host, shell=True)
            ret = re.findall(r'(\d+) received', output)
            received_count = int(ret[0])
            return received_count > 0

        except:
            return False

    def _alert(self, bad_hosts):
        logging.warning("bad hosts:%s", ",".join(bad_hosts))
        contents = []
        for bad_host in bad_hosts:
            contents.append(
                '''<li style="clear: both;"><span style="color: #ff0000;">{host}</span></li>'''.format(host=bad_host)
            )

        yag = yagmail.SMTP(self.email_user, self.email_password, self.email_host, self.email_port)
        yag.send(self.email_recipient, self.email_subject,
                 self.alert_template.format(date=datetime.datetime.now(), content=" ".join(contents)))

    def _run(self):
        while 1:
            bad_hosts = []
            for host in self.hosts:
                bad_hosts.append(host) if not self._ping_ok(host) else ""

            if bad_hosts:
                self._alert(bad_hosts)
            logging.info("bad is:%s", bad_hosts)
            time.sleep(self.interval_sec)

    def ping(self):
        try:
            self._run()
        except:
            logging.exception('')
            return 1


if __name__ == "__main__":
    hosts = [
        "192.168.56.101",
        "192.168.56.102",
        "192.168.56.103",
        "192.168.56.104",
        "192.168.56.105",
    ]
    pm = PingMonitor(hosts,
                     email_subject=u'主机离线',
                     email_recipient='510908220@qq.com',
                     email_user='13417710900@163.com',
                     email_password='abcdefg123456',
                     email_host='smtp.163.com',
                     email_port=25)
    sys.exit(pm.ping())
