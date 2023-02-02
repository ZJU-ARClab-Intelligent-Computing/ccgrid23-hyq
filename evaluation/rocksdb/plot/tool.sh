set +x


kernel_folder_fio="/home/jane/test-rocksdb/rocksdb-results/kernel"
kernel_files_fio=$(ls $kernel_folder_fio)
kernel_lastindex=$(ls $kernel_folder_fio -l | grep "^d" | wc -l)
cnt=1
for file in $kernel_files_fio; do
  if [[ $cnt == $(($kernel_lastindex)) ]]; then
    kernel_lastfile_fio=$kernel_folder_fio"/"$file"/*"
     echo $kernel_lastfile_fio
  fi
  cnt=$((cnt + 1))
done



cx5_folder_fio="/home/jane/test-rocksdb/rocksdb-results/cx5"
cx5_files_fio=$(ls $cx5_folder_fio)
cx5_lastindex=$(ls $cx5_folder_fio -l | grep "^d" | wc -l)
cnt=1
for file in $cx5_files_fio; do
  if [[ $cnt == $(($cx5_lastindex)) ]]; then
    cx5_lastfile_fio=$cx5_folder_fio"/"$file"/*"
    #  echo $cx5_lastfile_fio
  fi
  cnt=$((cnt + 1))
done


hypath_folder_fio="/home/jane/test-rocksdb/rocksdb-results/hypath"
hypath_files_fio=$(ls $hypath_folder_fio)
hypath_lastindex=$(ls $hypath_folder_fio -l | grep "^d" | wc -l)
cnt=1
for file in $hypath_files_fio; do
  if [[ $cnt == $(($hypath_lastindex)) ]]; then
    hypath_lastfile_fio=$hypath_folder_fio"/"$file"/*"
    #  echo $hypath_lastfile_fio
  fi
  cnt=$((cnt + 1))
done



# nowdate=$(date "+%Y%m%d%H%M%S")
# nowdate='20221109163848-single'
nowdate='20221213135525'

fio_dir="./fio_res/"$nowdate
plt_dir="./plot_res/"$nowdate

mkdir $fio_dir
mkdir $plt_dir


mkdir $fio_dir"/kernel"
cp -rf $kernel_lastfile_fio $fio_dir"/kernel"

mkdir $fio_dir"/cx5"
cp -rf $cx5_lastfile_fio $fio_dir"/cx5"

mkdir $fio_dir"/hypath"
cp -rf $hypath_lastfile_fio $fio_dir"/hypath"


# sleep 1
# python3 /home/jinzhen/backup/dragonball/plot_through/io_plot.py $fio_dir $fio_dir $plt_dir
# python3 ./plot_type_abs.py $fio_dir $plt_dir
python3 ./plot_mul.py $fio_dir $plt_dir