Ash__CONFIG_FILENAME="ash_config.yaml"
Ash__TRUE="true"
Ash__FALSE="false"
Ash__CALL_DIRECTORY="."

Logger__error() {
  echo "ERROR: $*"
}

Logger__alert() {
  echo "ALERT: $*"
}

Logger__success() {
  echo "SUCCESS: $*"
}

Ash__find_module_directory() {
  local module="$1"
  if test -d "$module"; then
    echo "$module"
  fi
}

Ash_load_callable_file() {
  return 0
}

Ash__import() {
  return 0
}

YamlParse__parse() {
  # Minimal parser for test_prefix in ash_config.yaml
  local path="$1"
  local prefix_var="$2"
  local value
  value=$(grep '^test_prefix:' "$path" | sed 's/test_prefix:[[:space:]]*//')
  if test -n "$value"; then
    echo "${prefix_var}test_prefix=$value"
  fi
}
