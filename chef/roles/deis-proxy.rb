name "deis-proxy"
description "Deis PaaS Proxy"
run_list "recipe[deis]", "recipe[deis::proxy]"
#env_run_lists "prod" => ["recipe[apache2]"], "staging" => ["recipe[apache2::staging]"], "_default" => []
#default_attributes "apache2" => { "listen_ports" => [ "80", "443" ] }
#override_attributes "apache2" => { "max_children" => "50" }
