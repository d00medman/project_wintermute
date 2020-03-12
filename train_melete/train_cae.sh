MODEL_NAME=melete_cae_prototype
REGION=us-central1
TRAINER_PACKAGE_PATH=./trainer
MAIN_TRAINER_MODULE=trainer.task
PACKAGE_STAGING_PATH=gs://wintermute_perception_staging

CURRENT_DATE=`date +%Y%m%d_%H%M%S`
JOB_NAME=train_${MODEL_NAME}_${CURRENT_DATE}

gcloud ai-platform jobs submit training $JOB_NAME \
    --module-name=$MAIN_TRAINER_MODULE \
    --job-dir=$PACKAGE_STAGING_PATH  \
    --package-path=$TRAINER_PACKAGE_PATH \
    --config=config.yaml \
    --stream-logs \
    -- \
    --algorithm=cae \
    --epochs=3 \
    --cae-output-file=cloud_train_prototype.h5
