/* rexx  __ANSIBLE_ENCODE_EBCDIC__  */
/* WANT_JSON */

/* Copyright (c) IBM Corporation 2019, 2020 */
/* Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0) */

/*
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: zos_ping
version_added: 2.9
short_description: Try to connect to zOS host, verify a usable z/OS Web Client enablement toolkit,
  iconv and usable python and return C(pong) on success and warning if usable Python is not found
description:
  - A trivial test module, this module always returns C(pong) on successful contact. It does not make sense
    in playbooks, but it is useful from C(/usr/bin/ansible) to verify the ability to login and check if system
    has prerequisite.
  - This is NOT ICMP ping, this is just a trivial test module that requires z/OS Web Client enablement toolkit,
    iconv and usable python on z/OS."
  - The "zos_ssh" conection plugin must be used for this module to function correctly

author:
  - Vijay Katoch
  - Blake Becker (minor changes)

'''

EXAMPLES = '''
- name: Ping the z/OS host and perform resource checks
  zos_ping:
  register: result
'''

RETURN = '''
ping:
  description: Should contain the value "pong" on success 
  type: str
warnings: In case usable Python is not found
  description: List of warnings returned from stderr when performing resource checks
  type: list
  elements: str
'''
*/

Parse Arg argFile .

pythonName       = 'Python'
majVersionPython = 3
minVersionPython = 6

If (argFile = '') Then Do
    errmsg = 'Internal Error: JSON argument file missing' || ESC_N
    Call Syscalls 'ON'
    Address Syscall
        'Write' 2 'errmsg' length(errmsg)
    Exit(16)
End
newArgFile1 = argFile || 1
/* Check for iconv utility by conversting the JSON argument file form ASCII to EBCDIC */
retC = bpxwunix('iconv -f ISO8859-1 -t IBM-1047' argFile,,stdout.,stderr.)
If (retC <> 0) Then Do
    If (stderr. <> 0) Then Do
        Call Syscalls 'ON'
        Address Syscall
            Do index=1 To stderr.0
                errmsg = stderr.index || ESC_N
                'Write' 2 'errmsg' length(errmsg)
            End
    End        
    Exit(retC)
End
/* Load z/OS Web Client enablement toolkit to verify system has z/OS Web Client enablement toolkit installed */ Call hwtcalls "on"
Address hwtjson 'hwtConst returnCode resbuf.'
If (rc <> 0 | returnCode <> HWTJ_OK) Then Do
    retC = rc
    errmsg = 'Error: Unable to start JSON Parser may be due to missing',
             'z/OS Web Client enablement toolkit.' || ESC_N
    Call Syscalls 'ON'
    Address Syscall
        'Write' 2 'errmsg' length(errmsg)
    Exit(retC)
End

warningJsonList = ''

/* Check for Python version eg: 'Python 3.6.9' */
retC = bpxwunix('python3 --version',, out., err.)
If (err.0 > 0) Then Do
    warningJsonList = ',"warnings":['
    Do index=1 To err.0
        warningJsonList = warningJsonList || '"Python Warning: ' || err.index || '"'
        If (index < err.0) Then
            warningJsonList = warningJsonList || ','
    End
    warningJsonList = warningJsonList || ']'
End
Else Do
    If (out.0 > 0) Then Do
        parse Var out.1 name version
        parse Var version majVer '.' minVer '.' micVer
        If (pythonName == strip(name)) Then Do
            If (majVer < majVersionPython | minVer < minVersionPython) Then Do
                warningJsonList = ',"warnings": ["Python Warning: Python not up to the level to support z/OS modules"]'
            End
        End
        Else Do
            warningJsonList = ',"warnings": ["Python Warning: Incorrect Python Found"]'
        End
    End
End

retJson = '{"changed":false,"ping": "pong","failed":false'
/* Construct a JSON list for warnings */
If (warningJsonList <> '') Then
    retJson = retJson || warningJsonList
retJson = retJson || '}'

Say retJson
Exit(0)
