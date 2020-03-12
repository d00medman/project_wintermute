MODEL_NAME=melete_dcec_grid_prototype
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
    --algorithm=dcec \
    --type=g \
    --maxiter=50 \
    --epochs=10 \
    --clusters=5 \
    --data-set=grid_square_pickle.p \
    --cae-output-file=cloud_train_test_cae.h5 \
    --dcec-output-file=cloud_train_test_dcec.h5