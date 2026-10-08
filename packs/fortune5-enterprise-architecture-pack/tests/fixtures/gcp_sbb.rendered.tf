# GENERATED from templates/gcp-sbb.tf.tera (rendered: sbbId=fin1,
# fleetHostProject=proj-host, serviceProject=proj-svc, pscSubnet=psc-subnet,
# keyringLocation=us-east1, one CMEK key member fin1-data-key).
# Fixture for tests/test_resource_graph.py.

resource "google_gke_hub_fleet" "sbb_fleet" {
  provider   = google-beta
  project    = "proj-host"
  location   = "global"
  name       = "sbb-fin1-fleet"
  default_cluster_config {
    security_posture_config {
      mode               = "ENTERPRISE"
      vulnerability_mode = "VULNERABILITY_AUTOMATIC"
    }
  }
}

resource "google_gke_hub_membership" "sbb_cluster" {
  provider   = google-beta
  project    = "proj-host"
  name       = "sbb-fin1-membership"
  endpoint {
    gke_cluster {
      resource_link = "//container.googleapis.com/projects/proj-svc/locations/us-east1/clusters/sbb-fin1"
    }
  }
}

resource "google_compute_shared_vpc_service_project" "svc_attach" {
  provider        = google-beta
  host_project    = "proj-host"
  service_project = "proj-svc"
}

resource "google_compute_firewall" "deny_all_ingress" {
  provider      = google-beta
  project       = "proj-host"
  name          = "sbb-fin1-deny-ingress"
  network       = "shared-vpc-host"
  direction     = "INGRESS"
  priority      = 1000
  source_ranges = ["0.0.0.0/0"]
  deny {
    protocol = "all"
  }
}

resource "google_compute_address" "psc_endpoint_ip" {
  provider     = google-beta
  project      = "proj-svc"
  name         = "sbb-fin1-psc-ip"
  subnetwork   = "psc-subnet"
  address_type = "INTERNAL"
}

resource "google_compute_forwarding_rule" "psc_endpoint" {
  provider              = google-beta
  project               = "proj-svc"
  name                  = "sbb-fin1-psc-endpoint"
  region                = "us-east1"
  network               = "shared-vpc-host"
  subnetwork            = "psc-subnet"
  ip_address            = google_compute_address.psc_endpoint_ip.id
  load_balancing_scheme = ""
  target                = google_compute_service_attachment.svc_att.id
  allow_global_access   = false
}

resource "google_compute_service_attachment" "svc_att" {
  provider              = google-beta
  project               = "proj-svc"
  name                  = "sbb-fin1-svc-attachment"
  region                = "us-east1"
  description           = "PSC service attachment, no public path"
  target_service        = google_compute_region_backend_service.svc.id
  nat_subnets           = ["psc-subnet"]
  connection_preference = "ACCEPT_MANUAL"
}

resource "google_compute_region_backend_service" "svc" {
  provider              = google-beta
  project               = "proj-svc"
  name                  = "sbb-fin1-backend"
  region                = "us-east1"
  protocol              = "HTTPS"
  load_balancing_scheme = "INTERNAL_MANAGED"
}

resource "google_kms_key_ring" "keyring" {
  provider = google-beta
  project  = "proj-svc"
  name     = "sbb-fin1-keyring"
  location = "us-east1"
}

resource "google_kms_crypto_key" "fin1_data_key" {
  provider                   = google-beta
  name                       = "fin1-data-key"
  key_ring                   = google_kms_key_ring.keyring.id
  purpose                    = "ENCRYPT_DECRYPT"
  rotation_period            = "7776000s"
  destroy_scheduled_duration = "86400s"
}
