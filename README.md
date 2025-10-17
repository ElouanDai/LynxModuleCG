cd ../lina-mono
pnpm m ls --parseable > ../LynxModuleCG/out-module-list.txt
cd ../LynxModuleCG
python3 moduleFilter.py out-module-list.txt out-module-list-filtered.txt
python3 generate_module_tps_list.py out-module-list-filtered.txt ../lina-mono
python3 build_tp_list_set.py module_tps out-tp-list.json out-tp-list.txt
python3 generate_tp_func_list.py out-tp-list.txt ../lina-mono ../Jelly-Mod/lib/main.js
python3 get_tp_config.py out-tp-list.txt ../lina-mono tp_config
python3 generate_cg.py out-module-list-filtered.txt ../lina-mono cg
python3 enhance_cg.py cg cg-enhanced ../lina-mono out-tp-list.json tp_funcs
python3 filter_cg.py cg-enhanced cg-filtered ../lina-mono tp_config