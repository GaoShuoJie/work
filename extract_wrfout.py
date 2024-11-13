import xarray as xr

# 设置文件路径和输出文件名
wrfpath = "~/gsj/work/wrfout/"
wrfoutname = "wrfout_d01_2008-09-09_00:00:00"
varnames = ['T2']  # 在这里添加你要提取的变量名
output_filename = f"./ext_{wrfoutname}.nc"  # 输出文件名



# 打开 WRF 输出数据集
ds = xr.open_dataset(wrfpath + wrfoutname,engine='netcdf4')

# 提取变量并合并到新的数据集
extracted_vars = {}
for var in varnames:
    if var in ds:
        extracted_vars[var] = ds[var]
    else:
        print(f"Variable '{var}' not found in the dataset.")

# 创建新的数据集
new_ds = xr.Dataset(extracted_vars)

# 保存到 NetCDF 文件
new_ds.to_netcdf(output_filename)
print(f"Extracted variables saved to {output_filename}.")
