#!/usr/bin/env python

'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
import json
from mock.mock import MagicMock, patch
from stacks.utils.RMFTestCase import *
from only_for_platform import not_for_platform, PLATFORM_WINDOWS

@not_for_platform(PLATFORM_WINDOWS)
class TestRangerAdmin(RMFTestCase):
  COMMON_SERVICES_PACKAGE_DIR = "RANGER/0.4.0/package"
  STACK_VERSION = "2.5"

  @patch("os.path.isfile")
  def test_configure_default(self, isfile_mock):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/ranger_admin.py",
      classname = "RangerAdmin",
      command = "configure",
      config_file="ranger-admin-default.json",
      stack_version = self.STACK_VERSION,
      target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_default()
    self.assertTrue(isfile_mock.called)
    self.assertNoMoreResources()

  @patch("os.path.isfile")    
  def test_start_default(self, isfile_mock):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/ranger_admin.py",
      classname = "RangerAdmin",
      command = "start",
      config_file="ranger-admin-default.json",
      stack_version = self.STACK_VERSION,
      target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_default()

    self.assertResourceCalled('Directory', '/var/log/ambari-logsearch-solr-client',
        owner = 'logsearch-solr',
        group = 'hadoop',
        create_parents = True,
        mode = 0755,
        cd_access = 'a',
    )
    self.assertResourceCalled('Directory', '/usr/lib/ambari-logsearch-solr-client',
        group = 'hadoop',
        cd_access = 'a',
        create_parents = True,
        mode = 0755,
        owner = 'logsearch-solr',
        recursive_ownership = True,
    )
    self.assertResourceCalled('File', '/usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh',
        content = StaticFile('/usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh'),
        owner = 'logsearch-solr',
        group = 'hadoop',
        mode = 0755,
    )
    self.assertResourceCalled('File', '/usr/lib/ambari-logsearch-solr-client/log4j.properties',
        owner = 'logsearch-solr',
        content = InlineTemplate(self.getConfig()['configurations']['logsearch-solr-client-log4j']['content']),
        group = 'hadoop',
        mode = 0644,
    )
    self.assertResourceCalled('File', '/var/log/ambari-logsearch-solr-client/solr-client.log',
        content = '',
        owner = 'logsearch-solr',
        group = 'hadoop',
        mode = 0664,
    )
    self.assertResourceCalledRegexp('^Execute$', '^export JAVA_HOME=/usr/jdk64/jdk1.7.0_45 ; /usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/ambari-solr --download-config --config-dir /tmp/solr_config_ranger_audits_0.[0-9]* --config-set ranger_audits --retry 30 --interval 5')
    self.assertResourceCalledRegexp('^Execute$', '^export JAVA_HOME=/usr/jdk64/jdk1.7.0_45 ; /usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/ambari-solr --upload-config --config-dir /usr/hdp/current/ranger-admin/contrib/solr_for_audit_setup/conf --config-set ranger_audits --retry 30 --interval 5')
    self.assertResourceCalledRegexp('^Directory$', '^/tmp/solr_config_ranger_audits_0.[0-9]*',
                                    action=['delete'],
                                    owner='ranger',
                                    create_parents=True)
    self.assertResourceCalledRegexp('^Execute$', '^export JAVA_HOME=/usr/jdk64/jdk1.7.0_45 ; /usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/ambari-solr --create-collection --collection ranger_audits --config-set ranger_audits --shards 1 --replication 1 --max-shards 1 --retry 5 --interval 10')

    self.assertResourceCalled('Execute', '/usr/bin/ranger-admin-start',
      environment = {'JAVA_HOME': u'/usr/jdk64/jdk1.7.0_45'},
      not_if = 'ps -ef | grep proc_rangeradmin | grep -v grep',
      user = 'ranger',
    )

    self.assertTrue(isfile_mock.called)
    self.assertNoMoreResources()

  def test_stop_default(self):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/ranger_admin.py",
      classname = "RangerAdmin",
      command = "stop",
      config_file="ranger-admin-default.json",
      stack_version = self.STACK_VERSION,
      target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assertResourceCalled('Execute', '/usr/bin/ranger-admin-stop',
      environment = {'JAVA_HOME': u'/usr/jdk64/jdk1.7.0_45'},
      user = 'ranger'
    )
    self.assertResourceCalled('File', '/var/run/ranger/rangeradmin.pid',
      action = ['delete']
    )
    self.assertNoMoreResources()

  @patch("os.path.isfile")    
  def test_configure_secured(self, isfile_mock):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/ranger_admin.py",
      classname = "RangerAdmin",
      command = "configure",
      config_file="ranger-admin-secured.json",
      stack_version = self.STACK_VERSION,
      target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_secured()
    self.assertTrue(isfile_mock.called)
    self.assertNoMoreResources()

  @patch("os.path.isfile")
  def test_start_secured(self, isfile_mock):
    self.executeScript(self.COMMON_SERVICES_PACKAGE_DIR + "/scripts/ranger_admin.py",
      classname = "RangerAdmin",
      command = "start",
      config_file="ranger-admin-secured.json",
      stack_version = self.STACK_VERSION,
      target = RMFTestCase.TARGET_COMMON_SERVICES
    )
    self.assert_configure_secured()

    self.assertResourceCalled('Directory', '/var/log/ambari-logsearch-solr-client',
        owner = 'logsearch-solr',
        group = 'hadoop',
        create_parents = True,
        mode = 0755,
        cd_access = 'a',
    )
    self.assertResourceCalled('Directory', '/usr/lib/ambari-logsearch-solr-client',
        group = 'hadoop',
        cd_access = 'a',
        create_parents = True,
        mode = 0755,
        owner = 'logsearch-solr',
        recursive_ownership = True,
    )
    self.assertResourceCalled('File', '/usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh',
        content = StaticFile('/usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh'),
        owner = 'logsearch-solr',
        group = 'hadoop',
        mode = 0755,
    )
    self.assertResourceCalled('File', '/usr/lib/ambari-logsearch-solr-client/log4j.properties',
        owner = 'logsearch-solr',
        content = InlineTemplate(self.getConfig()['configurations']['logsearch-solr-client-log4j']['content']),
        group = 'hadoop',
        mode = 0644,
    )
    self.assertResourceCalled('File', '/var/log/ambari-logsearch-solr-client/solr-client.log',
        content = '',
        owner = 'logsearch-solr',
        group = 'hadoop',
        mode = 0664,
    )
    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/conf/ranger_solr_jass.conf',
      content = Template('ranger_solr_jass_conf.j2'),
      owner = 'ranger',
    )
    self.assertResourceCalledRegexp('^Execute$', '^export JAVA_HOME=/usr/jdk64/jdk1.7.0_45 ; /usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/ambari-solr --download-config --config-dir /tmp/solr_config_ranger_audits_0.[0-9]* --config-set ranger_audits --retry 30 --interval 5')
    self.assertResourceCalledRegexp('^Execute$', '^export JAVA_HOME=/usr/jdk64/jdk1.7.0_45 ; /usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/ambari-solr --upload-config --config-dir /usr/hdp/current/ranger-admin/contrib/solr_for_audit_setup/conf --config-set ranger_audits --retry 30 --interval 5')
    self.assertResourceCalledRegexp('^Directory$', '^/tmp/solr_config_ranger_audits_0.[0-9]*',
                                    action=['delete'],
                                    owner='ranger',
                                    create_parents=True)
    self.assertResourceCalledRegexp('^Execute$', '^export JAVA_HOME=/usr/jdk64/jdk1.7.0_45 ; /usr/lib/ambari-logsearch-solr-client/solrCloudCli.sh --zookeeper-connect-string c6401.ambari.apache.org:2181/ambari-solr --create-collection --collection ranger_audits --config-set ranger_audits --shards 1 --replication 1 --max-shards 1 --retry 5 --interval 10')

    self.assertResourceCalled('Execute', '/usr/bin/ranger-admin-start',
      environment = {'JAVA_HOME': u'/usr/jdk64/jdk1.7.0_45'},
      not_if = 'ps -ef | grep proc_rangeradmin | grep -v grep',
      user = 'ranger',
    )

    self.assertTrue(isfile_mock.called)
    self.assertNoMoreResources()

  def assert_configure_default(self):
    self.assertResourceCalled('Directory', '/usr/hdp/current/ranger-admin/conf',
      owner = 'ranger',
      group = 'ranger',
      create_parents = True
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java-old.jar',
        action = ['delete'],
    )

    self.assertResourceCalled('File', '/tmp/mysql-connector-java.jar',
      content = DownloadSource('http://c6401.ambari.apache.org:8080/resources//mysql-connector-java.jar'),
      mode = 0644
    )

    self.assertResourceCalled('Execute', ('cp', '--remove-destination', '/tmp/mysql-connector-java.jar', '/usr/hdp/current/ranger-admin/ews/lib'),
      sudo = True,
      path = ['/bin', '/usr/bin/']
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java.jar',
      mode = 0644
    )

    self.assertResourceCalled('ModifyPropertiesFile', '/usr/hdp/current/ranger-admin/install.properties',
      properties = self.getConfig()['configurations']['admin-properties'],
      owner = 'ranger'
    )

    self.assertResourceCalled('ModifyPropertiesFile', '/usr/hdp/current/ranger-admin/install.properties',
      owner = 'ranger',
      properties = {'SQL_CONNECTOR_JAR': '/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java.jar'}
    )

    self.assertResourceCalled('File', '/usr/lib/ambari-agent/DBConnectionVerification.jar',
      content = DownloadSource('http://c6401.ambari.apache.org:8080/resources/DBConnectionVerification.jar'),
      mode = 0644
    )

    self.assertResourceCalled('Execute',
      '/usr/jdk64/jdk1.7.0_45/bin/java -cp /usr/lib/ambari-agent/DBConnectionVerification.jar:/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java.jar:/usr/hdp/current/ranger-admin/ews/lib/* org.apache.ambari.server.DBConnectionVerification \'jdbc:mysql://c6401.ambari.apache.org:3306/ranger01\' rangeradmin01 rangeradmin01 com.mysql.jdbc.Driver',
      path=['/usr/sbin:/sbin:/usr/local/bin:/bin:/usr/bin'],
      tries=5,
      try_sleep=10,
      environment = {}
    )

    self.assertResourceCalled('Execute', ('ln', '-sf', '/usr/hdp/current/ranger-admin/ews/webapp/WEB-INF/classes/conf', '/usr/hdp/current/ranger-admin/conf'),
      not_if = 'ls /usr/hdp/current/ranger-admin/conf',
      only_if = 'ls /usr/hdp/current/ranger-admin/ews/webapp/WEB-INF/classes/conf',
      sudo = True
    )

    self.assertResourceCalled('Directory', '/usr/hdp/current/ranger-admin/',
      owner='ranger',
      group='ranger',
      recursive_ownership = True
    )

    self.assertResourceCalled('Directory', '/var/run/ranger',
      mode=0755,
      owner = 'ranger',
      group = 'hadoop',
      cd_access = "a",
      create_parents=True
    )

    self.assertResourceCalled('Directory', '/var/log/ranger/admin',
      owner='ranger',
      group='ranger',
      create_parents = True,
      cd_access = 'a',
      mode = 0755
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/conf/ranger-admin-env-logdir.sh',
      content = 'export RANGER_ADMIN_LOG_DIR=/var/log/ranger/admin',
      owner = 'ranger',
      group = 'ranger',
      mode = 0755
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/conf/ranger-admin-default-site.xml',
      owner = 'ranger',
      group = 'ranger'
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/conf/security-applicationContext.xml',
      owner = 'ranger',
      group = 'ranger'
    )

    self.assertResourceCalled('Execute', ('ln', '-sf', '/usr/hdp/current/ranger-admin/ews/ranger-admin-services.sh', '/usr/bin/ranger-admin'),
      not_if = 'ls /usr/bin/ranger-admin',
      only_if = 'ls /usr/hdp/current/ranger-admin/ews/ranger-admin-services.sh',
      sudo = True
    )

    self.assertResourceCalled('XmlConfig', 'ranger-admin-site.xml',
      owner = 'ranger',
      group = 'ranger',
      conf_dir = '/usr/hdp/current/ranger-admin/conf',
      configurations = self.getConfig()['configurations']['ranger-admin-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['ranger-admin-site'],
      mode = 0644
    )

    self.assertResourceCalled('Directory', '/usr/hdp/current/ranger-admin/conf/ranger_jaas',
      owner ='ranger',
      group ='ranger',
      mode = 0700
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/ews/webapp/WEB-INF/log4j.properties',
      owner = 'ranger',
      group = 'ranger',
      content = self.getConfig()['configurations']['admin-log4j']['content'],
      mode = 0644
    )

    self.assertResourceCalled('Execute', ('/usr/jdk64/jdk1.7.0_45/bin/java', '-cp', '/usr/hdp/current/ranger-admin/cred/lib/*', 'org.apache.ranger.credentialapi.buildks', 'create', 'rangeradmin', '-value', 'rangeradmin01', '-provider', 'localjceks://file/etc/ranger/admin/rangeradmin.jceks'),
      environment = {'JAVA_HOME': u'/usr/jdk64/jdk1.7.0_45'},
      logoutput=True,
      sudo = True
    )

    self.assertResourceCalled('File', '/etc/ranger/admin/rangeradmin.jceks',
      owner = 'ranger',
      group = 'ranger',
      mode = 0640
    )

    self.assertResourceCalled('XmlConfig', 'core-site.xml',
      owner = 'ranger',
      group = 'ranger',
      conf_dir = '/usr/hdp/current/ranger-admin/conf',
      configurations = self.getConfig()['configurations']['core-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['core-site'],
      mode = 0644
    )

  def assert_configure_secured(self):

    self.assertResourceCalled('Directory', '/usr/hdp/current/ranger-admin/conf',
      owner = 'ranger',
      group = 'ranger',
      create_parents = True
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java-old.jar',
        action = ['delete'],
    )

    self.assertResourceCalled('File', '/tmp/mysql-connector-java.jar',
      content = DownloadSource('http://c6401.ambari.apache.org:8080/resources//mysql-connector-java.jar'),
      mode = 0644
    )

    self.assertResourceCalled('Execute', ('cp', '--remove-destination', '/tmp/mysql-connector-java.jar', '/usr/hdp/current/ranger-admin/ews/lib'),
      sudo = True,
      path = ['/bin', '/usr/bin/']
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java.jar',
      mode = 0644
    )

    self.assertResourceCalled('ModifyPropertiesFile', '/usr/hdp/current/ranger-admin/install.properties',
      properties = self.getConfig()['configurations']['admin-properties'],
      owner = 'ranger'
    )

    self.assertResourceCalled('ModifyPropertiesFile', '/usr/hdp/current/ranger-admin/install.properties',
      owner = 'ranger',
      properties = {'SQL_CONNECTOR_JAR': '/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java.jar'}
    )

    self.assertResourceCalled('File', '/usr/lib/ambari-agent/DBConnectionVerification.jar',
      content = DownloadSource('http://c6401.ambari.apache.org:8080/resources/DBConnectionVerification.jar'),
      mode = 0644
    )

    self.assertResourceCalled('Execute',
      '/usr/jdk64/jdk1.7.0_45/bin/java -cp /usr/lib/ambari-agent/DBConnectionVerification.jar:/usr/hdp/current/ranger-admin/ews/lib/mysql-connector-java.jar:/usr/hdp/current/ranger-admin/ews/lib/* org.apache.ambari.server.DBConnectionVerification \'jdbc:mysql://c6401.ambari.apache.org:3306/ranger01\' rangeradmin01 rangeradmin01 com.mysql.jdbc.Driver',
      path=['/usr/sbin:/sbin:/usr/local/bin:/bin:/usr/bin'],
      tries=5,
      try_sleep=10,
      environment = {}
    )

    self.assertResourceCalled('Execute', ('ln', '-sf', '/usr/hdp/current/ranger-admin/ews/webapp/WEB-INF/classes/conf', '/usr/hdp/current/ranger-admin/conf'),
      not_if = 'ls /usr/hdp/current/ranger-admin/conf',
      only_if = 'ls /usr/hdp/current/ranger-admin/ews/webapp/WEB-INF/classes/conf',
      sudo = True
    )

    self.assertResourceCalled('Directory', '/usr/hdp/current/ranger-admin/',
      owner='ranger',
      group='ranger',
      recursive_ownership = True
    )

    self.assertResourceCalled('Directory', '/var/run/ranger',
      mode=0755,
      owner = 'ranger',
      group = 'hadoop',
      cd_access = "a",
      create_parents=True
    )

    self.assertResourceCalled('Directory', '/var/log/ranger/admin',
      owner='ranger',
      group='ranger',
      create_parents = True,
      cd_access = 'a',
      mode = 0755
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/conf/ranger-admin-env-logdir.sh',
      content = 'export RANGER_ADMIN_LOG_DIR=/var/log/ranger/admin',
      owner = 'ranger',
      group = 'ranger',
      mode = 0755
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/conf/ranger-admin-default-site.xml',
      owner = 'ranger',
      group = 'ranger'
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/conf/security-applicationContext.xml',
      owner = 'ranger',
      group = 'ranger'
    )

    self.assertResourceCalled('Execute', ('ln', '-sf', '/usr/hdp/current/ranger-admin/ews/ranger-admin-services.sh', '/usr/bin/ranger-admin'),
      not_if = 'ls /usr/bin/ranger-admin',
      only_if = 'ls /usr/hdp/current/ranger-admin/ews/ranger-admin-services.sh',
      sudo = True
    )

    self.assertResourceCalled('XmlConfig', 'ranger-admin-site.xml',
      owner = 'ranger',
      group = 'ranger',
      conf_dir = '/usr/hdp/current/ranger-admin/conf',
      configurations = self.getConfig()['configurations']['ranger-admin-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['ranger-admin-site'],
      mode = 0644
    )

    self.assertResourceCalled('Directory', '/usr/hdp/current/ranger-admin/conf/ranger_jaas',
      owner ='ranger',
      group ='ranger',
      mode = 0700
    )

    self.assertResourceCalled('File', '/usr/hdp/current/ranger-admin/ews/webapp/WEB-INF/log4j.properties',
      owner = 'ranger',
      group = 'ranger',
      content = self.getConfig()['configurations']['admin-log4j']['content'],
      mode = 0644
    )

    self.assertResourceCalled('Execute', ('/usr/jdk64/jdk1.7.0_45/bin/java', '-cp', '/usr/hdp/current/ranger-admin/cred/lib/*', 'org.apache.ranger.credentialapi.buildks', 'create', 'rangeradmin', '-value', 'rangeradmin01', '-provider', 'localjceks://file/etc/ranger/admin/rangeradmin.jceks'),
      environment = {'JAVA_HOME': u'/usr/jdk64/jdk1.7.0_45'},
      logoutput=True,
      sudo = True
    )

    self.assertResourceCalled('File', '/etc/ranger/admin/rangeradmin.jceks',
      owner = 'ranger',
      group = 'ranger',
      mode = 0640
    )

    self.assertResourceCalled('XmlConfig', 'core-site.xml',
      owner = 'ranger',
      group = 'ranger',
      conf_dir = '/usr/hdp/current/ranger-admin/conf',
      configurations = self.getConfig()['configurations']['core-site'],
      configuration_attributes = self.getConfig()['configuration_attributes']['core-site'],
      mode = 0644
    )    