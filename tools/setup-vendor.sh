#!/bin/sh
# Recupere les sources de mist64 a la version testee et applique les modifications du projet.
set -eu
cd "$(dirname "$0")/.."
fetch() {
    name=$1 commit=$2
    if [ ! -d "vendor/$name" ]; then
        git clone -q "https://github.com/mist64/$name" "vendor/$name"
        git -C "vendor/$name" checkout -q "$commit"
        git -C "vendor/$name" apply "../../patches/$name.patch"
        echo "vendor/$name : version $commit, modifications appliquees"
    fi
}
mkdir -p vendor
fetch geos 617efdc7191eda14eaf699d317e66d5bda68c039
fetch geowrite 640f1aba3a68c096c56fafc81b55772db391de35
