#!/bin/bash
######################################################################
# User-configurable parameters
######################################################################
dataset_name="3dsr2000" #choose from [mipnerf360, llff]
dataset_path="C:/Users/han/Desktop/vggt_colmap"
# GPU IDs
gpu=0
# HR resolution downscale factor
HR_factor=1
# Number of GS training iterations for each diffusion step
GS_iters=2000
# Pretrained LR model path
output_dir="./outputs/LR_pretrained/input_DS_$((HR_factor * 4))"
# Define 3DSR experiment directory    
exp_dir="./outputs/${dataset_name}/load_DS_$((HR_factor * 4))"
######################################################################s


scenes=(
    "NorthAreas_g"
    "EastResearchAreas_g"
)
# Loop through each scene
for scene in "${scenes[@]}"; do    

    #################
    # Training 3DSR
    #################    
    echo "🛠️  Starting Training: $scene ..."
    export NUM_ITERS=${GS_iters}
    OMP_NUM_THREADS=4 CUDA_VISIBLE_DEVICES=$gpu python train_3dsr.py \
        -s ${dataset_path}/${scene} \
        -m ${output_dir}/${scene} \
        -r $HR_factor \
        --port $((6000 + gpu)) \
        --output_folder ${exp_dir} \
        --load_pretrain \
        --kernel_size 0.1 \
        --config ./configs/stableSRNew/v2-finetune_text_T_512.yaml \
        --ckpt ./third_parties/weights/stablesr_turbo.ckpt \
        --init-img ${dataset_path}/${scene}/images_$((HR_factor * 4)) \
        --outdir ${exp_dir}/${scene} \
        --ddpm_steps 3 \
        --dec_w 0.5 \
        --seed 42 \
        --n_samples 2 \
        --vqgan_ckpt ./third_parties/weights/vqgan_cfw_00011.ckpt \
        --colorfix_type wavelet \
        --upscale 4 \
        --fidelity_train_en \
        --wt_lr 1 \
        --densify_end $((NUM_ITERS / 2))
    
done