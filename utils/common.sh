(return 0 2>/dev/null) || echo "bad" || exit 1

load_properties_from_file() {

	echo "3---"
	local xx=0
	trap -p EXIT | grep "cleanup_function" && xx=1
	echo "-->$xx<--"
	echo "---"

	verbose_echo "{Loading 'project.properties file'...}"
	while IFS='=' read -r key_value; do
		if [[ ${key_value} == \#* ]]; then
			continue
		fi
		key=$(echo "${key_value}" | cut -d '=' -f1)
		value=$(echo "${key_value}" | cut -d '=' -f2-)
		export "${key}=${value}"
	done <"${SCRIPT_DIR}/project.properties"

	if [[ -z ${PYTHON_MODULE_NAME} ]]; then
		complete_process 1 "Property 'PYTHON_MODULE_NAME' must be defined in the project.properties file."
	fi
}
