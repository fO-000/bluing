#!/usr/bin/env bash

_bluescan() {
    local pword cword opts modes le_scan_types result
    pword=${COMP_WORDS[COMP_CWORD-1]}
    cword=${COMP_WORDS[COMP_CWORD]}

    opts='-h --help -v --version -m -i --sort= --inquiry-len= --timeout= --le-scan-type='
    modes='le br LE BR'
    le_scan_types='active passive'
    sort_method='rssi RSSI'

    # echo -e '\n'
    # echo cmd: $cmd
    # echo pword: $pword
    # echo cword: $cword
    # echo COMP_CWORD: $COMP_CWORD

    case $cword in
    -*)
        result=($(compgen -W "$opts" -- $cword))
        ;;
    esac


    case $pword in
    -m)
        result=($(compgen -W "$modes" -- $cword))
        ;;
    =)
        if [ $COMP_CWORD -gt 1 ] && [ ${COMP_WORDS[COMP_CWORD-2]} = --le-scan-type ]; then
            result=($(compgen -W "$le_scan_types" -- $cword))
        fi

        if [ $COMP_CWORD -gt 1 ] && [ ${COMP_WORDS[COMP_CWORD-2]} = --sort ]; then
            result=($(compgen -W "$sort_method" -- $cword))
        fi        
        ;;
    esac

    if [ ${#result[*]} -ne 1 ]; then
        # 当匹配结果不唯一时，不把匹配结果传递给 bash
        result=('')
    fi

    COMPREPLY=$result
}

complete -F _bluescan bluescan
