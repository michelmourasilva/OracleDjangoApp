import os


class ClsTnsnames(object):
    ''''
    Chamada
    from pprint       import pprint
    from lib_database import Tnsnames

    tnsnnames = Tnsnames('/usr/lib/oracle/12.2/client64/network/admin')
    print('Connexions:')
    pprint(tnsnnames.connections)
    print('Aliases:')
    pprint(tnsnnames.aliases)
    print('Duplicates:')
    pprint(tnsnnames.duplicates)

    '''
    def __init__(self, file_path, file_name='tnsnames.ora'):
        self.file_path = file_path
        self.file_name = file_name
        self.load_file()

    def load_file(self):
        try:
            import pdb;
            pdb.set_trace()
            fhd = open(os.path.join(self.file_path, self.file_name), 'rt', encoding='utf-8')
            print(fhd)
        except:
            raise
        else:

            #Oracle doc : https://docs.oracle.com/cd/B28359_01/network.111/b28317/tnsnames.htm#NETRF007
            file_content = list()
            for l in fhd:
                l = " ".join(l.split()).strip(" \n")
                if len(l) > 0:
                    if "#" not in l:
                        file_content.append(l)
            fhd.close()
            file_content = " ".join(file_content)
            connections_list = dict()
            current_depth = 0
            current_word = ""
            current_keyword = ""
            name_to_register = ""
            is_in_add_list = False
            current_addr = dict()
            connections_aliases = dict()
            stop_registering = False
            connections_duplicates = list()
            for c in file_content:
                if c == " ":
                    pass
                elif c == "=":
                    current_keyword = str(current_word)
                    current_word = ""
                    if current_keyword == "ADDRESS_LIST":
                        is_in_add_list = True
                elif c == "(":
                    if current_depth == 0:
                        current_keyword = current_keyword.upper()
                        names_list = current_keyword.replace(" ", "").split(",")
                        if len(names_list) == 1:
                            name_to_register = names_list[0]
                        else:
                            name_to_register = None
                            # We use either the first name with at least
                            # a dot in it, or the longest one.
                            for n in names_list:
                                if "." in n:
                                    name_to_register = n
                                    break
                            else:
                                name_to_register = max(names_list, key=len)
                            names_list.remove(name_to_register)
                            for n in names_list:
                                if n in connections_aliases.keys():
                                    print("[ERROR] already registered alias:", n,
                                          ". Registered to:", connections_aliases[n],
                                          ". New:", name_to_register,
                                          ". This possible duplicate will not be registered.")
                                    connections_duplicates.append(n)
                                    stop_registering = True
                                else:
                                    connections_aliases[n] = name_to_register
                        if not stop_registering:
                            connections_list[name_to_register] = {"ADDRESS_LIST": list(),
                                                                  "CONNECT_DATA": dict(),
                                                                  "LAST_TEST_TS": None}
                        current_depth += 1
                    elif current_depth in [1, 2, 3]:
                        current_depth += 1
                    else:
                        print("[ERROR] Incorrect depth:", repr(current_depth), ". Current connection will not be registered" )
                        del connections_list[name_to_register]
                        stop_registering = True
                elif c == ")":
                    if current_depth == 1:
                        if stop_registering:
                            stop_registering = False
                        else:
                            # Before moving to next connection,
                            # we check that current connection
                            # have at least a HOST, and a SID or
                            # SERVICE_NAME
                            connection_is_valid = True
                            if isinstance(connections_list[name_to_register]["ADDRESS_LIST"], dict):
                                if "HOST" not in connections_list[name_to_register]["ADDRESS_LIST"].keys():
                                    print("[ERROR] Only one address defined, and no HOST defined. Current connection will not be registered:", name_to_register)
                                    connection_is_valid = False
                            elif isinstance(connections_list[name_to_register]["ADDRESS_LIST"], list):
                                for current_address in connections_list[name_to_register]["ADDRESS_LIST"]:
                                    if "HOST" in current_address.keys():
                                        break
                                else:
                                    print("[ERROR] Multiple addresses but none with HOST. Current connection will not be registered:", name_to_register)
                                    connection_is_valid = False
                            else:
                                print("[ERROR] Incorrect address format:", connections_list[name_to_register]["ADDRESS_LIST"], " Connection:", name_to_register)
                                connection_is_valid = False
                            if not connection_is_valid:
                                del connections_list[name_to_register]
                            else:
                                if "SERVICE_NAME" not in connections_list[name_to_register]["CONNECT_DATA"].keys() and \
                                   "SID" not in connections_list[name_to_register]["CONNECT_DATA"].keys():
                                    print("[ERROR] Missing SERVICE_NAME / SID for connection:", name_to_register)
                                    del connections_list[name_to_register]
                    elif current_depth == 2:
                        if is_in_add_list:
                            is_in_add_list = False
                            if not stop_registering:
                                if len(connections_list[name_to_register]["ADDRESS_LIST"]) == 1:
                                    connections_list[name_to_register]["ADDRESS_LIST"] = connections_list[name_to_register]["ADDRESS_LIST"][0]
                    elif current_depth == 3:
                        if is_in_add_list:
                            if not stop_registering:
                                connections_list[name_to_register]["ADDRESS_LIST"].append(current_addr)
                            current_addr = dict()
                        elif current_keyword.upper() in ["SID", "SERVER", "SERVICE_NAME"]:
                            if not stop_registering:
                                connections_list[name_to_register]["CONNECT_DATA"][current_keyword.upper()] = current_word.upper()
                    elif current_depth == 4:
                        if is_in_add_list:
                            if not stop_registering:
                                current_addr[current_keyword.upper()] = current_word.upper()
                    current_keyword = ""
                    current_word = ""
                    current_depth  += -1
                else:
                    current_word += c
        self.connections = connections_list
        self.aliases = connections_aliases
        self.duplicates = connections_duplicates


clsTns = ClsTnsnames('C:/app/Oracle/product/12.2.0/dbhome_1/network/admin/')
tnsnnames = clsTns.aliases
print('>>>>>>>>>>>>>>>>>>>>>', tnsnnames)
for i in tnsnnames:
    print(tnsnnames[i])