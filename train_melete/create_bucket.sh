BUCKET_NAME="wintermute_perception_staging"
#PROJECT_ID=$(gcloud config list project --format "value(core.project)")
#BUCKET_NAME=${PROJECT_ID}-aiplatform
echo $BUCKET_NAME
REGION=us-central1
gsutil mb -l $REGION gs://$BUCKET_NAME
