'''
Demo datas
'''

operating_systems = [
    { 'host': 'database-01', 'os': 'Debian Bookworm' },
    { 'host': 'database-02', 'os': 'Debian Bullseye' },
    { 'host': 'webserver-01', 'os': 'Red Hat Enterprise Linux 8' },
    { 'host': 'webserver-02', 'os': 'Red Hat Enterprise Linux 9' },
    { 'host': 'mailserver-01', 'os': 'Windows Server 2025' },
    { 'host': 'mailserver-02', 'os': 'Windows Server 2022' },
]

dns_records = [
    { 'hostname': 'database-01.admin.lan', 'A_record': '10.10.10.101', 'CNAME_record': 'postgresql-01.admin.lan' },
    { 'hostname': 'database-01.prod.lan', 'A_record': '172.16.10.101', 'CNAME_record': 'postgresql-01.prod.lan' },

    { 'hostname': 'database-02.admin.lan', 'A_record': '10.10.10.102', 'CNAME_record': 'postgresql-02.admin.lan' },
    { 'hostname': 'database-02.prod.lan', 'A_record': '172.16.10.102', 'CNAME_record': 'postgresql-02.prod.lan' },

    { 'hostname': 'webserver-01.admin.lan', 'A_record': '10.10.10.111' },
    { 'hostname': 'webserver-01.prod.lan', 'A_record': '172.16.10.111' },

    { 'hostname': 'webserver-02.admin.lan', 'A_record': '10.10.10.112' },
    { 'hostname': 'webserver-02.prod.lan', 'A_record': '172.16.10.112' },
    
    { 'hostname': 'mailserver-01.admin.lan', 'A_record': '10.10.10.121' },
    { 'hostname': 'mailserver-01.prod.lan', 'A_record': '172.16.10.121', 'TXT_record': 'My SPF data' },

    { 'hostname': 'mailserver-02.admin.lan', 'A_record': '10.10.10.122' },
    { 'hostname': 'mailserver-02.prod.lan', 'A_record': '172.16.10.122', 'TXT_record': 'My SPF data'  },
]

vlans = [
    { 'id': 100, 'network': '10.10.0.0', 'netmask': '255.255.240.0', 'description': 'Administration VLAN' },
    { 'id': 110, 'network': '172.16.10.0', 'netmask': '255.255.255.128', 'description': 'Production VLAN' },
    { 'id': 120, 'network': '172.16.10.128', 'netmask': '255.255.255.128', 'description': 'Reserved VLAN' },
]