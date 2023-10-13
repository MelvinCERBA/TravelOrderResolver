# How to Create GKE Cluster Using TERRAFORM?
credits: Tutorial by Anton Putra ( https://antonputra.com/google/create-gke-cluster-using-terraform/#apply-terraform )
## Setup Terraform GCP Provider
First of all, we need to declare a terraform provider. You can think of it as a library with methods to create and manage infrastructure in a specific environment. In this case, it is a Google Cloud Platform.

*1-provider.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs  
provider "google" {  
  project = "<project-id>"  
  region  = "us-central1"  
}  
```


## Configure Terraform GCS Backend
When you create resources in GCP such as VPC, Terraform needs a way to keep track of them. If you simply apply terraform right now, it will keep all the state locally on your computer. It's very hard to collaborate with other team members and easy to accidentally destroy all your infrastructure. You can declare Terraform backend to use remote storage instead. Since we're creating infrastructure in GCP, the logical approach would be to use Google Storage Bucket to store Terraform state. You need to provide a bucket name and a prefix.

*1-provider.tf*
```
# https://www.terraform.io/language/settings/backends/gcs  
terraform {  
  backend "gcs" {  
    bucket = "<your-bucket>"  
    prefix = "terraform/state"  
  }  
  required_providers {  
    google = {  
      source  = "hashicorp/google"  
      version = "~> 4.0"  
    }  
  }  
}  
```
## Create VPC in GCP using Terraform¶
Nothing stops you from using the existing VPC to create a Kubernetes cluster, but I will create all the infrastructure using Terraform for this lesson. For example, instead of resource, you can use data keyword to import it to Terraform. Before creating VPC in a new GCP project, you need to enable compute API. To create a GKE cluster, you also need to enable container google API.

*2-vpc.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_service
resource "google_project_service" "compute" {
  service = "compute.googleapis.com"
}

resource "google_project_service" "container" {
  service = "container.googleapis.com"
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_network
resource "google_compute_network" "main" {
  name                            = "main"
  routing_mode                    = "REGIONAL"
  auto_create_subnetworks         = false
  mtu                             = 1460
  delete_default_routes_on_create = false

  depends_on = [
    google_project_service.compute,
    google_project_service.container
  ]
}
```

## Create Subnet in GCP using Terraform
The next step is to create a private subnet to place Kubernetes nodes. When you use the GKE cluster, the Kubernetes control plane is managed by Google, and you only need to worry about the placement of Kubernetes workers.

*3-subnets.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_subnetwork
resource "google_compute_subnetwork" "private" {
  name                     = "private"
  ip_cidr_range            = "10.0.0.0/18"
  region                   = "us-central1"
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
```

## Create Cloud Router in GCP using Terraform¶
Next, we need to create Cloud Router to advertise routes. It will be used with the NAT gateway to allow VMs without public IP addresses to access the internet. For example, Kubernetes nodes will be able to pull docker images from the docker hub.

*4-router.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router
resource "google_compute_router" "router" {
  name    = "router"
  region  = "us-central1"
  network = google_compute_network.main.id
}
```

## Create Cloud NAT in GCP using Terraform¶
Now, let's create Cloud NAT. Give it a name and a reference to the Cloud Router. Then the region us-central1. You can decide to advertise this Cloud NAT to all subnets in that VPC, or you can select specific ones. In this example, I will choose the private subnet only.

*5-nat.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_router_nat
resource "google_compute_router_nat" "nat" {
  name   = "nat"
  router = google_compute_router.router.name
  region = "us-central1"

  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"
  nat_ip_allocate_option             = "MANUAL_ONLY"

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
```

## Create Firewall in GCP using Terraform¶
The next resource is a firewall. We don't need to create any firewalls manually for GKE; it's just to give you an example. This firewall will allow sshing to the compute instances within VPC.

*6-firewalls.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_firewall
resource "google_compute_firewall" "allow-ssh" {
  name    = "allow-ssh"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
}
```

## Create GKE Cluster Using Terraform¶
Finally, we got to Kubernetes resource. First, we need to configure the control plane of the cluster itself.

*7-kubernetes.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_cluster
resource "google_container_cluster" "primary" {
  name                     = "primary"
  location                 = "us-central1-a"
  remove_default_node_pool = true
  initial_node_count       = 1
  network                  = google_compute_network.main.self_link
  subnetwork               = google_compute_subnetwork.private.self_link
  logging_service          = "logging.googleapis.com/kubernetes"
  monitoring_service       = "monitoring.googleapis.com/kubernetes"
  networking_mode          = "VPC_NATIVE"

  # Optional, if you want multi-zonal cluster
  node_locations = [
    "us-central1-b"
  ]

  addons_config {
    http_load_balancing {
      disabled = true
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  release_channel {
    channel = "REGULAR"
  }

  workload_identity_config {
    workload_pool = "devops-v4.svc.id.goog"
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "k8s-pod-range"
    services_secondary_range_name = "k8s-service-range"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  #   Jenkins use case
  #   master_authorized_networks_config {
  #     cidr_blocks {
  #       cidr_block   = "10.0.0.0/18"
  #       display_name = "private-subnet-w-jenkins"
  #     }
  #   }
}
```

## Create GKE Node Pools using Terraform¶
Before we can create node groups for Kubernetes, if we want to follow best practices, we need to create a dedicated service account. In this tutorial, we will create two node groups.

*8-node-pools.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_service_account
resource "google_service_account" "kubernetes" {
  account_id = "kubernetes"
}

# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/container_node_pool
resource "google_container_node_pool" "general" {
  name       = "general"
  cluster    = google_container_cluster.primary.id
  node_count = 1

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = false
    machine_type = "e2-small"

    labels = {
      role = "general"
    }

    service_account = google_service_account.kubernetes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

resource "google_container_node_pool" "spot" {
  name    = "spot"
  cluster = google_container_cluster.primary.id

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  autoscaling {
    min_node_count = 0
    max_node_count = 10
  }

  node_config {
    preemptible  = true
    machine_type = "e2-small"

    labels = {
      team = "devops"
    }

    taint {
      key    = "instance_type"
      value  = "spot"
      effect = "NO_SCHEDULE"
    }

    service_account = google_service_account.kubernetes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
```

## Apply Terraform
To run Terraform locally on your computer, you need to configure default application credentials. Run gcloud auth application-default login command. It will open the default browser, where you would need to complete authorization.

> gcloud auth application-default login

The first command that you need to run is terraform init. It will download google provider and initialize the Terraform backend to use GS bucket. To actually create all those resources that we defined in Terraform, we need to run terraform apply.

> terraform init
> terraform apply

## GKE Autoscaling Demo (Example 1)¶
Now let's deploy a few examples to the Kubernetes. The first one is the deployment object to demonstrate cluster autoscaling. Let's use the nginx image and set two replicas. We want to deploy it to the spot instance group that does not have any nodes right now.

*1-example.yaml*
```
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: default
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
      tolerations:
      - key: instance_type
        value: spot
        effect: NoSchedule
        operator: Equal
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: team
                operator: In
                values:
                - devops
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - nginx
            topologyKey: kubernetes.io/hostname
```
We can use the kubectl apply command and provide a path to the folder or file, in this case, example one.

> kubectl apply -f k8s/1-example.yaml

## GKE Workload Identity Tutorial (Example 2)
In the following example, I'll show you how to use workload identity and grant access for the pod to list GS buckets. First of all, we need to create a service account in the Google Cloud Platform.

*9-service-account.tf*
```
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_service_account
resource "google_service_account" "service-a" {
  account_id = "service-a"
}

\# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_project_iam
resource "google_project_iam_member" "service-a" {
  project = "devops-v4"
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.service-a.email}"
}

\# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/google_service_account_iam
resource "google_service_account_iam_member" "service-a" {
  service_account_id = google_service_account.service-a.id
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:devops-v4.svc.id.goog[staging/service-a]"
}
```
Time to create the second example. The first will be a staging namespace. Then the deployment. Give it a name gcloud and specify the same staging namespace.

*2-example.yaml*
```
---
apiVersion: v1
kind: Namespace
metadata:
  name: staging
---
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    iam.gke.io/gcp-service-account: service-a@devops-v4.iam.gserviceaccount.com
  name: service-a
  namespace: staging
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gcloud
  namespace: staging
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gcloud
  template:
    metadata:
      labels:
        app: gcloud
    spec:
      serviceAccountName: service-a
      containers:
      - name: cloud-sdk
        image: google/cloud-sdk:latest
        command: [ "/bin/bash", "-c", "--" ]
        args: [ "while true; do sleep 30; done;" ]
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: iam.gke.io/gke-metadata-server-enabled
                operator: In
                values:
                - "true"
```

Create Deployment object

> kubectl apply -f k8s/2-example.yaml

## Deploy Nginx Ingress Controller on GKE (Example 3)¶
For the last example, let me deploy the nginx ingress controller using the helm. Add the ingress-nginx repository.

> helm repo add ingress-nginx \
>  https://kubernetes.github.io/ingress-nginx

Update Helm Index

> helm repo update

To override some default variables, create the nginx-values.yaml file.

*nginx-values.yaml*
```
---
controller:
  config:
    compute-full-forwarded-for: "true"
    use-forwarded-headers: "true"
    proxy-body-size: "0"
  ingressClassResource:
    name: external-nginx
    enabled: true
    default: false
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
            - key: app.kubernetes.io/name
              operator: In
              values:
                - ingress-nginx
        topologyKey: "kubernetes.io/hostname"
  replicaCount: 1
  admissionWebhooks:
    enabled: false
  service:
    annotations:
      cloud.google.com/load-balancer-type: External
  metrics:
    enabled: false

helm install my-ing ingress-nginx/ingress-nginx \
  --namespace ingress \
  --version 4.0.17 \
  --values nginx-values.yaml \
  --create-namespace
We will reuse the deployment object created earlier for the autoscaling demo. This service will select those pods by using the app: nginx label. Then the ingress itself.

3-example.yaml

---
apiVersion: v1
kind: Service
metadata:
  name: nginx
  namespace: default
spec:
  selector:
    app: nginx
  ports:
    - protocol: TCP
      port: 80
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: nginx-ing
  namespace: default
spec:
  ingressClassName: external-nginx
  rules:
  - host: api.devopsbyexample.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 80
```

Create Service and Ingress.

> kubectl apply -f k8s/3-example.yaml