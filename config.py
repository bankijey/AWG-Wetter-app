from configparser import ConfigParser
from urllib.parse import urlparse
import psycopg2

def config(filename= 'config.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

result = urlparse("postgres://xmedzuylzapgdq:0d4b3758b43de4c7ee01b02646ff7c0348d13b75723656ca88a9f0209cadde07@ec2-107-22-83-3.compute-1.amazonaws.com:5432/d4c25g1h6no7hu")
# also in python 3+ use: urlparse("YourUrl") not urlparse.urlparse("YourUrl")
username = result.username
password = result.password
database = result.path[1:]
hostname = result.hostname
port = result.port
connection = psycopg2.connect(
    database = database,
    user = username,
    password = password,
    host = hostname,
    port = port
)