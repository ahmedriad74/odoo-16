import oerplib
import time
import sys
import os
import psycopg2
import base64
from oerplib import rpc
from datetime import datetime
from dateutil.relativedelta import relativedelta

installed_modules=[
'sale_management'
]
except_modules=[
'hrms_dashboard',
'ohrms_core',
'hr_employee_transfer',
'automatic_payroll',
'front_office_management',
'hr_reminder',
'hr_resignation',
'oh_hr_zk_attendance',
'ohrms_overtime',
'hr_reward_warning',
'event',
'project',
'sale_timesheet',
'boraq_company_branches',
'hr_employee_shift',
'hr_zk_attendance'
]
modules_list=os.listdir('/mnt/extra-addons')
modules_list.extend(installed_modules)
modules = [x for x in modules_list if x not in except_modules]
url = sys.argv[1] if len(sys.argv) > 1 else 'web'
database_password = os.environ.get('ADMIN_PASSWORD', 'admin')
database_name = os.environ.get('DB_NAME', 'default')
master_password = os.environ.get('DB_MASTER_PASSWORD', "admin")
IS_RESTORE_CUSTOM_DB = True if os.environ.get('RESTORE_CUSTOM_DB', '1') == '1' else False
print "Connect ", url
oerp = oerplib.OERP(server=url, protocol='xmlrpc', port=8069)
oerp.config['timeout'] = 60000
print "Get databases"
databases = oerp.db.list()
if database_name not in databases :
  if not IS_RESTORE_CUSTOM_DB: 
    print "Create Database"
    oerp.db.create_database(master_password, database_name, True, 'en_US', database_password)
  else:
    print "restore backup"
    with open("restore_custom_db.zip", "rb") as db_backup:
      db_base=base64.b64encode(db_backup.read())
      oerp.db.restore(master_password, database_name,db_base)
  time.sleep(60)
databases = oerp.db.list()
print databases
for db in databases:
  print db +" login"
  cnt = rpc.ConnectorJSONRPC('web',timeout=30000, port=8069)
  cnt.proxy.web.session.authenticate(db=db, login='admin', password=database_password)
  print "Update modules list"
  upgrade_module_instance = cnt.proxy.web.dataset.call(model='base.module.update', method='create', args=[{}])
  cnt.proxy.web.dataset.call(model='base.module.update', method='update_module', args=[upgrade_module_instance['result']])
  #Query_Modules From DB
  install_module_ids = cnt.proxy.web.dataset.call(model='ir.module.module', method='search', args=[[('name', 'in', modules),('state', '!=', 'installed')]])
  upgrade_module_ids = cnt.proxy.web.dataset.call(model='ir.module.module', method='search', args=[[('name', 'in', modules),('state', '=', 'installed')]])
  install_module_objs = cnt.proxy.web.dataset.call(model='ir.module.module', method='read', args=[install_module_ids['result']])
  upgrade_module_objs = cnt.proxy.web.dataset.call(model='ir.module.module', method='read', args=[upgrade_module_ids['result']])
  if len(install_module_ids['result']) > 0:
      print("Installing modules:")
      tries = 0
      while True:
          try:
              tries += 1
              cnt.proxy.web.dataset.call(model='ir.module.module', method='button_immediate_install', args=[install_module_ids['result']])
              for obj in install_module_objs['result']:
                print "install module " + obj['name'] + " "+obj['installed_version']
          except Exception as e:
              if tries > 3:
                  raise e
          else:
              break

  if len(upgrade_module_ids['result']) > 0:
      print("upgrading modules:")
      tries = 0
      while True:
          try:
              tries += 1
              cnt.proxy.web.dataset.call(model='ir.module.module', method='button_immediate_upgrade', args=[upgrade_module_ids['result']])
              for obj in upgrade_module_objs['result']:
                print "upgrade module " + obj['name'] + " "+obj['installed_version']
          except Exception as e:
              if tries > 3:
                  raise e
          else:
              break
