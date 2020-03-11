import os
import subprocess
import base64
import hashlib
import string
import errno

from ansible.module_utils._text import to_bytes
from ansible.module_utils.six import string_types
from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
from ansible.utils.hashing import checksum, checksum_s


# Create return parameters
def _update_result(result, src, dest, ds_type, binary_mode=False, encoding='EBCDIC'):
    data_set_types = {
        'PS': "Sequential",
        'PO': "Partitioned",
        'PDSE': "Partitioned Extended",
        'PE': "Partitioned Extended",
        'VSAM': "VSAM",
        'USS': "Unix"
    }
    updated_result = dict((k,v) for k,v in result.items())
    updated_result.update({
        'message': {
            'msg': "The {} was fetched successfully".format("file" if ds_type == 'USS' else "data set"),
            'stdout': "",
            'stderr': "",
            'ret_code': 0
        },
        'file': src,
        'dest': dest,
        'data_set_type': data_set_types[ds_type],
        'is_binary': binary_mode
    })
    if not binary_mode:
        updated_result.update({'encoding': encoding})
    
    return updated_result
    

def _write_content_to_file(filename, content, write_mode):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:    
        with open(filename, write_mode) as outfile:
            outfile.write(content)
    except UnicodeEncodeError as err:
        raise AnsibleError('''Error writing to destination {} due to encoding issues.
                               If it is a binary file, make sure to set 
                               'is_binary' parameter to 'true'; stderr: {}'''.format(filename, err))
    
    except (IOError, OSError) as err:
        raise AnsibleError("Error writing to destination {}: {}".format(filename, err))


def _process_boolean(arg, default=False):
    try:
        return boolean(arg)
    except TypeError:
        return default


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp
        
        src                 = self._task.args.get('src')
        dest                = self._task.args.get('dest')
        encoding            = self._task.args.get('encoding')
        volume              = self._task.args.get('volume')
        flat                = _process_boolean(self._task.args.get('flat'), default=False)
        is_binary           = _process_boolean(self._task.args.get('is_binary'))
        validate_checksum   = _process_boolean(self._task.args.get('validate_checksum'), default=True)

        msg = None
        if not isinstance(src, string_types):
            msg = "Invalid type supplied for 'source' option, it must be a string"
        if not isinstance(dest, string_types):
            msg = "Invalid type supplied for 'destination' option, it must be a string"
        if encoding and not isinstance(encoding, string_types):
            msg = "Invalid type supplied for 'encoding' option, it must be a string"
        if volume and not isinstance(volume, string_types):
            msg = "Invalid type supplied for 'volume' option, it must be a string"
        if src is None or dest is None:
            msg = "Source and destination are required"

        if msg:
            result['message'] = dict(msg=msg, stdout="", stderr="", ret_code=None)
            result['failed'] = True
            return result
        
        is_uss = True if '/' in src else False
        ds_type = None
        fetch_member = False
        src = self._connection._shell.join_path(src)
        src = self._remote_expand_user(src)

        if src.endswith(')'):
            fetch_member = True

        # calculate the destination name
        if os.path.sep not in self._connection._shell.join_path('a', ''):
            src = self._connection._shell._unquote(src)
            source_local = src.replace('\\', '/')
        else:
            source_local = src

        dest = os.path.expanduser(dest)
        if flat:
            if os.path.isdir(to_bytes(dest, errors='surrogate_or_strict')) and not dest.endswith(os.sep):
                result['message'] = dict(msg="dest is an existing directory, use a trailing slash if you want to fetch src into that directory",
                                        stdout="",
                                        stderr="",
                                        ret_code=None
                                    )
                result['failed'] = True
                return result
            if dest.endswith(os.sep):
                base = os.path.basename(source_local)
                dest = os.path.join(dest, base)
            if not dest.startswith("/"):
                dest = self._loader.path_dwim(dest)
        else:
            if 'inventory_hostname' in task_vars:
                target_name = task_vars['inventory_hostname']
            else:
                target_name = self._play_context.remote_addr
            dest = "{}/{}/{}".format(self._loader.path_dwim(dest), target_name, source_local)

        dest = dest.replace("//", "/")
        if fetch_member:
            member = src[ src.find('(') + 1 : src.find(')') ]
            base_dir = os.path.dirname(dest)
            dest = os.path.join(base_dir, member)
        
        new_module_args = dict((k,v) for k,v in self._task.args.items())
        new_module_args.update({'_fetch_member': fetch_member, 'is_uss': is_uss})
        fetch_res = self._execute_module(module_name='zos_fetch', module_args=new_module_args, task_vars=task_vars)
        
        if fetch_res.get('msg'):
            result['message'] = dict(stdout=fetch_res['stdout'], 
                                    stderr=fetch_res['stderr'], 
                                    ret_code=fetch_res['ret_code'],
                                    msg=fetch_res['msg']
                                )
            result['failed'] = fetch_res.get('failed')
            return result
        
        elif fetch_res.get('note'):
            result['note'] = fetch_res.get('note')
            return result
        
        ds_type = fetch_res.get('ds_type')
        src = fetch_res['file']

        fetch_content = None
        mvs_ds = ds_type in ('PO', 'PDSE', 'PE')
        
        if ds_type == 'VSAM' or ds_type == 'PS' or is_uss or (fetch_member and mvs_ds):
            fetch_content = self._transfer_from_uss(dest, task_vars, fetch_res['content'], fetch_res['checksum'], 
                                    binary_mode=is_binary, validate_checksum=validate_checksum)
        
        elif mvs_ds:   
            fetch_content = self._transfer_pds(dest, task_vars, fetch_res['pds_path'], binary_mode=is_binary)
        
        else:
            result['message'] = dict(msg="The data set type '{}' is not currently supported".format(ds_type),
                                    stdout="",
                                    stderr="",
                                    ret_code=None
                                )
            result['failed'] = True
            return result

        if fetch_content:
            result.update(fetch_content)
        
        result = _update_result(result, src, dest, ds_type, 
                    binary_mode=is_binary, encoding=encoding if encoding else 'EBCDIC')
        
        return result


    # Transfer PDS from remote z/OS machine to the local machine
    def _transfer_pds(self, dest, task_vars, pds_path, binary_mode=False):
        result = dict()
        try:
            ansible_user = self._play_context.remote_user
            ansible_host = self._play_context.remote_addr
            stdin = None
            
            if binary_mode:
                cmd = ['sftp', ansible_user + '@' + ansible_host]
                stdin = "get -r {} {}".format(pds_path, dest).encode()
            else:
                cmd = ['scp', '-r', ansible_user + '@' + ansible_host + ':' + pds_path, dest]

            transfer_pds = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = transfer_pds.communicate(stdin)
            
            if transfer_pds.returncode != 0:
                raise AnsibleError("Error transferring PDS from remote z/OS system\n stdout: {}\n stderr: {}".format(out, err))
            
            result['changed'] = True
        
        finally:
            self._connection.exec_command("rm -r {}".format(pds_path))

        return result

      
    # Transfer USS files or sequential data sets to the local machine 
    def _transfer_from_uss(self, dest, task_vars, content, checksum, binary_mode=False, validate_checksum=True):
        result = dict()
        new_content = content
        
        if binary_mode:
            write_mode = 'wb'
            try:
                local_data = open(dest, 'rb').read()
                local_checksum = checksum_s(base64.b64encode(local_data))
            except FileNotFoundError:
                local_checksum = None
            
            new_content = base64.b64decode(content)
        else:
            write_mode = 'w'
            local_checksum = checksum(dest)
        
        if validate_checksum:
            remote_checksum = checksum
            
            if remote_checksum != local_checksum:
                _write_content_to_file(dest, new_content, write_mode)
                new_checksum = checksum_s(content)
                
                if remote_checksum != new_checksum:
                    result.update(dict(msg='Checksum mismatch',checksum=new_checksum,
                                    remote_checksum=remote_checksum, failed=True))
                else:
                    result.update(dict(checksum=new_checksum, changed=True, remote_checksum=remote_checksum))
            else:
                result['changed'] = False
                result['checksum'] = remote_checksum
        else:
            _write_content_to_file(dest, new_content, write_mode) 
            result['changed'] = True
        
        return result
        
