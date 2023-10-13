# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_subnetwork

# Internet Assigned Numbers Authority (IANA) standard -- ips reserved for local networks :
# 10.0.0.0 to 10.255.255.255 (10.0.0.0/8) 
# 172.16.0.0 to 172.31.255.255 (172.16.0.0/12)
# 192.168.0.0 to 192.168.255.255 (192.168.0.0/16)
resource "google_compute_subnetwork" "private" {
  name                     = "private"
  ip_cidr_range            = "10.0.0.0/18" 
  region                   = "europe-west9"
  network                  = google_compute_network.main.id
  private_ip_google_access = true

  secondary_ip_range {
    range_name    = "k8s-pod-range"
    ip_cidr_range = "10.48.0.0/14"
  }
  secondary_ip_range {
    range_name    = "k8s-service-range"
    ip_cidr_range = "10.52.0.0/20"
  }
}
