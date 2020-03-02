# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division)
__metaclass__ = type


from ansible.module_utils.basic import AnsibleModule
import pytest
import sys
from mock import call

# Used my some mock modules, should match import directly below
IMPORT_NAME = 'ansible_collections_ibm_zos_core.plugins.modules.zos_operator_openquestion'


# * Tests for zos_operator_openquestion

dummy_dict1 = {
    'request_number_list': ['001','010']
}

dummy_dict1_result = [{
    'number': '010', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13369', 'message_text': '*010 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5A', 'jobname': 'IM5ACTRL', 'message_id': 'DFS3139I'}]

dummy_dict2 = {
    'request_number_list': []
}
dummy_dict2_result = [{'number': '466', 'type': 'R', 'system': 'MV27', 'jobid': 'STC30925', 'message_text': '*466 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5H', 'jobname': 'IM5HCTRL', 'message_id': 'DFS3139I'}, {'number': '465', 'type': 'R', 'system': 'MV27', 'jobid': 'STC30927', 'message_text': '*465 HWSC0000I *IMS CONNECT READY* IM5HCONN', 'jobname': 'IM5HCONN', 'message_id': 'HWSC0000I'}, {'number': '216', 'type': 'R', 'system': 'MV26', 'jobid': 'STC23289', 'message_text': '*216 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5G', 'jobname': 'IM5GCTRL', 'message_id': 'DFS3139I'}, {'number': '215', 'type': 'R', 'system': 'MV26', 'jobid': 'STC23291', 'message_text': '*215 HWSC0000I *IMS CONNECT READY* IM5GCONN', 'jobname': 'IM5GCONN', 'message_id': 'HWSC0000I'}, {'number': '183', 'type': 'R', 'system': 'MV26', 'jobid': 'STC21689', 'message_text': '*183 VAMP 0670 : ENTER COMMAND FOR IYCQZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '182', 'type': 'R', 'system': 'MV26', 'jobid': 'STC21684', 'message_text': '*182 DSI802A IYM26    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'MQNVIEW', 'message_id': 'DSI802A'}, {'number': '178', 'type': 'R', 'system': 'MV26', 'message_text': '*178 DSI802A IYCQN    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '134', 'type': 'R', 'system': 'MV2I', 'jobid': 'STC15829', 'message_text': '*134 DSI802A IYM2I    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'MQNVIEW', 'message_id': 'DSI802A'}, {'number': '133', 'type': 'R', 'system': 'MV2I', 'jobid': 'STC15833', 'message_text': '*133 VAMP 0670 : ENTER COMMAND FOR IYCIZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '116', 'type': 'R', 'system': 'MV2H', 'jobid': 'STC15768', 'message_text': '*116 VAMP 0670 : ENTER COMMAND FOR IYDCZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '130', 'type': 'R', 'system': 'MV2I', 'message_text': '*130 DSI802A IYCIN    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '101', 'type': 'R', 'system': 'MV2G', 'jobid': 'STC15413', 'message_text': '*101 VAMP 0670 : ENTER COMMAND FOR IYDBZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '113', 'type': 'R', 'system': 'MV2H', 'message_text': '*113 DSI802A IYDCN    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '088', 'type': 'R', 'system': 'MV2D', 'jobid': 'STC15113', 'message_text': '*088 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5F', 'jobname': 'IM5FCTRL', 'message_id': 'DFS3139I'}, {'number': '087', 'type': 'R', 'system': 'MV2D', 'jobid': 'STC15175', 'message_text': '*087 HWSC0000I *IMS CONNECT READY* IM5FCONN', 'jobname': 'IM5FCONN', 'message_id': 'HWSC0000I'}, {'number': '086', 'type': 'R', 'system': 'MV2D', 'jobid': 'STC15120', 'message_text': '*086 DSI802A IYM2D    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'MQNVIEW', 'message_id': 'DSI802A'}, {'number': '085', 'type': 'R', 'system': 'MV2D', 'jobid': 'STC15125', 'message_text': '*085 VAMP 0670 : ENTER COMMAND FOR IYCXZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '098', 'type': 'R', 'system': 'MV2G', 'message_text': '*098 DSI802A IYDBN    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '070', 'type': 'R', 'system': 'MV29', 'jobid': 'STC14852', 'message_text': '*070 DSI802A IYM29    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'MQNVIEW', 'message_id': 'DSI802A'}, {'number': '069', 'type': 'R', 'system': 'MV29', 'jobid': 'STC14856', 'message_text': '*069 VAMP 0670 : ENTER COMMAND FOR IY29ZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '082', 'type': 'R', 'system': 'MV2D', 'message_text': '*082 DSI802A IYCXN    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '054', 'type': 'R', 'system': 'MV28', 'jobid': 'STC14575', 'message_text': '@054 DFHSI1538D  IYCWEHCM Install GRPLIST Errors. Is startup to be continued - Enter GO or CANCEL.', 'jobname': 'IYCWEHCM', 'message_id': 'DFHSI1538D'}, {'number': '053', 'type': 'R', 'system': 'MV28', 'jobid': 'STC14520', 'message_text': '*053 DSI802A IYM28    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'MQNVIEW', 'message_id': 'DSI802A'}, {'number': '052', 'type': 'R', 'system': 'MV28', 'jobid': 'STC14526', 'message_text': '*052 VAMP 0670 : ENTER COMMAND FOR IYCSZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '066', 'type': 'R', 'system': 'MV29', 'message_text': '*066 DSI802A IY29N    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '038', 'type': 'R', 'system': 'MV27', 'jobid': 'STC14220', 'message_text': '*038 DSI802A IYM27    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'MQNVIEW', 'message_id': 'DSI802A'}, {'number': '037', 'type': 'R', 'system': 'MV27', 'jobid': 'STC14225', 'message_text': '*037 VAMP 0670 : ENTER COMMAND FOR IYCRZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}, {'number': '049', 'type': 'R', 'system': 'MV28', 'message_text': '*049 DSI802A IYCSN    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '034', 'type': 'R', 'system': 'MV27', 'message_text': '*034 DSI802A IYCRN    REPLY WITH VALID NCCF SYSTEM OPERATOR COMMAND', 'jobname': 'NETVIEW', 'message_id': 'DSI802A'}, {'number': '010', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13369', 'message_text': '*010 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5A', 'jobname': 'IM5ACTRL', 'message_id': 'DFS3139I'}, {'number': '009', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13367', 'message_text': '*009 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM4A', 'jobname': 'IM4ACTRL', 'message_id': 'DFS3139I'}, {'number': '008', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13493', 'message_text': '*008 HWSC0000I *IMS CONNECT READY* IM5DCONN', 'jobname': 'IM5DCONN', 'message_id': 'HWSC0000I'}, {'number': '007', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13484', 'message_text': '*007 HWSC0000I *IMS CONNECT READY* IM4ACONN', 'jobname': 'IM4ACONN', 'message_id': 'HWSC0000I'}, {'number': '006', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13480', 'message_text': '*006 HWSC0000I *IMS CONNECT READY* IM4DCONN', 'jobname': 'IM4DCONN', 'message_id': 'HWSC0000I'}, {'number': '005', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13489', 'message_text': '*005 HWSC0000I *IMS CONNECT READY* IM5ACONN', 'jobname': 'IM5ACONN', 'message_id': 'HWSC0000I'}, {'number': '004', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13395', 'message_text': '*004 VAMP 0670 : ENTER COMMAND FOR IYCWZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}]



dummy_dict3 = {
    'request_number_list': [],
    'system': 'mv2c'
}
dummy_dict3_result = [{'number': '010', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13369', 'message_text': '*010 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5A', 'jobname': 'IM5ACTRL', 'message_id': 'DFS3139I'}, {'number': '009', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13367', 'message_text': '*009 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM4A', 'jobname': 'IM4ACTRL', 'message_id': 'DFS3139I'}, {'number': '008', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13493', 'message_text': '*008 HWSC0000I *IMS CONNECT READY* IM5DCONN', 'jobname': 'IM5DCONN', 'message_id': 'HWSC0000I'}, {'number': '007', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13484', 'message_text': '*007 HWSC0000I *IMS CONNECT READY* IM4ACONN', 'jobname': 'IM4ACONN', 'message_id': 'HWSC0000I'}, {'number': '006', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13480', 'message_text': '*006 HWSC0000I *IMS CONNECT READY* IM4DCONN', 'jobname': 'IM4DCONN', 'message_id': 'HWSC0000I'}, {'number': '005', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13489', 'message_text': '*005 HWSC0000I *IMS CONNECT READY* IM5ACONN', 'jobname': 'IM5ACONN', 'message_id': 'HWSC0000I'}, {'number': '004', 'type': 'R', 'system': 'MV2C', 'jobid': 'STC13395', 'message_text': '*004 VAMP 0670 : ENTER COMMAND FOR IYCWZVMP', 'jobname': 'VAMP', 'message_id': 'VAMP'}]


dummy_dict4 = {
    'request_number_list': [],
    'message_id': 'DFH*'
}
dummy_dict4_result = [{'number': '054', 'type': 'R', 'system': 'MV28', 'jobid': 'STC14575', 'message_text': '@054 DFHSI1538D  IYCWEHCM Install GRPLIST Errors. Is startup to be continued - Enter GO or CANCEL.', 'jobname': 'IYCWEHCM', 'message_id': 'DFHSI1538D'}]

dummy_dict5_uppercase = {
    'request_number_list': [],
    'message_id': 'DFH*',
    'system': 'MV28'
}

dummy_dict5_lowercase = {
    'request_number_list': [],
    'message_id': 'DFH*',
    'system': 'mv28'
}

dummy_dict5_result = [{'number': '054', 'type': 'R', 'system': 'MV28', 'jobid': 'STC14575', 'message_text': '@054 DFHSI1538D  IYCWEHCM Install GRPLIST Errors. Is startup to be continued - Enter GO or CANCEL.', 'jobname': 'IYCWEHCM', 'message_id': 'DFHSI1538D'}]

dummy_dict6 = {
      'request_number_list': ['466'],
      'system': 'mv27',
      'message_id': 'DFS*',
      'jobname': 'IM5H*'
}

dummy_dict6_result = [{'number': '466', 'type': 'R', 'system': 'MV27', 'jobid': 'STC30925', 'message_text': '*466 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART PROCEEDING IM5H', 'jobname': 'IM5HCTRL', 'message_id': 'DFS3139I'}, {'number': '465', 'type': 'R', 'system': 'MV27', 'jobid': 'STC30927', 'message_text': '*465 HWSC0000I *IMS CONNECT READY* IM5HCONN', 'jobname': 'IM5HCONN', 'message_id': 'HWSC0000I'}]

dummy_dict7 = {
      'request_number_list': ['888'],
      'system': 'mv27',
      'message_id': 'DFS*',
      'jobname': 'IM5H*'
}

dummy_dict7_result = []

dummy_dict_invalid_message = {
    'request_number_list': [],
    'message_id': 'DFH1234567'
}
dummy_dict_invalid_job_name = {
    'request_number_list': [],
    'jobname': 'IM5H123456'
}
dummy_dict_invalid_system = {
    'request_number_list': [],
    'system': 'mv2712345',
}

dummy_dict_invalid_number = {
    'request_number_list': ['abc'],
    'system': 'mv27',
}

# dummy result for operator command 'd r,a,s'
operator_message1 = 'MV2C      2019361  03:36:24.71             ISF031I CONSOLE XIAOPIN ACTIVATED\nMV2C      2019361  03:36:24.71            -D R,A,S\nMV2C      2019361  03:36:24.72             IEE112I 03.36.24 PENDING REQUESTS 963\n                                           RM=37   IM=0     CEM=0     EM=0     RU=0    IR=0    NOAMRF\n                                           ID:R/K     T SYSNAME  JOB ID   MESSAGE TEXT\n                                                  466 R MV27     STC30925 *466 DFS3139I IMS INITIALIZED,\n                                                                          AUTOMATIC RESTART PROCEEDING\n                                                                          IM5H\n                                                  465 R MV27     STC30927 *465 HWSC0000I *IMS CONNECT READY*\n                                                                          IM5HCONN\n                                                  216 R MV26     STC23289 *216 DFS3139I IMS INITIALIZED,\n                                                                          AUTOMATIC RESTART PROCEEDING\n                                                                          IM5G\n                                                  215 R MV26     STC23291 *215 HWSC0000I *IMS CONNECT READY*\n                                                                          IM5GCONN\n                                                  183 R MV26     STC21689 *183 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYCQZVMP\n                                                  182 R MV26     STC21684 *182 DSI802A IYM26    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  178 R MV26              *178 DSI802A IYCQN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  134 R MV2I     STC15829 *134 DSI802A IYM2I    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  133 R MV2I     STC15833 *133 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYCIZVMP\n                                                  116 R MV2H     STC15768 *116 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYDCZVMP\n                                                  130 R MV2I              *130 DSI802A IYCIN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  101 R MV2G     STC15413 *101 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYDBZVMP\n                                                  113 R MV2H              *113 DSI802A IYDCN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  088 R MV2D     STC15113 *088 DFS3139I IMS INITIALIZED,\n                                                                          AUTOMATIC RESTART PROCEEDING\n                                                                          IM5F\n                                                  087 R MV2D     STC15175 *087 HWSC0000I *IMS CONNECT READY*\n                                                                          IM5FCONN\n                                                  086 R MV2D     STC15120 *086 DSI802A IYM2D    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  085 R MV2D     STC15125 *085 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYCXZVMP\n                                                  098 R MV2G              *098 DSI802A IYDBN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  070 R MV29     STC14852 *070 DSI802A IYM29    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  069 R MV29     STC14856 *069 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IY29ZVMP\n                                                  082 R MV2D              *082 DSI802A IYCXN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  054 R MV28     STC14575 @054 DFHSI1538D  IYCWEHCM Install\n                                                                          GRPLIST Errors. Is startup to be\n                                                                          continued - Enter GO or CANCEL.\n                                                  053 R MV28     STC14520 *053 DSI802A IYM28    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  052 R MV28     STC14526 *052 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYCSZVMP\n                                                  066 R MV29              *066 DSI802A IY29N    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  038 R MV27     STC14220 *038 DSI802A IYM27    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  037 R MV27     STC14225 *037 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYCRZVMP\n                                                  049 R MV28              *049 DSI802A IYCSN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  034 R MV27              *034 DSI802A IYCRN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND\n                                                  010 R MV2C     STC13369 *010 DFS3139I IMS INITIALIZED,\n                                                                          AUTOMATIC RESTART PROCEEDING\n                                                                          IM5A\n                                                  009 R MV2C     STC13367 *009 DFS3139I IMS INITIALIZED,\n                                                                          AUTOMATIC RESTART PROCEEDING\n                                                                          IM4A\n                                                  008 R MV2C     STC13493 *008 HWSC0000I *IMS CONNECT READY*\n                                                                          IM5DCONN\n                                                  007 R MV2C     STC13484 *007 HWSC0000I *IMS CONNECT READY*\n                                                                          IM4ACONN\n                                                  006 R MV2C     STC13480 *006 HWSC0000I *IMS CONNECT READY*\n                                                                          IM4DCONN\n                                                  005 R MV2C     STC13489 *005 HWSC0000I *IMS CONNECT READY*\n                                                                          IM5ACONN\n                                                  004 R MV2C     STC13395 *004 VAMP 0670 : ENTER COMMAND FOR\n                                                                          IYCWZVMP\n                                                  001 R MV2C              *001 DSI802A IYCWN    REPLY WITH VALID\n                                                                          NCCF SYSTEM OPERATOR COMMAND'
# dummy result for operator command 'd r,a,jn'
operator_message2 = 'MV2C      2019361  03:00:04.57             ISF031I CONSOLE XIAOPIN ACTIVATED\nMV2C      2019361  03:00:04.57            -D R,A,JN\nMV2C      2019361  03:00:04.58             IEE112I 03.00.04 PENDING REQUESTS 619\n                                           RM=37   IM=0     CEM=0     EM=0     RU=0    IR=0    NOAMRF\n                                           ID:R/K     T JOB ID   MESSAGE TEXT\n                                                  466 R IM5HCTRL *466 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART\n                                                                  PROCEEDING         IM5H\n                                                  465 R IM5HCONN *465 HWSC0000I *IMS CONNECT READY*  IM5HCONN\n                                                  216 R IM5GCTRL *216 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART\n                                                                  PROCEEDING         IM5G\n                                                  215 R IM5GCONN *215 HWSC0000I *IMS CONNECT READY*  IM5GCONN\n                                                  183 R VAMP     *183 VAMP 0670 : ENTER COMMAND FOR IYCQZVMP\n                                                  182 R MQNVIEW  *182 DSI802A IYM26    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  178 R NETVIEW  *178 DSI802A IYCQN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  134 R MQNVIEW  *134 DSI802A IYM2I    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  133 R VAMP     *133 VAMP 0670 : ENTER COMMAND FOR IYCIZVMP\n                                                  116 R VAMP     *116 VAMP 0670 : ENTER COMMAND FOR IYDCZVMP\n                                                  130 R NETVIEW  *130 DSI802A IYCIN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  101 R VAMP     *101 VAMP 0670 : ENTER COMMAND FOR IYDBZVMP\n                                                  113 R NETVIEW  *113 DSI802A IYDCN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  088 R IM5FCTRL *088 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART\n                                                                  PROCEEDING         IM5F\n                                                  087 R IM5FCONN *087 HWSC0000I *IMS CONNECT READY*  IM5FCONN\n                                                  086 R MQNVIEW  *086 DSI802A IYM2D    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  085 R VAMP     *085 VAMP 0670 : ENTER COMMAND FOR IYCXZVMP\n                                                  098 R NETVIEW  *098 DSI802A IYDBN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  070 R MQNVIEW  *070 DSI802A IYM29    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  069 R VAMP     *069 VAMP 0670 : ENTER COMMAND FOR IY29ZVMP\n                                                  082 R NETVIEW  *082 DSI802A IYCXN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  054 R IYCWEHCM @054 DFHSI1538D  IYCWEHCM Install GRPLIST\n                                                                 Errors. Is startup to be continued - Enter GO or\n                                                                  CANCEL.\n                                                  053 R MQNVIEW  *053 DSI802A IYM28    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  052 R VAMP     *052 VAMP 0670 : ENTER COMMAND FOR IYCSZVMP\n                                                  066 R NETVIEW  *066 DSI802A IY29N    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  038 R MQNVIEW  *038 DSI802A IYM27    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  037 R VAMP     *037 VAMP 0670 : ENTER COMMAND FOR IYCRZVMP\n                                                  049 R NETVIEW  *049 DSI802A IYCSN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  034 R NETVIEW  *034 DSI802A IYCRN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND\n                                                  010 R IM5ACTRL *010 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART\n                                                                  PROCEEDING         IM5A\n                                                  009 R IM4ACTRL *009 DFS3139I IMS INITIALIZED, AUTOMATIC RESTART\n                                                                  PROCEEDING         IM4A\n                                                  008 R IM5DCONN *008 HWSC0000I *IMS CONNECT READY*  IM5DCONN\n                                                  007 R IM4ACONN *007 HWSC0000I *IMS CONNECT READY*  IM4ACONN\n                                                  006 R IM4DCONN *006 HWSC0000I *IMS CONNECT READY*  IM4DCONN\n                                                  005 R IM5ACONN *005 HWSC0000I *IMS CONNECT READY*  IM5ACONN\n                                                  004 R VAMP     *004 VAMP 0670 : ENTER COMMAND FOR IYCWZVMP\n                                                  001 R NETVIEW  *001 DSI802A IYCWN    REPLY WITH VALID NCCF\n                                                                 SYSTEM OPERATOR COMMAND"'

operator_result1 = {
    'rc': 0,
    'message': operator_message1
}
operator_result2 = {
    'rc': 0,
    'message': operator_message2
}
operator_result3 = {
    'rc': 1,
    'message': None
}


test_data = [
    (dummy_dict1, dummy_dict1_result, True),
    (dummy_dict2, dummy_dict2_result, True),
    (dummy_dict3, dummy_dict3_result, True),
    (dummy_dict4, dummy_dict4_result, True),
    (dummy_dict5_uppercase, dummy_dict5_result, True),
    (dummy_dict5_lowercase, dummy_dict5_result, True),
    (dummy_dict6, dummy_dict6_result, True),
    (dummy_dict7, dummy_dict7_result, False),
    (dummy_dict_invalid_message, dummy_dict7_result, False),
    (dummy_dict_invalid_job_name, dummy_dict7_result, False),
    (dummy_dict_invalid_system, dummy_dict7_result, False),
    (dummy_dict_invalid_number, dummy_dict7_result, False)
]
test_data = [
    (dummy_dict1, True),
    (dummy_dict2, True),
    (dummy_dict3, True),
    (dummy_dict4, True),
    (dummy_dict5_uppercase, True),
    (dummy_dict5_lowercase, True),
    (dummy_dict6, True),
    (dummy_dict7, False),
    (dummy_dict_invalid_message, False),
    (dummy_dict_invalid_job_name, False),
    (dummy_dict_invalid_system, False),
    (dummy_dict_invalid_number, False)
]

@pytest.mark.parametrize("args,expected", test_data)
def test_zos_operator_openquestion_various_args(zos_import_mocker, args, expected):
    mocker, importer = zos_import_mocker
    zos_operator_openquestion = importer(IMPORT_NAME)
    passed = True
    mocker.patch('zoautil_py.OperatorCmd.execute',
                create=True, side_effect=[operator_result1,operator_result2])
    try:
        zos_operator_openquestion.find_required_request(args)
    except zos_operator_openquestion.Error:
        passed = False
    except TypeError as e:
        # MagicMock throws TypeError when input args is None
        # But if it gets that far we consider it passed
        if 'MagicMock' not in str(e):
            passed = False
    assert passed == expected

def test__zos_operator_openquestion_failed_to_run_first_operator_command(zos_import_mocker):
    mocker, importer = zos_import_mocker
    passed = False
    params = {'request_number_list': ['001','010']}
    zos_operator_openquestion = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.OperatorCmd.execute',
                create=True, side_effect=[operator_result3,operator_result2])
    try:
        zos_operator_openquestion.find_required_request(params)
    except zos_operator_openquestion.OperatorCmdError:
        passed = True
    assert passed == True

def test__zos_operator_openquestion_failed_to_run_second_operator_command(zos_import_mocker):
    mocker, importer = zos_import_mocker
    passed = False
    params = {'request_number_list': [ '001','010' ]}
    zos_operator_openquestion = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.OperatorCmd.execute',
                create=True, side_effect=[operator_result1,operator_result3])
    try:
        zos_operator_openquestion.find_required_request(params)
    except zos_operator_openquestion.OperatorCmdError:
        passed = True
    assert passed == True

def test__zos_operator_openquestion_failed_to_run_all_operator_command(zos_import_mocker):
    mocker, importer = zos_import_mocker
    passed = False
    params = {'request_number_list': ['001','010']}
    zos_operator_openquestion = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.OperatorCmd.execute',
                create=True, side_effect=[operator_result3,operator_result3])
    try:
        zos_operator_openquestion.find_required_request(params)
    except zos_operator_openquestion.OperatorCmdError:
        passed = True
    assert passed == True

def test__zos_operator_openquestion_missing_all_params(zos_import_mocker):
    mocker, importer = zos_import_mocker
    passed = True
    zos_operator_openquestion = importer(IMPORT_NAME)
    params={'request_number_list': ['all']}
    mocker.patch('zoautil_py.OperatorCmd.execute',
                create=True, side_effect=[operator_result1,operator_result2])
    list = []
    try:
        list= zos_operator_openquestion.find_required_request(params)
    except zos_operator_openquestion.OperatorCmdError:
        pass
    assert len(list) != 0


def test__zos_operator_openquestion_empty_list(zos_import_mocker):
    mocker, importer = zos_import_mocker
    operator_result = {
    'rc': 0,
    'message': 'abcde eedfx ddessdf dddess'
    }
    list = []
    passed = False
    params = {'request_number_list': [ '001' ,'010' ]}
    zos_operator_openquestion = importer(IMPORT_NAME)
    mocker.patch('zoautil_py.OperatorCmd.execute',
                create=True, return_value=operator_result)
    try:
        list = zos_operator_openquestion.find_required_request(params)
    except zos_operator_openquestion.OperatorCmdError:
        passed = False
    assert len(list) == 0
