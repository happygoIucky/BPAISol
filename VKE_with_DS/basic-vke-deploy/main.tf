    terraform {
      required_providers {
        byteplus = {
          source  = "byteplus-sdk/byteplus"
          version = "0.0.17" 
        }
      }
    }
    provider "byteplus" {
      access_key    = "yourak"
      secret_key    = "yoursk"
      region        = "ap-southeast-1"
      endpoint      = "open.ap-southeast-1.byteplusapi.com"
    }

    provider "kubernetes" {
      config_path = "~/.kube/config"
    }

    data "byteplus_zones" "foo" { 
    }

    resource "byteplus_vpc" "foo" {
      vpc_name   = "jawn-vke-vpc"
      cidr_block = "192.168.0.0/16"
    }

    resource "byteplus_subnet" "foo" {
      subnet_name = "jawn-vke-subnet"
      cidr_block  = "192.168.0.0/24"
      zone_id     = "ap-southeast-1b"
      vpc_id      = byteplus_vpc.foo.id
    }

    resource "byteplus_nat_gateway" "foo" {
      vpc_id           = byteplus_vpc.foo.id
      subnet_id        = byteplus_subnet.foo.id
      spec             = "Small"
      nat_gateway_name = "jawn-vke-ng"
      description      = "jawn-vke"
      billing_type     = "PostPaid"
      project_name     = "default"
    }

    resource "byteplus_eip_address" "foo" {
      name         = "jawn-vke-eip"
      description  = "jawn-vke"
      bandwidth    = 1
      billing_type = "PostPaidByBandwidth"
      isp          = "BGP"
    }

    resource "byteplus_eip_associate" "foo" {
      allocation_id = byteplus_eip_address.foo.id
      instance_id   = byteplus_nat_gateway.foo.id
      instance_type = "Nat"
    }

    resource "byteplus_snat_entry" "foo" {
      snat_entry_name = "jawn-vke-snat-entry"
      nat_gateway_id  = byteplus_nat_gateway.foo.id
      eip_id          = byteplus_eip_address.foo.id
      source_cidr     = "192.168.0.0/24"
      depends_on      = ["byteplus_eip_associate.foo"]
    }
    resource "byteplus_security_group" "foo" {
      security_group_name = "jawn-vke-security-group"
      vpc_id              = byteplus_vpc.foo.id
    }

    data "byteplus_images" "foo" {
      name_regex = "veLinux 1.0 CentOS兼容版 64位"
    }

    resource "byteplus_vke_cluster" "foo" {
      name                      = "jawn-vke-cluster"
      description               = "created by terraform"
      delete_protection_enabled = false
      cluster_config {
        subnet_ids                       = [byteplus_subnet.foo.id]
        api_server_public_access_enabled = true
        api_server_public_access_config {
          public_access_network_config {
            billing_type = "PostPaidByBandwidth"
            bandwidth    = 1
          }
        }
        resource_public_access_default_enabled = true
      }
      pods_config {
        pod_network_mode = "VpcCniShared"
        vpc_cni_config {
          subnet_ids = [byteplus_subnet.foo.id]
        }
      }
      services_config {
        service_cidrsv4 = ["172.30.0.0/18"]
      }
      tags {
        key   = "tf-k1"
        value = "tf-v1"
      }
    }

    resource "byteplus_vke_node_pool" "foo" {
      cluster_id = byteplus_vke_cluster.foo.id
      name       = "jawn-vke-node-pool"
      auto_scaling {
        enabled = false
      }
      node_config {
        instance_type_ids = ["ecs.g3il.2xlarge"]
        subnet_ids        = [byteplus_subnet.foo.id]
        image_id          = "image-yce62qvi49bhcbf53gw5"
        system_volume {
          type = "ESSD_PL0"
          size = "200"
        }
        data_volumes {
          type        = "ESSD_PL0"
          size        = "200"
          mount_point = "/tf"
        }
        initialize_script = "ZWNobyBoZWxsbyB0ZXJyYWZvcm0h"
        security {
          login {
            password = "yourpw"
          }
          security_strategies = ["Hids"]
          security_group_ids  = [byteplus_security_group.foo.id]
        }
        additional_container_storage_enabled = true
        instance_charge_type                 = "PostPaid"
        name_prefix                          = "jawn-vke"
        //ecs_tags {
        //  key   = "ecs_k1"
        //  value = "ecs_v1"
        //}
      }
      kubernetes_config {
        labels {
          key   = "label1"
          value = "value1"
        }
        //taints {
        //  key    = "taint-key/node-type"
        //  value  = "taint-value"
        //  effect = "NoSchedule"
        //}
        cordon = false
      }
      tags {
        key   = "node-pool-k1"
        value = "node-pool-v1"
      }
    }

    resource "byteplus_ecs_instance" "foo" {
      instance_name        = "jawn-vke-ecs-${count.index}"
      host_name            = "tf-jawn-vke"
      image_id             = "image-yce62qvi49bhcbf53gw5"
      instance_type        = "ecs.g3il.2xlarge"  # change to your desired instance
      password             = "yourpw"
      instance_charge_type = "PostPaid"
      system_volume_type   = "ESSD_PL0"
      system_volume_size   = 200
      data_volumes {
        volume_type          = "ESSD_PL0"
        size                 = 200
        delete_with_instance = true
      }
      subnet_id          = byteplus_subnet.foo.id
      security_group_ids = [byteplus_security_group.foo.id]
      project_name       = "default"
      //tags {
      //  key   = "k1"
      //  value = "v1"
      //}
      lifecycle {
        ignore_changes = [security_group_ids, instance_name]
      }
      count = 2
    }

    resource "byteplus_vke_node" "foo" {
      cluster_id   = byteplus_vke_cluster.foo.id
      instance_id  = byteplus_ecs_instance.foo[count.index].id
      node_pool_id = byteplus_vke_node_pool.foo.id
      count        = 2
    }

    data "byteplus_vke_nodes" "foo" {
      ids = byteplus_vke_node.foo[*].id
    }

    # kubeconfig
    resource "byteplus_vke_kubeconfig" "foo" {
      cluster_id     = byteplus_vke_cluster.foo.id
      type           = "Public"
      valid_duration = 43800
    }

    data "byteplus_vke_kubeconfigs" "foo" {
      ids = [byteplus_vke_kubeconfig.foo.id]
    }

    output "kubeconfig" {
      value = base64decode(data.byteplus_vke_kubeconfigs.foo.kubeconfigs[0].kubeconfig)
    }

    resource "byteplus_vke_addon" "nas" {
      cluster_id       = byteplus_vke_cluster.foo.id
      name             = "csi-nas"
    }

    resource "byteplus_vke_addon" "dns" {
      cluster_id       = byteplus_vke_cluster.foo.id
      name             = "core-dns"
    }
    
    resource "byteplus_vke_addon" "gpu" {
      cluster_id       = byteplus_vke_cluster.foo.id
      name             = "nvidia-device-plugin"
    }

    //save config to my mac machine, you can change the path accordingly in case u use windows
    resource "null_resource" "write_kubeconfig" {
      provisioner "local-exec" {
        command = "terraform output -raw kubeconfig > ~/.kube/config'"
      }
      depends_on = [byteplus_vke_kubeconfig.foo]
    }