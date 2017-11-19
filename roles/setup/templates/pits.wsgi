import sys
 
sys.path.append('{{ provision_base_dir }}')
 
from {{ provision_prefix }} import app as application

