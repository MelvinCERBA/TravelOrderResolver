# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router

# The router is there only to provide the necessary framework for the nat

resource "google_compute_router" "router" {
  name    = "router"
  region  = "europe-west9"
  network = google_compute_network.main.id
}
