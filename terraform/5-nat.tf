# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router_nat

# A NAT is used to allow vm devoid of public ip to make requests to the internet

resource "google_compute_router_nat" "nat" {
  name   = "nat"
  router = google_compute_router.router.name
  region = "europe-west9"

  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"    # Manually define subnets to use Nat on
  nat_ip_allocate_option             = "MANUAL_ONLY"            # Manually define the ip used by the nat (see resource below)

  # Perform nat on all ips of the private subnetwork
  subnetwork {
    name                    = google_compute_subnetwork.private.id
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }

  nat_ips = [google_compute_address.nat.self_link]
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_address
resource "google_compute_address" "nat" {
  name         = "nat"
  address_type = "EXTERNAL"
  network_tier = "PREMIUM"

  depends_on = [google_project_service.compute]
}
