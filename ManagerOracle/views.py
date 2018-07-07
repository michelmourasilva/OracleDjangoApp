from django.shortcuts import render
from django.views import View
import time
from subprocess import Popen, PIPE
import pandas as pd
import cx_Oracle
import os
import threading

#python -m pdb manage.py runserver
# import pdb;
# pdb.set_trace()


class ClsData(View):
    def __init__(self):
        self.v_data = time.strftime("%Y-%m-%d %H:%M:%S").replace('-', '')[:8]
        self.v_complete_data_number = time.strftime("%Y-%m-%d %H:%M:%S").replace('-', '').replace(':', '').replace(' '
                                       , '')
        self.v_complete_data_string = time.strftime("%Y-%m-%d %H:%M:%S")


class ClsForm(ClsData):
    def __init__(self, v_oracle_user, v_oracle_password, lst_servers, v_action, v_sql_file, v_csv_splitter,
                 v_sql_query, v_path_export
                 , lst_file_import, v_export_engine, v_sql_loader_splitter, v_sql_loader_owner, v_sql_loader_table,
                 v_sql_loader_head, v_sql_loader_constants):
        ClsData.__init__()
        self.v_oracle_user = v_oracle_user
        self.v_oracle_password = v_oracle_password
        self.lst_servers = lst_servers
        self.v_action = v_action
        self.v_sql_file = v_sql_file
        self.v_csv_splitter = v_csv_splitter
        self.v_sql_query = v_sql_query
        self.v_path_export = v_path_export
        self.lst_file_import = lst_file_import
        self.v_export_engine = v_export_engine
        self.v_sql_loader_splitter = v_sql_loader_splitter
        self.v_sql_loader_owner = v_sql_loader_owner
        self.v_sql_loader_table = v_sql_loader_table
        self.v_sql_loader_head = v_sql_loader_head
        self.v_sql_loader_constants = v_sql_loader_constants


class ClsInit(ClsForm):
    def __init__(self, v_oracle_user, v_oracle_password, lst_servers, v_action, v_sql_file, v_csv_splitter,
                 v_sql_query, v_path_export
                 , lst_file_import, v_export_engine, v_sql_loader_splitter, v_sql_loader_owner, v_sql_loader_table,
                 v_sql_loader_head, v_sql_loader_constants):
        ClsForm.__init__(self, v_oracle_user, v_oracle_password, lst_servers, v_action, v_sql_file,
                         v_csv_splitter, v_sql_query, v_path_export
                         , lst_file_import, v_export_engine, v_sql_loader_splitter, v_sql_loader_owner,
                         v_sql_loader_table, v_sql_loader_head, v_sql_loader_constants)

    def fnc_generate_connection_string(self, p_server):
        v_connection_string = '{0}/{1}@{2}'.format(self.v_oracle_user, self.v_oracle_password, p_server)
        return v_connection_string

    def fnc_execute_sql_file(self):
        v_sql_file = '@' + self.v_sql_file.replace('\\', '/').replace('"', '').replace(' ', '')
        try:
            for rgs_servers in self.lst_servers:
                if rgs_servers != 'VOID':
                    v_connection_string = self.fnc_generate_connection_string(rgs_servers)
                    v_session_terminal = Popen(['sqlplus', v_connection_string], stdin=PIPE, stdout=PIPE, stderr=PIPE)
                    v_session_terminal.stdin.write(b'SET ECHO ON;\n')
                    v_session_terminal.stdin.write(b'SET SERVEROUTPUT ON SIZE 1000000;\n')
                    v_session_terminal.stdin.write(v_sql_file.encode('utf-8'))
                    v_session_terminal_output, v_session_terminal_error = v_session_terminal.communicate()
                    v_session_terminal_output = v_session_terminal_output.decode('utf-8', errors="ignore")
                    ## Integration with INEP.demandas ------------------------------------
                    ## v_nu_demanda = re.findall(r'[0-9]{6}', v_sql_file)[0]
                    ## v_descricao_demanda = self.fnc_monta_cabecalho(rgs_servers, v_nu_demanda)
                    v_description_demands = ''
                    v_method_output = v_description_demands + v_session_terminal_output
                    v_file_name = fnc_generate_log(v_method_output, v_sql_file, rgs_servers)
            return 0, 'fnc_execute_sql_file', 'Process executed successfully.', None
        except Exception as e:
            return 1, 'fnc_execute_sql_file', e, None

    def fnc_export_query(self):
        v_count = 0
        v_file_progress = ''
        try:
            for rgs_servers in self.lst_servers:
                if rgs_servers != 'VOID':
                    v_connection_string = self.fnc_generate_connection_string(rgs_servers)
                    v_connection = cx_Oracle.connect(v_connection_string, encoding='latin1')
                    v_query_cursor = v_connection.cursor()
                    v_file_progress = self.v_complete_data_number + '_progress_.txt'
                    v_count = int(
                        pd.read_sql('SELECT COUNT(*) FROM ({table_name})'.format(table_name=self.v_sql_query),
                                    v_connection).values)
                    v_query_cursor.close()
                    thread = threading.Thread(target=self.fnc_export_query_background, args=(v_connection
                                                                                             , v_count, rgs_servers
                                                                                             , v_file_progress))
                    thread.daemon = True  # Daemonize thread
                    thread.start()  # Start the execution

            return None, 'fnc_export_query', v_file_progress, v_count
        except Exception as e:
            return 1, 'fnc_export_query', e, None

    def fnc_export_query_background(self, v_connection, v_count, v_server, v_file_progress):
        v_query_cursor = v_connection.cursor()
        v_query_cursor.execute(
            "alter session set nls_date_format = 'DD/MM/RRRR HH24:MI:SS' nls_date_language='ENGLISH'")
        with v_connection:
            df_result = pd.read_sql_query(self.v_sql_query, v_connection, chunksize=10000)
            v_export_file = self.v_path_export + '/' + \
                            self.v_complete_data_number + '_Export_' + v_server + '.csv'
            i = 0
            for chunk in df_result:
                i = i + 1
                if v_count >= 10000:
                    with open('./static/files/'+ v_file_progress, 'w+') as txt_export_progress:
                        txt_export_progress.write(str(i * 10000))
                    txt_export_progress.close()
                chunk.to_csv(v_export_file, sep=self.v_csv_splitter, index=False,
                             encoding='ISO-8859-1', mode='a')
        v_query_cursor.close()

    def fnc_execute_sqlloader(self):
        try:
            for rgs_servers in self.lst_servers:
                if rgs_servers != 'VOID':
                    lst_import_files = self.lst_file_import.replace(' ', '').split(',')
                    for rgs_files in lst_import_files:
                        v_sqlloader_file = self.fnc_generate_sqlloader_file(rgs_files, rgs_servers)
                        v_ctl_file = v_sqlloader_file[0]
                        v_fields = v_sqlloader_file[1].replace('char(', 'varchar2(')
                        v_original_file = v_sqlloader_file[2]

                        v_connection_string = self.fnc_generate_connection_string(rgs_servers)
                        v_connection = cx_Oracle.connect(v_connection_string, encoding='latin1')
                        v_query_cursor = v_connection.cursor()
                        with v_connection:
                            v_query = "Select 1 from dba_tables where table_name = '{0}' and owner = '{1}'".format(
                               self.v_sql_loader_table.upper(), self.v_sql_loader_owner.upper())
                            df_result = pd.read_sql_query(v_query, v_connection)
                            if len(df_result.index) == 0:
                                v_create_table = "create table {0}.{1} ( {2} )".format(self.v_sql_loader_owner,
                                                                                      self.v_sql_loader_table,
                                                                                      v_fields)
                                v_query_cursor.execute(v_create_table)
                                v_query_cursor.close()

                        v_log_file = v_original_file.replace('.txt', '_log.txt').replace('.csv','_log.txt')

                        v_session_terminal = Popen(
                           ['sqlldr', v_connection_string, 'control=' + v_ctl_file, 'log=' + v_log_file],
                           stdin=PIPE, stdout=PIPE, stderr=PIPE)
                        #v_session_terminal, v_session_terminal_error = v_session_terminal.communicate()

            return 0, 'fnc_execute_sqlloader', 'File Imported successfully.', None
        except Exception as e:
            return 1, 'fnc_execute_sqlloader', e, None

    def fnc_generate_sqlloader_file(self, p_file, p_server):
        try:

            v_sql_loader_splitter = bytes(self.v_sql_loader_splitter, 'utf-8').decode("unicode_escape")
            v_file = p_file.replace('\\', '/')
            v_sqlldr_template = './templates/SQLLOADER_TEMPLATE.ctl'

            v_sqlldr_template_copy = os.path.dirname(
                v_file) + '\\' + self.v_complete_data_number + '_' + self.v_sql_loader_table + '_' + p_server + '.ctl'

            if self.v_sql_loader_head == '' or self.v_sql_loader_head is None:
                v_file_opened = open(v_file, 'r')
                v_header = v_file_opened.readline()
                v_fields = v_header.replace('\n', ' char(4000) ')
                v_fields = v_fields.replace(v_sql_loader_splitter, ' char(4000),\n')

            else:
                v_fields = self.v_sql_loader_head

            if self.v_sql_loader_constants != '' and self.v_sql_loader_constants is not None:
                v_fields = v_fields + ' , ' + self.v_sql_loader_constants

            v_sqlldr_template_string = ''
            if os.path.exists(v_sqlldr_template):
                sqlldr_template_file = open(v_sqlldr_template, 'r')
                for line in sqlldr_template_file:
                    v_sqlldr_template_string = v_sqlldr_template_string + line
            v_sqlldr_template_string = v_sqlldr_template_string.replace('<FILE>', v_file)
            v_sqlldr_template_string = v_sqlldr_template_string.replace('<FIELDS>', v_fields)
            v_sqlldr_template_string = v_sqlldr_template_string.replace('<OWNER>', self.v_sql_loader_owner)
            v_sqlldr_template_string = v_sqlldr_template_string.replace('<TABLE>', self.v_sql_loader_table)

            if v_sql_loader_splitter == '\t':
                v_sql_loader_splitter = '\\t'

            v_sqlldr_template_string = v_sqlldr_template_string.replace('<SPLITTER>', v_sql_loader_splitter)
            v_sqlldr_template_string = v_sqlldr_template_string.replace('<SKIP>', '1')
            out_file = open(v_sqlldr_template_copy, 'w')
            out_file.write(v_sqlldr_template_string)
            out_file.close()
            return v_sqlldr_template_copy, v_fields, v_file

        except Exception as e:
            return 1, 'fnc_generate_sqlloader_file', e, None


def fnc_generate_log(p_method_output, p_file_name, p_servers):
    v_method_output = p_method_output.replace('\r\n\r\n\r\n', '\r\n')
    v_server = p_servers.replace('INEP_', '').replace('_D', '')
    v_file_name = p_file_name.replace('@', '').replace('.sql', '') + '_log_' + v_server + '.txt'
    with open(v_file_name, 'w') as the_file:
        the_file.write(v_method_output)
    return v_file_name


def show_object_servers(p_object):

    lst_servers_1 = []
    lst_servers_2 = []
    if p_object == 1:  # Return servers list
        lst_servers_1.append('Server1')
        lst_servers_2.append('Server2')
    elif p_object == 2:
        lst_servers_1.append('ORCL')
    return lst_servers_1, lst_servers_2


def request_form(request):
    v_oracle_user = request.GET.get('v_oracle_user')
    v_oracle_password = request.GET.get('v_oracle_password')
    lst_servers = request.GET.getlist('lst_servers')
    v_action = request.GET.get('v_action')
    v_sql_file = request.GET.get('v_sql_file')
    v_csv_splitter = request.GET.get('v_csv_splitter')
    v_sql_query = request.GET.get('v_sql_query')
    v_path_export = request.GET.get('v_path_export')
    lst_file_import = request.GET.get('lst_file_import')
    v_export_engine = request.GET.get('v_export_engine')
    v_sql_loader_splitter = request.GET.get('v_sql_loader_splitter')
    v_sql_loader_owner = request.GET.get('v_sql_loader_owner')
    v_sql_loader_table = request.GET.get('v_sql_loader_table')
    v_sql_loader_head = request.GET.get('v_sql_loader_head')
    v_sql_loader_constants = request.GET.get('v_sql_loader_constants')

    interface_cls_init = ClsInit(v_oracle_user, v_oracle_password, lst_servers, v_action, v_sql_file, v_csv_splitter,
                                 v_sql_query, v_path_export, lst_file_import, v_export_engine, v_sql_loader_splitter,
                                 v_sql_loader_owner, v_sql_loader_table,
                                 v_sql_loader_head, v_sql_loader_constants)

    v_return = (None, None)

    if v_action == '1':  # Execute sql file
        v_return = 'return.html', interface_cls_init.fnc_execute_sql_file()
    elif v_action == '0':  # Export query to csv files
        v_return = 'export.html', interface_cls_init.fnc_export_query()
    elif v_action == '2':  # Import text file
        v_return = 'return.html', interface_cls_init.fnc_execute_sqlloader()

    return render(request, v_return[0], {'v_return': v_return[1]})


def show_index(request):
    return render(request, 'index.html', {'lst_servers': show_object_servers(2)})
