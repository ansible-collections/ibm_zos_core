stage('Run z/OS Ansible Pipeline') {
    build job: 'zosAnsible', parameters:[
        string(name: 'BRANCH', value: CHANGE_BRANCH),
    ]
}