for sens_file in raw_data_ScanNet/*/*.sens; do
    scene_id=$(echo $sens_file | cut -d'/' -f 2)
    echo "$sens_file -> datasets_ScanNet/$scene_id"
    python ScanNet/reader.py --rob --export_depth_images --export_color_images --export_intrinsics --filename "$sens_file" --output_path "datasets_ScanNet/$scene_id"
done