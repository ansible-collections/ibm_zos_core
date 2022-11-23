from __future__ import absolute_import, division, print_function
from datetime import datetime
import json
from os import path

from ansible.plugins.action import ActionBase
__metaclass__ = type


class ActionModule(ActionBase):
    '''
    Action plugin to process input to zos_ickdsf_init module, then pass
    the output to zos_mvs_raw, logging output to an HTML file if specified
    '''
    def run(self, tmp=None, task_vars=None):
        '''
        Runs Action plugin to process input to zos_ickdsf_init and zos_mvs raw
        modules, then runs the modules and prints the output to console
        '''
        if task_vars is None:
            task_vars = dict()

        super().run(tmp=tmp, task_vars=task_vars)
        task_args = self._task.args.copy()

        # execute IckdsfCommand convert to get input for zos_mvs_raw
        result = self._execute_module(
            module_name='ibm.ibm_zos_core.zos_ickdsf_init',
            module_args=task_args,
            task_vars=task_vars,
        )

        if not result.get('command'):
            result['failed'] = True
            result['msg'] = 'Could not parse command'
            return dict(result)

        mvs_raw_args = {
            'program_name': 'ICKDSF',
            'parm': 'NOREPLYU,FORCE',
            'auth': True,
            'dds': [
                {
                    'dd_output': {
                        'dd_name': 'sysprint',
                        'return_content': {
                            'type': 'text'
                        }
                    },
                },
                {
                    'dd_input': {
                        'dd_name': 'sysin',
                        'content': result.get('command')
                    }
                }
            ]
        }

        # execute mvs_raw with content from IckdsfCommand convert
        mvs_result = self._execute_module(
            module_name='ibm.ibm_zos_core.zos_mvs_raw',
            module_args=mvs_raw_args,
            task_vars=task_vars,
        )

        result['mvs_raw_output'] = mvs_result

        rc = mvs_result.get('ret_code').get('code')
        if rc != 0:
            result['failed'] = True
            result['output'] = "INIT Failed with return code {}".format(rc)
        else:
            result['changed'] = True

        # save into a html file, if html_output key exists and full file path is provided
        if task_args.get("output_html") and task_args.get("output_html").get("full_file_path"):
            print("generating html file")
            mvs_result["output_html"] = self.generate_html_file(mvs_result)

        return dict(result)

    def generate_html_file(self, mvs_result):
        '''
        Creates an HTML file with output from ICKDSF INIT command.
        '''
        task_args = self._task.args.copy()

        # obtain current time
        now = datetime.now()
        time_string = now.strftime("%m/%d/%Y %H:%M:%S")

        # create or append to user-defined html file, if it exists
        user_defined_path = task_args.get("output_html").get("full_file_path")
        append_output = task_args.get("output_html").get("append")

        if append_output or append_output is None:
            f = open(user_defined_path, 'a')
        else:
            f = open(user_defined_path, 'w')

        # steps to maintain correct format for z/os output in the html file
        json_convert = json.dumps(mvs_result)
        json_output = json.loads(json_convert)
        json_prettified = json.dumps(json_output, indent=4, sort_keys=True)
        playbook_prettified = json.dumps(task_args, indent=4, sort_keys=True)

        # obtain relavant html elements
        ickdsf_ref_link = "https://www-01.ibm.com/servers/resourcelink/svc00100.nsf/pages/zOSV2R4gc350033/$file/ickug00_v2r4.pdf"
        ickdsf_mod_link = "https://github.ibm.com/jumpstart-bayarea/tc2021-ch1-zOMAP/tree/ads-actionplugin/collections/ansible_collections/ibm/ibm_zos_core"
        zos_collection_link = "https://ibm.github.io/z_ansible_collections_doc/index.html"
        rec = mvs_result.get("ret_code").get("code")
        # if return code is non-zero, color it red, else, green
        if int(rec):
            rec_color = "red"
        else:
            rec_color = "green"

        # create html template
        html_template = """
        <html>
            <head>
                <title>Z/OS ICKDSF Command Output </title>
                <style>
                    div.first {{
                        text-indent: 50px;
                    }}
                    div.second {{
                        text-indent: 100px;
                    }}
                    div.third {{
                        text-indent: 150px;
                    }}
                    pre {{
                        margin-left: 100px;
                    }}
                </style>
            </head>

            <body>
                <h2>Z/OS ICKDSF Command Output Generated on {time} </h2>
                <div class="first">
                    <h3> Command used: {command} </h3>
                    <h3> Return code:
                        <span style="color: {rec_color}"> {rec} </span>
                    </h3>
                </div>
                <div class="first">
                    <h3> Playbook: </h3>
                    <pre> {playbook} </pre>
                </div>
                <div class="first">
                    <h3> Command output: </h3>
                    <pre> {output} </pre>
                </div>
                <div class="second">
                    <p> For more information regarding ICKDSF commands:
                        <a href={ickdsf_ref_link}> ICKDSF User's Guide and Reference </a> </p>

                    <p> Documentation regarding ICKDSF module (requires IBM w3id):
                        <a href={ickdsf_mod_link}> ICKDSF Github Page </a> </p>

                    <p> Ansible Galaxy page for z/OS core collection, on which this module is based:
                        <a href={zos_collection_link}>IBM z/OS Core Collection</a> </p>
                    </p>
                        <br>
                </div>
            </body>
        </html>""".format(command="init", time=time_string, playbook=playbook_prettified, output=json_prettified, rec=rec, rec_color=rec_color,
                          ickdsf_ref_link=ickdsf_ref_link, ickdsf_mod_link=ickdsf_mod_link, zos_collection_link=zos_collection_link)

        f.write(html_template)
        f.close()
        return path.abspath(user_defined_path)
