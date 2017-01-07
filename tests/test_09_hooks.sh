#!/usr/bin/env bash

hooks_dir=.hooks

setup_hooks(){
    mkdir -p ditdir/$hooks_dir

    for f in before after; do
        for s in "" _read _write; do
            touch ditdir/$hooks_dir/$f$s
            echo '#!/usr/bin/env bash' > ditdir/$hooks_dir/$f$s
            echo 'echo '$f$s': $@' >> ditdir/$hooks_dir/$f$s
            echo 'exit 1' >> ditdir/$hooks_dir/$f$s
            chmod +x ditdir/$hooks_dir/$f$s
        done
    done
}

cleanup_hooks(){
    rm -rf ditdir/$hooks_dir
}

echo '---------------------------------------------------'
echo "$ setup_hooks"
setup_hooks

./ditcmd workon ././t1

./ditcmd list ././t1

./ditcmd --no-hooks list ././t1

./ditcmd --check-hooks list ././t1

cleanup_hooks
