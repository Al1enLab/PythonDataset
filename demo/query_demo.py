from Dataset import Dataset
from DatasetQuery import select, update, delete, alter, asc, desc, UpdateElement
from .demo_data import *

import ipaddress
import re

os_dataset = Dataset(operating_systems, name='OS')
dns_dataset = Dataset(dns_records, name='DNS')
vlans_dataset = Dataset(vlans, name='VLANs')

header_width = 80
print()
print('< Demo Datasets >'.center(header_width, '='))
print()
print(f'< {os_dataset} dataset >'.center(header_width, ' '))
print()
os_dataset.to_table()
print()
print(f'< {dns_dataset} dataset >'.center(header_width, ' '))
print()
dns_dataset.to_table()
print()
print(f'< {vlans_dataset} dataset >'.center(header_width, ' '))
print()
vlans_dataset.to_table()

def explain_and_run(query, query_name):
    print()
    print(f'< {query_name} >'.center(header_width, '='))
    print()
    print(query.explain())
    print()
    query.execute().to_table()
    print()

# Requête la plus simple
query = (
    # Sans liste de champs, select retourne tous les champs
    select()
    # depuis le dataset os_dataset
    .from_(os_dataset)
)
explain_and_run(query, 'Simple query')

# Avec JOIN et fonction
def host_from_hostname(dns_hostname: str) -> str:
    '''Retourne le nom de la machine depuis le nom DNS
    Par exemple : machine.domain.ext -> machine'''
    return dns_hostname.split('.')[0]

'''
Le JOIN ci-dessous est fait sur :
- le nom de machine contenu dans os_dataset
- le résultat de l'appel de la fonction host_from_hostname
    avec pour paramètre le hostname du dns_dataset
'''
query = (
    select(
        dns_dataset.hostname,
        os_dataset.os,
        dns_dataset.A_record,
        dns_dataset.CNAME_record,
        dns_dataset.TXT_record
    )
    .from_(os_dataset)
    .join(dns_dataset).on(os_dataset.host == dns_dataset.hostname.func(host_from_hostname))
)
explain_and_run(query, 'Select specific fields, JOIN on function result')

# JOINs multiples sur fonctions multiples
def ip_in_network(ipaddr: str, network: str, netmask: str) -> bool:
    '''Retourne True si ipaddr est dans network/netmask'''
    ipaddr = ipaddress.IPv4Address(ipaddr)
    network = ipaddress.ip_network(f'{network}/{netmask}')
    return ipaddr in network

def prefix_len(netmask: str) -> int:
    '''Retourne le netmask sous forme d'entier'''
    return ipaddress.IPv4Network(f'0.0.0.0/{netmask}').prefixlen

'''
datasetfield.func() permet d'exécuter une fonction sur le datafield
Le premier paramètre passé à la fonction est TOUJOURS la valeur actuelle du datafield.

.cast_as(type) permet de transtyper un champ ou une expression

datafield.exists est True si le champ existe dans l'élément courant, False sinon.
N'oublions pas que nous n'avons pas de schéma, et qu'un champ peut exister dans un élément
et pas nécessairement dans le suivant - cf ns_records.
'''
query = (
    select(
        dns_dataset.hostname.as_('Hostname'),
        os_dataset.os.as_('Operating System'),
        dns_dataset.A_record.as_('IP address'),
        vlans_dataset.id.as_('VLAN id'),
        (vlans_dataset.network + '/' + vlans_dataset.netmask.func(prefix_len).cast_as(str)).as_('Network'),
        vlans_dataset.description.as_('VLAN description'),
        (dns_dataset.CNAME_record.exists | dns_dataset.TXT_record.exists).as_('Additional records')
    )
    .from_(os_dataset)
    .join(dns_dataset).on(os_dataset.host == dns_dataset.hostname.func(host_from_hostname))
    .join(vlans_dataset).on(dns_dataset.A_record.func(ip_in_network, vlans_dataset.network, vlans_dataset.netmask))
)
explain_and_run(query, 'Multiple JOINs, Aliasing, CAST, exists')

'''
Construisons le dataset entier
'''
query = (
    select(
        dns_dataset.hostname.as_('Hostname'),
        os_dataset.os.as_('Operating System'),
        dns_dataset.A_record.as_('IP address'),
        vlans_dataset.id.as_('VLAN id'),
        (vlans_dataset.network + '/' + vlans_dataset.netmask.func(prefix_len).cast_as(str)).as_('Network'),
        vlans_dataset.description.as_('VLAN description'),
        dns_dataset.CNAME_record.as_('CNAME'),
        dns_dataset.TXT_record.as_('TXT')
    )
    .from_(os_dataset)
    .join(dns_dataset).on(os_dataset.host == dns_dataset.hostname.func(host_from_hostname))
    .join(vlans_dataset).on(dns_dataset.A_record.func(ip_in_network, vlans_dataset.network, vlans_dataset.netmask))
)
explain_and_run(query, 'Full dataset')
machines = query.execute().set_name('Machines')

'''
Suppression des valeurs None
La requête DROP accepte une clause WHERE - on n'a PAS de schéma, alors pourquoi pas
'''
query = (
    alter(machines)
    .drop(machines.CNAME)
    .where(machines.CNAME.is_(None))
)
explain_and_run(query, 'Remove None CNAME values')
query = (
    alter(machines)
    .drop(machines.TXT)
    .where(machines.TXT.is_(None))
)
explain_and_run(query, 'Remove None TXT values')

'''
Affichage des données uniquement si CNAME existe ou TXT existe
'''
query = (
    select()
    .from_(machines)
    .where(machines.CNAME.exists | machines.TXT.exists)
)
explain_and_run(query, 'Select where CNAME or TXT exist')

'''
Suppression des données des serveurs Windows
'''
query = (
    delete()
    .from_(machines)
    .where(machines['Operating System'].like(r'^WINDOWS.*', re.IGNORECASE))
)
explain_and_run(query, 'DELETE WHERE LIKE, __getitem__ syntax')

'''
Mise à jour des numéros de version Debian
'''
query = (
    update(machines)
    .set_(
        UpdateElement(machines['Operating System'], 'Debian 12')
    )
    .where(machines['Operating System'].like(r'debian bookworm', re.IGNORECASE))
)
explain_and_run(query, 'Update Debian version: Bookworm -> 12')

query = (
    update(machines)
    .set_(
        UpdateElement(machines['Operating System'], 'Debian 11')
    )
    .where(machines['Operating System'].like(r'debian bullseye', re.IGNORECASE))
)
explain_and_run(query, 'Update Debian version: Bullseye -> 11')
