for zip_file in datasets_ScanNet/*.zip; do
    echo "Unzipping $zip_file"
    unzip "$zip_file" -d datasets_ScanNet/
    rm "$zip_file"
done