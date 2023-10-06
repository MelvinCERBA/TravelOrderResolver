# Travel Order Resolver

This microservice application is composed of the following flask applications :
- NaturalLanguageProcessingService: takes in a travel order as text and defines what the origin and destination are.
- VoiceRecognitionService: takes in an audio, returns its transcription.
- TravelOptimizerService: takes in the origin and destination, and returns an optimized train itinerary between the two.
- Public API: This is the api that will be available to our end user. It will :
    1. Take in a travel order, either text or audio
    2. If the input is an audio file, request its transcription from the VoiceRecognitionService   
    3. Send the text travel order to the NaturalLanguageProcessingService to get the travel's origin and destination
    4. Send the origin and destination to the TravelOptimizerService
    5. Return the optimized travel plan to the user.

## Local testing

## Deployment

### Build the images and upload them to Docker Hub 
For each service :

1. Build and tag your image
> docker build -t your-username/your-image-name:your-tag .

2. Push it it to the docker hub registry
> docker login
> docker push your-username/your-image-name:your-tag

### Apply kubernetes manifests to cluster

#### Test the k8s deployment locally

1. Start the cluster
    > minikube start

2. Apply all manifests
    > kubectl apply -f ./k8s/

3. *(Optional)* Set up the ingress (nginx routing)
    - Enable minikube cluster's Ingress Controller
        > minikube addons enable ingress
    - Verify that the ingress controllers are set up
        > kubectl get pods --all-namespaces
    - Create a route from localhost to the Minikube cluster's services :
        > minikube tunnel
    - Add the services to your hosts file *(Your computer's dns will replace the service name with the cluster's ip when you request a service. The ingress controller can then use the header `"host":<service-name>.local` attached to your request to route it to the appropriate service )*
        > 127.0.0.1 nlp-service.local   
        > 127.0.0.1 voice-recognition-service.local   
        > 127.0.0.1 travel-optimizer-service.local   
        > 127.0.0.1 public-api.local    


4. See an overview the cluster
    > minikube dashboard

5. *(Optional: if ingress not set up)* Expose services to the outside of the cluster:
    > minikube service \<service-name\>

#### In production
