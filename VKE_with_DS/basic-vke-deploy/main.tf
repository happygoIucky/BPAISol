terraform {
  required_providers {
    byteplus = {
      source  = "byteplus-sdk/byteplus"
      version = "0.0.16"
    }
  }
}

provider "byteplus" {
  access_key = var.byteplus_access_key
  secret_key = var.byteplus_secret_key
  region     = var.region
}

#data "byteplus_zones" "foo" {}

resource "byteplus_vpc" "foo" {
  vpc_name   = "acc-test-vpc"
  cidr_block = "172.16.0.0/16"
}

resource "byteplus_subnet" "foo" {
  subnet_name = "acc-test-subnet"
  cidr_block  = "172.16.0.0/24"
  zone_id     = data.byteplus_zones.foo.zones[0].id
  vpc_id      = byteplus_vpc.foo.id
}

resource "byteplus_security_group" "foo" {
  security_group_name = "acc-test-security-group"
  vpc_id              = byteplus_vpc.foo.id
}

resource "byteplus_vke_cluster" "foo" {
  name                      = "acc-test-1"
  description               = "created by terraform"
  project_name              = "default"
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

data "byteplus_images" "foo" {
  name_regex = "veLinux 1.0 CentOS Compatible 64 bit"
}

resource "byteplus_vke_node_pool" "foo" {
  cluster_id = byteplus_vke_cluster.foo.id
  name       = "acc-test-node-pool"

  auto_scaling {
    enabled          = true
    min_replicas     = 1
    max_replicas     = 3
    desired_replicas = 0
    priority         = 5
    subnet_policy    = "ZoneBalance"
  }

  node_config {
    instance_type_ids = ["ecs.g1ie.xlarge"]
    subnet_ids        = [byteplus_subnet.foo.id]
    image_id          = [for image in data.byteplus_images.foo.images : image.image_id if image.image_name == "veLinux 1.0 CentOS Compatible 64 bit"][0]

    system_volume {
      type = "ESSD_PL0"
      size = 80
    }

    data_volumes {
      type        = "ESSD_PL0"
      size        = 80
      mount_point = "/tf1"
    }

    data_volumes {
      type        = "ESSD_PL0"
      size        = 60
      mount_point = "/tf2"
    }

    initialize_script = "ZWNobyBoZWxsbyB0ZXJyYWZvcm0h"

    security {
      login {
        password = "UHdkMTIzNDU2"
      }
      security_strategies = ["Hids"]
      security_group_ids  = [byteplus_security_group.foo.id]
    }

    additional_container_storage_enabled = false
    instance_charge_type                 = "PostPaid"
    name_prefix                          = "acc-test"
    #project_name                         = "default"

    ecs_tags {
      key   = "ecs_k1"
      value = "ecs_v1"
    }
  }

  kubernetes_config {
    labels {
      key   = "label1"
      value = "value1"
    }

    taints {
      key    = "taint-key/node-type"
      value  = "taint-value"
      effect = "NoSchedule"
    }

    cordon             = true
    #auto_sync_disabled = false
  }

  tags {
    key   = "node-pool-k1"
    value = "node-pool-v1"
  }
}

resource "byteplus_ecs_instance" "foo" {
  instance_name        = "acc-test-ecs-jl"
  host_name            = "tf-acc-test"
  image_id             = [for image in data.byteplus_images.foo.images : image.image_id if image.image_name == "veLinux 1.0 CentOS Compatible 64 bit"][0]
  instance_type        = "ecs.g1ie.xlarge"
  password             = "93f0cb0614Aab12"
  instance_charge_type = "PostPaid"
  system_volume_type   = "ESSD_PL0"
  system_volume_size   = 50
  subnet_id            = byteplus_subnet.foo.id
  security_group_ids   = [byteplus_security_group.foo.id]
  project_name         = "default"

  tags {
    key   = "k1"
    value = "v1"
  }

  lifecycle {
    ignore_changes = [security_group_ids, tags, instance_name]
  }
}

resource "byteplus_vke_node" "foo" {
  cluster_id   = byteplus_vke_cluster.foo.id
  instance_id  = byteplus_ecs_instance.foo.id
  node_pool_id = byteplus_vke_node_pool.foo.id
}
