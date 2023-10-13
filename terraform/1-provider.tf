# https://registry.terraform.io/providers/hashicorp/google/latest/docs
provider "google" {
  project = "travelorderresolver-401809"
  region  = "europe-west9" # Paris
}

# https://www.terraform.io/language/settings/backends/gcs
terraform {
  backend "gcs" {
    bucket = "travel_order_bucket"
    prefix = "terraform/state"
  }
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}
