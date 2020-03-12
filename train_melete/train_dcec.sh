CURRENT_DATE=$(date +%Y%m%d_%H%M%S)
MODEL_NAME=melete_dcec_prototype
JOB_NAME=train_${MODEL_NAME}_${CURRENT_DATE}
MAIN_TRAINER_MODULE=trainer.task
PACKAGE_STAGING_PATH=gs://wintermute_perception_staging
TRAINER_PACKAGE_PATH=./trainer

# todo: pass args in via config file
TYPE=f # f(ull screen) | g(rid square)
ALG=dcec # dcec | cae

gcloud ai-platform jobs submit training $JOB_NAME \
    --module-name=$MAIN_TRAINER_MODULE \
    --job-dir=$PACKAGE_STAGING_PATH  \
    --package-path=$TRAINER_PACKAGE_PATH \
    --config=config.yaml \
    --stream-logs \
    -- \
    --algorithm=$ALG \
    --type=$TYPE \
    --pretrain=true \
    --prototyping=true \
    --maxiter=50 \
    --clusters=5 \
    --epochs=10 \
    --data-set=train_and_test.p \
    --cae-file-name=cloud_train_test_cae.h5 \
    --dcec-output-file=cloud_train_test_dcec.h5