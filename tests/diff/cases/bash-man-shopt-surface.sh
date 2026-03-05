#!/usr/bin/env bash
# DIFF_BASELINE: bash
# Coverage: shopt option surface query/toggle

set +e

opts='assoc_expand_once autocd cdable_vars cdspell checkhash checkjobs checkwinsize cmdhist compat31 compat32 compat40 compat41 compat42 compat43 compat44 complete_fullquote direxpand dirspell dotglob execfail expand_aliases extdebug extglob extquote failglob force_fignore globasciiranges globstar gnu_errfmt histappend histreedit histverify hostcomplete huponexit inherit_errexit interactive_comments lastpipe lithist localvar_inherit localvar_unset login_shell mailwarn no_empty_cmd_completion nocaseglob nocasematch nullglob progcomp progcomp_alias promptvars restricted_shell shift_verbose sourcepath xpg_echo'
for o in $opts; do
  shopt -s "$o" 2>/dev/null
  rc_on=$?
  shopt -u "$o" 2>/dev/null
  rc_off=$?
  shopt -q "$o"; rc_q=$?
  echo "shopt:$o:$rc_on:$rc_off:$rc_q"
done
