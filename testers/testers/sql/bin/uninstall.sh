#!/usr/bin/env bash

drop_oracle_db() {
    echo "[SQL-UNINSTALL] Removing oracle user '${ORACLEUSER}' with database '${ORACLEDB}'"
    sudo -u postgres psql <<-EOF
		DROP DATABASE IF EXISTS ${ORACLEDB};
		DROP ROLE IF EXISTS ${ORACLEUSER};
	EOF
    sudo -u ${ORACLEUSER} -- bash -c 'rm -f ${HOME}/.pgpass'
}

drop_test_dbs() {
    for test_user in ${TESTUSERS}; do
        local test_db=${test_user}
        echo "[SQL-UNINSTALL] Removing test user '${test_user}' with database '${test_db}'"
        sudo -u postgres psql <<-EOF
			DROP DATABASE IF EXISTS ${test_db};
			DROP ROLE IF EXISTS ${test_user};
		EOF
    done
}

reset_specs() {
    echo "[SQL-UNINSTALL] Resetting specs"
    rm -f ${SPECSDIR}/install_settings.json
}

# script starts here
if [[ $# -ne 0 ]]; then
    echo "Usage: $0"
    exit 1
fi

# vars
THISSCRIPT=$(readlink -f ${BASH_SOURCE})
TESTERDIR=$(dirname $(dirname ${THISSCRIPT}))
SPECSDIR=${TESTERDIR}/specs
INSTALLSETTINGS=$(cat ${SPECSDIR}/install_settings.json)
ORACLEDB=$(echo ${INSTALLSETTINGS} | jq --raw-output .oracle_database)
ORACLEUSER=${ORACLEDB}
TESTUSERS=$(echo ${INSTALLSETTINGS} | jq --raw-output '.tests | .[] | .user')

# main
drop_oracle_db
drop_test_dbs
reset_specs
echo "[SQL-UNINSTALL] The following system packages have not been uninstalled: python3 postgresql jq. You may uninstall them if you wish."
rm -f ${SPECSDIR}/.installed